#!/usr/bin/env python3
"""Apply known-broken validation overlay to disclosure registry entries.

Reads:  working-data/cna/known-broken.json
Walks:  registry/disclosure/**/*.json
Writes: same files with _broken metadata injected on matching URL and email
        fields.

For each URL or email in the validation overlay, finds matching occurrences in
the disclosure entries and annotates them with:

  - _broken: true
  - _broken_verified: <date the failure was verified>
  - _broken_failure: <classification: hard_404, dns_failure, etc.>
  - _broken_note: <human-readable explanation>
  - _broken_source: "CVEProject/cve-website#3937" (or similar issue ref)

Run:    python3 scripts/apply-known-broken.py [--dry-run]

Idempotent — running multiple times produces the same result. Removing an
entry from known-broken.json and re-running will strip the _broken_* fields
from any URL/email no longer in the broken list.
"""

import json
import sys
from pathlib import Path

DRY_RUN = "--dry-run" in sys.argv

OVERLAY_FILE = Path("working-data/cna/known-broken.json")
REGISTRY_DIR = Path("registry/disclosure")

BROKEN_KEYS = ("_broken", "_broken_verified", "_broken_failure", "_broken_note", "_broken_source")


def load_overlay():
    if not OVERLAY_FILE.exists():
        print(f"ERROR: {OVERLAY_FILE} not found", file=sys.stderr)
        sys.exit(1)
    data = json.loads(OVERLAY_FILE.read_text())

    # Normalize: lowercased URL/email -> entry. Preserve original case in the
    # entry itself (we match case-insensitively but display the original).
    by_url = {}
    by_email = {}

    for u in data.get("broken_urls") or []:
        by_url[u["url"].strip().lower()] = u
    for e in data.get("broken_emails") or []:
        by_email[e["email"].strip().lower()] = e

    issues = data.get("upstream_issues") or []
    issue_ref = ", ".join(i["issue"] for i in issues) if issues else ""

    return by_url, by_email, issue_ref


def strip_broken(obj: dict) -> bool:
    """Remove all _broken_* keys from a dict. Return True if any were removed."""
    removed = False
    for k in BROKEN_KEYS:
        if k in obj:
            del obj[k]
            removed = True
    return removed


def annotate_broken(obj: dict, entry: dict, issue_ref: str) -> None:
    """Inject _broken metadata into obj based on an overlay entry."""
    obj["_broken"] = True
    obj["_broken_verified"] = entry["verified"]
    obj["_broken_failure"] = entry["failure"]
    obj["_broken_note"] = entry["note"]
    if issue_ref:
        obj["_broken_source"] = issue_ref


def process_url_object(url_obj: dict, by_url: dict, issue_ref: str) -> bool:
    """If url_obj['url'] matches a broken entry, annotate. Otherwise strip any
    stale annotations. Return True if anything changed."""
    if not isinstance(url_obj, dict):
        return False
    url = url_obj.get("url")
    if not isinstance(url, str):
        return strip_broken(url_obj)
    key = url.strip().lower()
    entry = by_url.get(key)
    if entry:
        # Snapshot before to detect change
        before = {k: url_obj.get(k) for k in BROKEN_KEYS}
        annotate_broken(url_obj, entry, issue_ref)
        return any(url_obj.get(k) != before[k] for k in BROKEN_KEYS)
    else:
        return strip_broken(url_obj)


def process_contact_object(contact: dict, by_email: dict, issue_ref: str) -> bool:
    """If contact is an email matching a broken entry, annotate. Otherwise
    strip stale annotations."""
    if not isinstance(contact, dict):
        return False
    if contact.get("type") != "email":
        return strip_broken(contact)
    val = contact.get("value")
    if not isinstance(val, str):
        return strip_broken(contact)
    key = val.strip().lower()
    entry = by_email.get(key)
    if entry:
        before = {k: contact.get(k) for k in BROKEN_KEYS}
        annotate_broken(contact, entry, issue_ref)
        return any(contact.get(k) != before[k] for k in BROKEN_KEYS)
    else:
        return strip_broken(contact)


def process_node_data(data: dict, by_url, by_email, issue_ref) -> bool:
    """Walk a match_node's data block, annotating URLs and contacts."""
    changed = False

    # data.urls[]
    for url_obj in data.get("urls") or []:
        if process_url_object(url_obj, by_url, issue_ref):
            changed = True

    # data.contacts[] (emails only)
    for contact in data.get("contacts") or []:
        if process_contact_object(contact, by_email, issue_ref):
            changed = True

    # data.disclosure_policy {url, checked}
    dp = data.get("disclosure_policy")
    if isinstance(dp, dict):
        if process_url_object(dp, by_url, issue_ref):
            changed = True

    # data.security_txt — sometimes a string, sometimes {url, ...}
    st = data.get("security_txt")
    if isinstance(st, dict):
        if process_url_object(st, by_url, issue_ref):
            changed = True

    return changed


def process_file(path: Path, by_url, by_email, issue_ref) -> tuple[bool, dict]:
    """Returns (modified, change_summary)."""
    data = json.loads(path.read_text())
    summary = {"urls_marked": 0, "emails_marked": 0, "stale_cleared": 0}

    # Top-level urls (mostly just the website URL — rarely flagged but check)
    for url_obj in data.get("urls") or []:
        before_broken = url_obj.get("_broken")
        if process_url_object(url_obj, by_url, issue_ref):
            if url_obj.get("_broken"):
                summary["urls_marked"] += 1
            elif before_broken:
                summary["stale_cleared"] += 1

    # match_nodes[].data
    file_modified = False
    for node in data.get("match_nodes") or []:
        node_data = node.get("data") or {}

        # Track per-field
        for u in node_data.get("urls") or []:
            before = u.get("_broken")
            if process_url_object(u, by_url, issue_ref):
                file_modified = True
                if u.get("_broken"):
                    summary["urls_marked"] += 1
                elif before:
                    summary["stale_cleared"] += 1

        for c in node_data.get("contacts") or []:
            before = c.get("_broken")
            if process_contact_object(c, by_email, issue_ref):
                file_modified = True
                if c.get("_broken"):
                    summary["emails_marked"] += 1
                elif before:
                    summary["stale_cleared"] += 1

        dp = node_data.get("disclosure_policy")
        if isinstance(dp, dict):
            before = dp.get("_broken")
            if process_url_object(dp, by_url, issue_ref):
                file_modified = True
                if dp.get("_broken"):
                    summary["urls_marked"] += 1
                elif before:
                    summary["stale_cleared"] += 1

        st = node_data.get("security_txt")
        if isinstance(st, dict):
            before = st.get("_broken")
            if process_url_object(st, by_url, issue_ref):
                file_modified = True
                if st.get("_broken"):
                    summary["urls_marked"] += 1
                elif before:
                    summary["stale_cleared"] += 1

    if file_modified and not DRY_RUN:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")

    return file_modified, summary


def main():
    by_url, by_email, issue_ref = load_overlay()
    print(f"Overlay loaded: {len(by_url)} broken URLs, {len(by_email)} broken emails")
    print(f"Mode: {'DRY RUN (no writes)' if DRY_RUN else 'LIVE'}")
    print()

    files_processed = 0
    files_modified = 0
    total_urls = 0
    total_emails = 0
    total_stale_cleared = 0
    modified_files = []

    for path in sorted(REGISTRY_DIR.rglob("*.json")):
        if "/_" in str(path) or path.name.startswith("_"):
            continue
        files_processed += 1
        modified, summary = process_file(path, by_url, by_email, issue_ref)
        if modified:
            files_modified += 1
            modified_files.append((path, summary))
            total_urls += summary["urls_marked"]
            total_emails += summary["emails_marked"]
            total_stale_cleared += summary["stale_cleared"]

    print(f"Files processed: {files_processed}")
    print(f"Files modified:  {files_modified}")
    print(f"  URL annotations applied:   {total_urls}")
    print(f"  Email annotations applied: {total_emails}")
    print(f"  Stale annotations cleared: {total_stale_cleared}")
    print()
    print("Modified files:")
    for path, summary in modified_files:
        bits = []
        if summary["urls_marked"]:
            bits.append(f"{summary['urls_marked']} urls")
        if summary["emails_marked"]:
            bits.append(f"{summary['emails_marked']} emails")
        if summary["stale_cleared"]:
            bits.append(f"cleared {summary['stale_cleared']}")
        print(f"  {path}  ({', '.join(bits)})")


if __name__ == "__main__":
    main()
