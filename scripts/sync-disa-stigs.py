#!/usr/bin/env python3
"""Sync DISA STIG/SRG document entries into registry/control/mil/disa.json.

Source of truth is the quarterly SRG/STIG Library Compilation published by DISA at
dl.dod.cyber.mil -- the same artifact every other STIG consumer ingests. We do NOT
scrape public.cyber.mil: that catalogue is a Salesforce Experience Cloud app whose
data comes from an undocumented /webruntime/api endpoint, which would break silently.

The compilation is ~370 MB, but the ZIP central directory (the file listing) sits at
the END of the archive. Two HTTP range requests are enough to read the manifest
without downloading the payload -- roughly 150 KB instead of 370 MB.

Naming inside the compilation:
    U_<Product>_V<major>R<minor>_{STIG,SRG}.zip     e.g. U_Active_Directory_Domain_V3R7_STIG.zip
    U_<Product>_Y<yy>M<mm>_{STIG,SRG}.zip           e.g. U_Apache_Server_2-4_Unix_Y26M07_STIG.zip

Both schemes are live; DISA is migrating from V<major>R<minor> to date-based Y<yy>M<mm>.

Usage:
    python3 scripts/sync-disa-stigs.py              # discover latest compilation, update registry
    python3 scripts/sync-disa-stigs.py --dry-run    # report what would change
    python3 scripts/sync-disa-stigs.py --compilation U_SRG-STIG_Library_July_2026.zip
"""
import argparse, json, re, struct, sys, urllib.request
from datetime import date, datetime, timezone
from pathlib import Path

BASE = "https://dl.dod.cyber.mil/wp-content/uploads/stigs/zip"
LIBRARY_PAGE = "https://public.cyber.mil/stigs/downloads/"
REGISTRY = Path("registry/control/mil/disa.json")
UA = {"User-Agent": "Mozilla/5.0 (SecID registry sync; +https://secid.cloudsecurityalliance.org)"}
MONTHS = ["January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]

# Programme-level nodes are hand-written and must survive a sync.
PROGRAMME_PATTERNS = {"(?i)^stig$", "(?i)^srg$", "(?i)^cci$"}
GENERATED_KEY = "_generated_from"

DOC_RE = re.compile(
    r'^U_(?P<prod>.+?)_(?:V(?P<maj>\d+)R(?P<min>\d+)|Y(?P<yy>\d{2})M(?P<mm>\d{2}))_(?P<kind>STIG|SRG)\.zip$')


def _get(url, rng=None):
    req = urllib.request.Request(url, headers=dict(UA))
    if rng:
        req.add_header("Range", f"bytes={rng[0]}-{rng[1]}")
    return urllib.request.urlopen(req, timeout=120)


def head_size(url):
    """Return Content-Length, or None if the URL is absent."""
    try:
        req = urllib.request.Request(url, headers=dict(UA), method="HEAD")
        with urllib.request.urlopen(req, timeout=60) as r:
            return int(r.headers.get("Content-Length") or 0) or None
    except Exception:
        return None


def discover_compilation(today=None):
    """Find the most recent published compilation, newest first."""
    today = today or date.today()
    # DISA publishes on fixed quarters: January, April, July, October. Do NOT step back
    # three months from the current month -- that lands on non-release months.
    quarters = [1, 4, 7, 10]
    candidates = []
    y = today.year
    # most recent release month at or before today
    m = max((q for q in quarters if q <= today.month), default=None)
    if m is None:
        y, m = y - 1, 10
    for _ in range(8):                       # ~2 years back
        candidates.append(f"U_SRG-STIG_Library_{MONTHS[m - 1]}_{y}.zip")
        idx = quarters.index(m) - 1
        if idx < 0:
            idx, y = 3, y - 1
        m = quarters[idx]
    for name in candidates:
        size = head_size(f"{BASE}/{name}")
        if size:
            return name, size
    raise SystemExit("Could not locate any SRG/STIG Library Compilation; check naming or connectivity.")


def read_manifest(name, size):
    """Read the ZIP central directory with two range requests."""
    url = f"{BASE}/{name}"
    tail_len = min(131072, size)
    tail = _get(url, (size - tail_len, size - 1)).read()
    i = tail.rfind(b"PK\x05\x06")
    if i < 0:
        raise SystemExit("No end-of-central-directory record found (ZIP64 not handled).")
    cd_size, = struct.unpack_from("<I", tail, i + 12)
    cd_off, = struct.unpack_from("<I", tail, i + 16)
    if cd_off == 0xFFFFFFFF:
        raise SystemExit("ZIP64 central directory; extend the parser.")
    cd = _get(url, (cd_off, cd_off + cd_size - 1)).read()
    names, off = [], 0
    while off < len(cd) - 4 and cd[off:off + 4] == b"PK\x01\x02":
        nlen, = struct.unpack_from("<H", cd, off + 28)
        elen, = struct.unpack_from("<H", cd, off + 30)
        clen, = struct.unpack_from("<H", cd, off + 32)
        names.append(cd[off + 46:off + 46 + nlen].decode("utf-8", "replace"))
        off += 46 + nlen + elen + clen
    return names


def parse(names):
    docs, skipped = [], []
    for n in names:
        m = DOC_RE.match(n)
        if not m:
            if n.endswith(".zip"):
                skipped.append(n)
            continue
        product = m["prod"].replace("_", " ")
        slug = re.sub(r"[^a-z0-9]+", "-", m["prod"].lower()).strip("-")
        version = f"V{m['maj']}R{m['min']}" if m["maj"] else f"Y{m['yy']}M{m['mm']}"
        docs.append({"slug": slug, "product": product, "version": version,
                     "kind": m["kind"], "file": n})
    docs.sort(key=lambda d: d["slug"])
    return docs, skipped


def rule_ids(data_repo, slug, version):
    """V-IDs for one document release, read from the data repository.

    The registry's job is disambiguation, and V-IDs are the case that needs it: the
    pattern ^V-\\d+$ is identical across every STIG, so without an enumerated set a
    bare search for V-257505 would match all 174 nodes and fabricate 173 wrong answers
    -- the failure the pattern-breadth gate exists to prevent. known_values closes the
    set so only the owning document matches.
    """
    f = Path(data_repo) / "data" / "control" / "mil" / "disa" / slug / version / "stig.json"
    if not f.is_file():
        return None
    try:
        return json.loads(f.read_text()).get("rule_index") or None
    except Exception:
        return None


def build_node(d, compilation, checked, data_repo=None):
    label = f"{d['product']} {d['kind']}"
    node = {
        "patterns": [f"(?i)^{d['slug']}$"],
        "description": f"{label} — DISA {'Security Technical Implementation Guide' if d['kind']=='STIG' else 'Security Requirements Guide'}",
        "weight": 100,
        "data": {
            "official_name": label,
            "kind": d["kind"],
            "notes": (f"Current release {d['version']}. Published as XCCDF XML inside {d['file']}. "
                      f"The per-document download URL is pinned to the current revision and 404s once "
                      f"superseded; the quarterly compilation is the stable citation. "
                      f"V-IDs for this release are enumerated below and resolve to structured records in "
                      f"SecID-Data-disa.mil; rule IDs and STIG IDs are recorded there but are not subpaths."),
            "urls": [
                {"type": "bulk_data", "url": f"{BASE}/{d['file']}", "format": "zip",
                 "parsability": "structured", "note": "XCCDF XML inside a ZIP. Revision-pinned URL.",
                 "checked": checked},
                {"type": "website", "url": LIBRARY_PAGE, "note": "Always-current document library."},
            ],
            "versions_available": [
                {"version": d["version"], "status": "current",
                 "note": f"As published in {compilation}."}
            ],
            "examples": [],
            GENERATED_KEY: compilation,
        },
    }
    vids = rule_ids(data_repo, d["slug"], d["version"]) if data_repo else None
    if vids:
        node["children"] = [{
            "patterns": ["^V-\\d+$"],
            "description": f"A single requirement within the {d['product']} {d['kind']}, by DISA Vuln ID.",
            "weight": 100,
            # ^V-\d+$ is identical across all 174 documents, so in UNSCOPED search this node
            # would match every one of them and fabricate 173 wrong answers for any V-token.
            # known_values below carries the real set and should close the pattern, but the
            # resolver does not yet honour it (SecID issue #190). open_pattern keeps these
            # nodes out of unscoped search while namespace-scoped resolution keeps working.
            # Remove this flag once known_values is enforced -- the data is already correct.
            "open_pattern": True,
            "data": {
                "note": ("DISA publishes no per-rule permalink; rules exist only inside the XCCDF. "
                         "Structured records are served from SecID-Data-disa.mil. Each rule also carries a "
                         "rule ID (SV-...r..._rule, revision-bearing), a per-benchmark STIG ID, and one or "
                         "more CCI references."),
                "known_values": vids,
                "urls": [{
                    "type": "bulk_data",
                    "url": (f"https://raw.githubusercontent.com/CloudSecurityAlliance/SecID-Data-disa.mil/main/"
                            f"data/control/mil/disa/{d['slug']}/{d['version']}/rules/{{id}}.json"),
                    "format": "json",
                    "parsability": "structured",
                    "note": "Structured rule record.",
                }],
                "examples": [{"input": vids[0], "note": "First requirement in this document."}],
            },
        }]
    return node


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--compilation")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--data-repo", default=str(Path.home() / "GitHub/CloudSecurityAlliance/SecID-Data-disa.mil"),
                    help="Path to SecID-Data-disa.mil, used to enumerate rule identifiers.")
    args = ap.parse_args()

    if args.compilation:
        name = args.compilation
        size = head_size(f"{BASE}/{name}")
        if not size:
            raise SystemExit(f"{name} not found at {BASE}")
    else:
        name, size = discover_compilation()
    print(f"compilation: {name} ({size:,} bytes)")

    names = read_manifest(name, size)
    docs, skipped = parse(names)
    print(f"manifest: {len(names)} entries -> {len(docs)} STIG/SRG documents "
          f"({sum(1 for d in docs if d['kind']=='STIG')} STIG, {sum(1 for d in docs if d['kind']=='SRG')} SRG)")
    if skipped:
        print(f"skipped {len(skipped)} non-STIG/SRG archives: {', '.join(skipped)}")

    dupes = {d["slug"] for d in docs if sum(1 for x in docs if x["slug"] == d["slug"]) > 1}
    if dupes:
        raise SystemExit(f"slug collisions, refusing to write: {sorted(dupes)}")

    # patterns[0] must be a clean literal, or SecID-Service derives the canonical name by
    # slugifying the description instead -- returning an unusable SecID (issue #181).
    unsafe = [d["slug"] for d in docs if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", d["slug"])]
    if unsafe:
        raise SystemExit(f"slugs are not clean literals, refusing to write: {unsafe[:10]}")

    doc = json.loads(REGISTRY.read_text())
    kept = [n for n in doc["match_nodes"] if n["patterns"][0] in PROGRAMME_PATTERNS]
    if len(kept) != len(PROGRAMME_PATTERNS):
        raise SystemExit("programme nodes (stig/srg/cci) missing; refusing to write.")
    checked = datetime.now(timezone.utc).date().isoformat()
    generated = [build_node(d, name, checked, args.data_repo) for d in docs]

    before = len(doc["match_nodes"])
    doc["match_nodes"] = kept + generated
    doc["status_notes"] = (
        f"Programme entries plus {len(generated)} STIG/SRG documents generated from {name} "
        f"by scripts/sync-disa-stigs.py. Rule-level identifiers (V-IDs, rule IDs, STIG IDs) "
        f"are not yet enumerated - see issue #59.")

    print(f"match_nodes: {before} -> {len(doc['match_nodes'])} ({len(kept)} programme + {len(generated)} documents)")
    if args.dry_run:
        print("dry run; nothing written.")
        return
    REGISTRY.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
    print(f"wrote {REGISTRY}")


if __name__ == "__main__":
    main()
