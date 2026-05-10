#!/usr/bin/env python3
"""Audit the known-broken overlay against fresh upstream CNAsList.json.

Walks working-data/cna/known-broken.json (schema v2.0) and classifies each
entry into one of four buckets by comparing its current_value to whatever
upstream CNAsList.json currently has at the same field_path:

  1. still_present  — upstream still holds the broken value at field_path.
                      No change; annotation is still valid.

  2. replaced       — field_path now resolves to a different value.
                      Upstream changed the URL/email. Re-validate manually.

  3. disappeared    — field_path no longer resolves at all (CNA removed it,
                      array length shrank, etc.). Orphan; candidate for
                      removal from the overlay.

  4. partial        — entry has multiple field_paths and the buckets differ
                      (e.g., still_present at one path, disappeared at another).

Stale is reported orthogonally on every entry: any entry whose
evidence.last_verified is older than --stale-days (default 90) is flagged
regardless of bucket.

REPORT-ONLY — does not auto-reprobe URLs/emails. Reprobing is a separate
manual step using Playwright / QuickEmailVerification.

Usage:
  scripts/audit-known-broken.py [--cnas-list PATH]
                                [--stale-days N]
                                [--json]

Exit code: 0 if every entry is still_present-and-not-stale; 1 otherwise
(the script ran fine, but the overlay needs human attention).
"""

import argparse
import json
import re
import sys
import urllib.request
from datetime import date
from pathlib import Path

OVERLAY = Path("working-data/cna/known-broken.json")
CNASLIST_URL = (
    "https://raw.githubusercontent.com/CVEProject/cve-website/"
    "main/src/assets/data/CNAsList.json"
)

# JMESPath subset we support in field_paths:
#   [?shortName=='X'].part1.part2[N].part3
# Anything else is rejected with a clear error.
PATH_RE = re.compile(r"^\[\?shortName=='([^']+)'\](.*)$")
SEGMENT_RE = re.compile(r"\.([A-Za-z_][A-Za-z0-9_]*)|\[(\d+)\]")


def resolve_field_path(cnaslist: list, field_path: str):
    """Evaluate our JMESPath subset against the CNAsList.json root array.

    Returns (status, value) where status is one of:
      'found'        — resolved to a non-None scalar
      'disappeared'  — path walks off the end (missing field, array out of range)
      'cna_missing'  — the [?shortName=='X'] filter matched no CNA
      'error'        — path syntax we don't support
    """
    m = PATH_RE.match(field_path)
    if not m:
        return ("error", f"unsupported field_path syntax: {field_path!r}")

    short_name, rest = m.group(1), m.group(2)

    # Find the CNA
    cna = next((c for c in cnaslist if c.get("shortName") == short_name), None)
    if cna is None:
        return ("cna_missing", None)

    # Walk the rest
    current = cna
    pos = 0
    while pos < len(rest):
        seg = SEGMENT_RE.match(rest, pos)
        if not seg:
            return ("error", f"unparseable segment at offset {pos} of {rest!r}")
        key, idx = seg.group(1), seg.group(2)
        if key is not None:
            if not isinstance(current, dict) or key not in current:
                return ("disappeared", None)
            current = current[key]
        else:
            i = int(idx)
            if not isinstance(current, list) or i >= len(current):
                return ("disappeared", None)
            current = current[i]
        pos = seg.end()

    return ("found", current)


def classify_path(cnaslist, field_path, current_value):
    """Returns (bucket, actual_value).

    bucket ∈ {still_present, replaced, disappeared, error}.
    """
    status, value = resolve_field_path(cnaslist, field_path)
    if status == "error":
        return ("error", value)
    if status in ("disappeared", "cna_missing"):
        return ("disappeared", None)
    # status == 'found'
    if str(value).strip().lower() == str(current_value).strip().lower():
        return ("still_present", value)
    return ("replaced", value)


def days_since(date_str):
    try:
        d = date.fromisoformat(date_str)
    except (ValueError, TypeError):
        return None
    return (date.today() - d).days


def audit_entry(entry, cnaslist, stale_days):
    last_verified = entry["evidence"]["last_verified"]
    age = days_since(last_verified)
    is_stale = age is not None and age > stale_days

    path_results = []
    for path in entry["field_paths"]:
        bucket, actual = classify_path(cnaslist, path, entry["current_value"])
        path_results.append(
            {"field_path": path, "bucket": bucket, "actual_value": actual}
        )

    # Aggregate overall bucket
    buckets = {p["bucket"] for p in path_results}
    if buckets == {"still_present"}:
        overall = "still_present"
    elif "error" in buckets:
        overall = "error"
    elif "replaced" in buckets:
        overall = "replaced"
    elif buckets == {"disappeared"}:
        overall = "disappeared"
    else:
        # Mixed (e.g., still_present + disappeared)
        overall = "partial"

    return {
        "cna_short_name": entry["cna_short_name"],
        "current_value": entry["current_value"],
        "failure": entry["failure"],
        "upstream_issue": entry.get("upstream_issue"),
        "last_verified": last_verified,
        "age_days": age,
        "stale": is_stale,
        "overall": overall,
        "paths": path_results,
    }


def load_cnaslist(local_path):
    if local_path:
        return json.loads(Path(local_path).read_text())
    print(f"Fetching {CNASLIST_URL} ...", file=sys.stderr)
    with urllib.request.urlopen(CNASLIST_URL) as r:
        return json.loads(r.read())


BUCKET_ORDER = ["still_present", "replaced", "disappeared", "partial", "error"]


def render_text(report):
    out = []
    out.append("=" * 72)
    out.append(f"Audit of known-broken overlay against current CNAsList.json")
    out.append(f"Audited at: {report['audited_at']}")
    out.append(f"Stale threshold: {report['stale_threshold_days']} days")
    out.append("=" * 72)

    for category, results in [
        ("URLs", report["url_results"]),
        ("Emails", report["email_results"]),
    ]:
        out.append(f"\n## {category}: {len(results)} entries\n")

        # Summary counts
        counts = {b: 0 for b in BUCKET_ORDER}
        for r in results:
            counts[r["overall"]] += 1
        stale_count = sum(1 for r in results if r["stale"])
        summary = ", ".join(f"{b}={counts[b]}" for b in BUCKET_ORDER if counts[b])
        out.append(f"  Summary: {summary or 'none'} | stale={stale_count}")
        out.append("")

        # Per-bucket detail
        for status in BUCKET_ORDER:
            items = [r for r in results if r["overall"] == status]
            if not items:
                continue
            out.append(f"### {status} ({len(items)})")
            for r in items:
                stale_mark = " [STALE]" if r["stale"] else ""
                age = f"{r['age_days']}d ago" if r["age_days"] is not None else "?"
                out.append(
                    f"  - [{r['cna_short_name']}]{stale_mark} "
                    f"{r['current_value']} (verified {age})"
                )
                if status != "still_present":
                    for p in r["paths"]:
                        if p["bucket"] != "still_present":
                            actual = p["actual_value"]
                            if actual is None:
                                out.append(f"      {p['field_path']}: {p['bucket']}")
                            else:
                                out.append(
                                    f"      {p['field_path']}: "
                                    f"{p['bucket']} -> {actual!r}"
                                )
            out.append("")

        # Stale-but-still-present (separate callout — easy to miss otherwise)
        stale_present = [
            r for r in results if r["stale"] and r["overall"] == "still_present"
        ]
        if stale_present:
            out.append(
                f"### stale + still_present ({len(stale_present)}) — recommend "
                f"manual reverification"
            )
            for r in stale_present:
                out.append(
                    f"  - [{r['cna_short_name']}] {r['current_value']} "
                    f"(verified {r['age_days']}d ago)"
                )
            out.append("")

    return "\n".join(out)


def needs_attention(report):
    """Return True if any entry is not still_present-and-not-stale."""
    for results in (report["url_results"], report["email_results"]):
        for r in results:
            if r["overall"] != "still_present" or r["stale"]:
                return True
    return False


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument(
        "--cnas-list",
        help="Local CNAsList.json path (default: fetch from CVEProject main)",
    )
    ap.add_argument(
        "--stale-days",
        type=int,
        default=90,
        help="Days threshold for marking entries stale (default: 90)",
    )
    ap.add_argument(
        "--json", action="store_true", help="Emit machine-readable JSON report"
    )
    args = ap.parse_args()

    overlay = json.loads(OVERLAY.read_text())
    if overlay.get("schema_version") != "2.0":
        print(
            f"ERROR: overlay schema_version is not '2.0' "
            f"(got {overlay.get('schema_version')!r})",
            file=sys.stderr,
        )
        sys.exit(2)

    cnaslist = load_cnaslist(args.cnas_list)
    if not isinstance(cnaslist, list):
        print(
            f"ERROR: CNAsList.json root is not an array (got {type(cnaslist).__name__})",
            file=sys.stderr,
        )
        sys.exit(2)
    print(f"CNAsList.json: {len(cnaslist)} CNAs", file=sys.stderr)

    report = {
        "audited_at": date.today().isoformat(),
        "stale_threshold_days": args.stale_days,
        "url_results": [
            audit_entry(e, cnaslist, args.stale_days) for e in overlay["broken_urls"]
        ],
        "email_results": [
            audit_entry(e, cnaslist, args.stale_days) for e in overlay["broken_emails"]
        ],
    }

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(render_text(report))

    sys.exit(1 if needs_attention(report) else 0)


if __name__ == "__main__":
    main()
