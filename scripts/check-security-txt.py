#!/usr/bin/env python3
"""Check security.txt for all disclosure namespace domains.

Fetches https://{domain}/.well-known/security.txt for each domain.
Records results and updates disclosure registry files with security_txt field.

Run: python3 scripts/check-security-txt.py [--dry-run] [--update]
  --dry-run: check but don't modify files
  --update: write security_txt field to disclosure JSON files
  (default: check and report only)

Output: working-data/security-txt-results.json
"""

import asyncio
import json
import glob
import sys
from datetime import datetime, timezone
from pathlib import Path

UPDATE = "--update" in sys.argv
DRY_RUN = "--dry-run" in sys.argv

REGISTRY_DIR = Path("registry/disclosure")
RESULTS_FILE = Path("working-data/security-txt-results.json")
TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")

# Concurrency limit to be polite
MAX_CONCURRENT = 20
TIMEOUT = 10  # seconds per request


async def check_domain(session, domain: str) -> dict:
    """Check a single domain for security.txt."""
    url = f"https://{domain}/.well-known/security.txt"
    try:
        async with session.get(url, timeout=TIMEOUT, allow_redirects=True, ssl=False) as resp:
            status = resp.status
            if status == 200:
                text = await resp.text()
                # Basic validation: security.txt should contain Contact:
                has_contact = "contact:" in text.lower()
                return {
                    "domain": domain,
                    "url": url,
                    "status": status,
                    "found": True,
                    "valid": has_contact,
                    "size": len(text),
                }
            else:
                return {
                    "domain": domain,
                    "url": url,
                    "status": status,
                    "found": False,
                }
    except asyncio.TimeoutError:
        return {"domain": domain, "url": url, "found": False, "error": "timeout"}
    except Exception as e:
        return {"domain": domain, "url": url, "found": False, "error": str(e)[:100]}


async def check_all(domains: list[str]) -> list[dict]:
    """Check all domains with concurrency limit."""
    import aiohttp
    connector = aiohttp.TCPConnector(limit=MAX_CONCURRENT)
    async with aiohttp.ClientSession(connector=connector) as session:
        sem = asyncio.Semaphore(MAX_CONCURRENT)

        async def bounded_check(domain):
            async with sem:
                return await check_domain(session, domain)

        tasks = [bounded_check(d) for d in domains]
        results = await asyncio.gather(*tasks)
    return results


def update_disclosure_files(results: list[dict]):
    """Update disclosure JSON files with security_txt field."""
    # Build domain → result map
    domain_results = {r["domain"]: r for r in results}

    updated = 0
    for json_file in sorted(REGISTRY_DIR.rglob("*.json")):
        if "/_" in str(json_file):
            continue

        data = json.loads(json_file.read_text())
        namespace = data.get("namespace", "")
        result = domain_results.get(namespace)
        if not result:
            continue

        modified = False
        for node in data.get("match_nodes", []):
            node_data = node.get("data", {})

            if result["found"]:
                node_data["security_txt"] = {
                    "url": result["url"],
                    "checked": TODAY,
                }
                if result.get("valid") is False:
                    node_data["security_txt"]["note"] = "File exists but missing Contact: field"
            else:
                node_data["security_txt"] = None
                # We could add a note about why, but null is sufficient

            modified = True

        if modified:
            updated += 1
            if not DRY_RUN:
                json_file.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")

    print(f"Updated {updated} files" + (" (dry run)" if DRY_RUN else ""))


def main():
    # Collect all domains
    domains = set()
    for f in sorted(glob.glob("registry/disclosure/**/*.json", recursive=True)):
        if "/_" in f:
            continue
        d = json.load(open(f))
        ns = d.get("namespace", "")
        if ns:
            domains.add(ns)

    domains = sorted(domains)
    print(f"Checking {len(domains)} domains for security.txt...")

    # Run checks
    results = asyncio.run(check_all(domains))

    # Summary
    found = [r for r in results if r.get("found")]
    not_found = [r for r in results if not r.get("found") and not r.get("error")]
    errors = [r for r in results if r.get("error")]
    valid = [r for r in found if r.get("valid")]

    print(f"\nResults:")
    print(f"  Found: {len(found)} ({len(valid)} with Contact: field)")
    print(f"  Not found: {len(not_found)}")
    print(f"  Errors: {len(errors)}")

    # Save results
    RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    result_data = {
        "checked_at": TODAY,
        "total_domains": len(domains),
        "found": len(found),
        "not_found": len(not_found),
        "errors": len(errors),
        "results": sorted(results, key=lambda r: r["domain"]),
    }
    RESULTS_FILE.write_text(json.dumps(result_data, indent=2) + "\n")
    print(f"Results saved to {RESULTS_FILE}")

    # Update files if requested
    if UPDATE:
        update_disclosure_files(results)

    # Show some results
    if found:
        print(f"\nSample found ({min(10, len(found))}):")
        for r in found[:10]:
            v = "valid" if r.get("valid") else "no Contact:"
            print(f"  {r['domain']}: {v}")

    if errors:
        print(f"\nSample errors ({min(10, len(errors))}):")
        for r in errors[:10]:
            print(f"  {r['domain']}: {r['error'][:60]}")


if __name__ == "__main__":
    main()
