#!/usr/bin/env python3
"""Generate CWE membership from pinned MITRE catalogs, never from guessed ID ranges.

Offline: python3 scripts/sync-cwe.py --check
Verify the manifest against downloaded official ZIPs:
  python3 scripts/sync-cwe.py --archive-dir /path/to/archives --check
Files must be named cwec_vVERSION.xml.zip. Hashes are pinned in data/cwe-releases.json.
To update, review new archive hashes and extracted IDs in that manifest first.
Without --check this updates only CWE children and version metadata in the registry.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "scripts/data/cwe-releases.json"
REGISTRY = ROOT / "registry/weakness/org/mitre.json"
KINDS = {"Weaknesses": "weakness", "Categories": "category", "Groupings": "category", "Views": "view"}


def verify_archives(manifest, directory):
    for release in manifest["releases"]:
        version = release["version"]
        path = directory / f"cwec_v{version}.xml.zip"
        if hashlib.sha256(path.read_bytes()).hexdigest() != release["sha256"]:
            raise ValueError(f"{path}: SHA-256 differs from reviewed archive")
        with zipfile.ZipFile(path) as archive:
            names = [n for n in archive.namelist() if n.endswith(".xml")]
            if len(names) != 1:
                raise ValueError(f"{path}: expected exactly one XML catalog")
            root = ET.fromstring(archive.read(names[0]))
        groups = {g.tag.rsplit("}", 1)[-1]: g for g in root}
        ids = {k: sorted(int(e.attrib["ID"]) for e in groups[k]) for k in KINDS if k in groups}
        schema = root.attrib["{http://www.w3.org/2001/XMLSchema-instance}schemaLocation"].split("_v")[1].removesuffix(".xsd")
        if (root.attrib["Version"], root.attrib["Date"], schema, ids) != (
            version, release["release_date"], release["schema"], release["ids"]
        ):
            raise ValueError(f"{path}: catalog metadata/membership differs from manifest")


def pattern(ids):
    return r"(?i)^CWE-(?:" + "|".join(map(str, sorted(ids))) + ")$"


def examples(ids, url, version=None):
    # Include common user queries and representative weaknesses, groupings and views.
    chosen = sorted(set(ids) & {19, 79, 89, 1000, 1425, 1427, 1448}) or [min(ids)]
    return [{"input": f"{prefix}-{n}", "url": url.replace("{num}", str(n)),
             **({"version": version} if version else {})}
            for n in chosen for prefix in ("CWE", "cwe")]


def live_node(ids, description, url, weight, content_type):
    return {"patterns": [pattern(ids)], "description": description, "weight": weight,
            "data": {"url": url, "content_type": content_type,
                     "parsability": "scraped" if content_type == "text/html" else "structured",
                     "auth": "none", "variables": {"num": {"extract": r"(?i)^CWE-(\d+)$"}},
                     "examples": examples(ids, url)}}


def generated(manifest):
    releases = manifest["releases"]
    if not releases or releases[0]["version"] != "5.0":
        raise ValueError("Review current-release selection before changing the release train")
    for r in releases:
        flat = [i for ids in r["ids"].values() for i in ids]
        if set(r["ids"]) - KINDS.keys() or len(flat) != len(set(flat)) or not flat:
            raise ValueError(f"Invalid or duplicated entry kinds/IDs in {r['version']}")
    current = releases[0]
    all_ids = sorted(i for ids in current["ids"].values() for i in ids)
    children = [live_node(all_ids, "CWE current HTML definition", "https://cwe.mitre.org/data/definitions/{num}.html", 100, "text/html")]
    # The API reports ContentVersion 4.21 (verified 2026-11-18); it still calls
    # Groupings 'Categories'. Do not label this moving endpoint as a 5.0 snapshot.
    api_release = next(r for r in releases if r["version"] == "4.21")
    for kind, ids in api_release["ids"].items():
        children.append(live_node(ids, f"CWE live {KINDS[kind]} API", f"https://cwe-api.mitre.org/api/v1/cwe/{KINDS[kind]}/{{num}}", 50, "application/json"))
    children.append(live_node(all_ids, "CWE live entry-type lookup", "https://cwe-api.mitre.org/api/v1/cwe/{num}", 40, "application/json"))
    versions = []
    for release in releases:
        version = release["version"]
        counts = ", ".join(f"{len(ids)} {kind.lower()}" for kind, ids in release["ids"].items())
        note = f"{counts}. XML schema {release['schema']}. Exact-release item references select entries from the official XML ZIP."
        versions.append({"version": version, "release_date": release["release_date"], "status": "current" if version == "5.0" else "superseded", "note": note})
        branches = []
        for kind, ids in release["ids"].items():
            singular = {"Weaknesses": "Weakness", "Categories": "Category", "Groupings": "Grouping", "Views": "View"}[kind]
            branches.append({"patterns": [pattern(ids)], "description": f"CWE {version} {kind.lower()}", "weight": 100,
                "data": {"url": release["url"], "content_type": "application/zip", "parsability": "structured", "auth": "none",
                         "schema": f"secid:reference/mitre.org/cwe-schema#{release['schema']}",
                         "parsing_instructions": f"Unzip the XML catalog (release {version}); select /Weakness_Catalog/{kind}/{singular} with @ID equal to the numeric suffix of the requested CWE identifier. Use the catalog's default XML namespace. This is a full catalog, not a per-item file.",
                         "examples": examples(ids, release["url"], version)}})
        children.append({"patterns": ["^" + re.escape(version) + "$"], "description": f"CWE {version}", "weight": 100,
                         "data": {"type": "version", "official_name": f"Common Weakness Enumeration {version}", "note": note,
                                  "urls": [{"type": "bulk_data", "url": release["url"], "format": "xml", "note": "ZIP containing the complete release XML catalog"}]},
                         "children": branches})
    return versions, children


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--archive-dir", type=Path)
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text())
    if args.archive_dir:
        verify_archives(manifest, args.archive_dir)
    document = json.loads(REGISTRY.read_text())
    source = document["match_nodes"][0]
    versions, children = generated(manifest)
    if args.check:
        if source["data"]["versions_available"] != versions or source["children"] != children:
            raise SystemExit("CWE registry differs from reviewed manifest; run scripts/sync-cwe.py")
    else:
        source["data"]["versions_available"], source["children"] = versions, children
        REGISTRY.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n")
    print(f"CWE: {len(versions)} release catalogs verified")


if __name__ == "__main__":
    main()
