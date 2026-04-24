#!/usr/bin/env python3
"""Scan entity domains for well-known files and save content.

Reads CNA domains from disclosure registry entries, checks each for
well-known files (llms.txt, robots.txt, security.txt, etc.), validates
content is real (not soft 404s), and saves valid content to the
SecID-Entity-Data repo.

Usage:
  python3 scripts/scan-well-known.py
  python3 scripts/scan-well-known.py --workers 10  # fewer concurrent requests
  python3 scripts/scan-well-known.py --domains cisco.com,github.com  # specific domains only
"""

import argparse
import concurrent.futures
import json
import glob
import os
import re
import subprocess
import sys
from pathlib import Path

# ── Configuration ──

REGISTRY_DIR = os.path.join(os.path.dirname(__file__), "..", "registry")
DATA_REPO = os.path.join(os.path.dirname(__file__), "..", "..", "..",
                         "CloudSecurityAlliance-DataSets", "SecID-Entity-Data", "data")

# Files to check, grouped by path
FILES_TO_CHECK = [
    "llms.txt",
    "llms-full.txt",
    "robots.txt",
    "sitemap.xml",
    "security.txt",
    "humans.txt",
    "skill.md",
    "SKILL.MD",
    ".well-known/security.txt",
    ".well-known/change-password",
    ".well-known/openid-configuration",
    ".well-known/mta-sts.txt",
]

TIMEOUT = 8  # seconds per request


# ── Content Validation ──

def validate_content(filename: str, content: str) -> bool:
    """Check if content is a real file, not a soft 404 / homepage HTML."""
    if not content or len(content.strip()) < 10:
        return False

    stripped = content.strip()

    # Universal HTML check — if it starts with HTML tags, it's not what we want
    # (except for sitemap.xml which is XML)
    if filename != "sitemap.xml" and filename != ".well-known/openid-configuration":
        if stripped.startswith("<!") or stripped.startswith("<html") or stripped.startswith("<HTML"):
            return False

    if filename in ("llms.txt", "llms-full.txt"):
        return stripped.startswith("#")

    if filename in ("skill.md", "SKILL.MD"):
        return stripped.startswith("#") or stripped.startswith("---")

    if filename == "robots.txt":
        lower = stripped.lower()
        return "user-agent:" in lower or "disallow:" in lower or "allow:" in lower

    if filename == "sitemap.xml":
        return "<?xml" in stripped[:200] or "<urlset" in stripped[:500] or "<sitemapindex" in stripped[:500]

    if filename in ("security.txt", ".well-known/security.txt"):
        return "contact:" in stripped.lower()

    if filename == ".well-known/openid-configuration":
        try:
            data = json.loads(stripped)
            return "issuer" in data
        except (json.JSONDecodeError, ValueError):
            return False

    if filename == ".well-known/mta-sts.txt":
        lower = stripped.lower()
        return "version:" in lower and "mode:" in lower

    if filename == "humans.txt":
        # Should be plaintext, not HTML
        return not stripped.startswith("<")

    if filename == ".well-known/change-password":
        # Any non-HTML response is fine — it's a redirect target
        return not stripped.startswith("<!")

    return True


# ── Domain Extraction ──

def extract_domains() -> list[str]:
    """Get unique website domains from disclosure registry entries."""
    domains = set()
    for f in sorted(glob.glob(os.path.join(REGISTRY_DIR, "disclosure", "**", "*.json"), recursive=True)):
        try:
            data = json.load(open(f))
            for u in data.get("urls", []):
                if u.get("type") == "website":
                    url = u["url"].rstrip("/")
                    domain = url.replace("https://", "").replace("http://", "").split("/")[0]
                    domains.add(domain)
        except (json.JSONDecodeError, KeyError):
            continue
    return sorted(domains)


def domain_to_path(domain: str) -> str:
    """Convert domain to reverse-DNS directory path: cisco.com → com/cisco"""
    parts = domain.split(".")
    # Reverse: cisco.com → [com, cisco], aws.amazon.com → [com, amazon, aws]
    reversed_parts = list(reversed(parts))
    return os.path.join(*reversed_parts)


# ── Scanning ──

def check_file(domain: str, filename: str) -> dict | None:
    """Check a single well-known file at a domain. Returns result dict or None."""
    url = f"https://{domain}/{filename}"
    try:
        # Use separate header output to avoid polluting content
        r = subprocess.run(
            ["curl", "-s", "-L", "-o", "-", "-w", "\n__CURL_META__%{http_code}|%{url_effective}",
             "--max-time", str(TIMEOUT), url],
            capture_output=True, text=True, timeout=TIMEOUT + 5
        )
        output = r.stdout

        # Parse status and redirect URL from the end marker
        meta_match = re.search(r"\n__CURL_META__(\d+)\|(.+)$", output)
        if not meta_match:
            return None

        status = int(meta_match.group(1))
        effective_url = meta_match.group(2).strip()

        # Content is everything before our marker
        content = output[:meta_match.start()].strip()

        # Curl -L can prepend redirect URLs to output — strip leading http(s) lines
        while content.startswith(("http://", "https://")):
            newline = content.find("\n")
            if newline == -1:
                break
            content = content[newline:].strip()

        if status == 200 or (300 <= status < 400):
            if validate_content(filename, content):
                redirected = effective_url != url
                result = {"status": status}
                if redirected and status != 200:
                    result["url"] = effective_url
                return {"result": result, "content": content, "valid": True}
            else:
                return {"result": None, "content": None, "valid": False}
        else:
            return None  # 404, 500, etc — not found

    except (subprocess.TimeoutExpired, Exception):
        return None


def scan_domain(domain: str) -> dict:
    """Scan a single domain for all well-known files."""
    results = {}
    for filename in FILES_TO_CHECK:
        check = check_file(domain, filename)
        if check and check["valid"]:
            results[filename] = {
                "result": check["result"],
                "content": check["content"],
            }
        elif check and not check["valid"]:
            # Soft 404 — record as null (checked, not found)
            results[filename] = {"result": None, "content": None}
        # else: actual 404/error — also null
        else:
            results[filename] = {"result": None, "content": None}

    return results


# ── Output ──

def save_content(domain: str, filename: str, content: str) -> str | None:
    """Save file content to the data repo. Returns the file path or None."""
    if not os.path.isdir(DATA_REPO):
        return None

    domain_path = domain_to_path(domain)
    dir_path = os.path.join(DATA_REPO, domain_path)

    # Handle .well-known/ subdirectory
    if "/" in filename:
        subdir, fname = filename.rsplit("/", 1)
        dir_path = os.path.join(dir_path, subdir)
    else:
        fname = filename

    os.makedirs(dir_path, exist_ok=True)
    file_path = os.path.join(dir_path, fname)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    return file_path


def main():
    parser = argparse.ArgumentParser(description="Scan entity domains for well-known files")
    parser.add_argument("--workers", type=int, default=20, help="Concurrent workers (default: 20)")
    parser.add_argument("--domains", type=str, help="Comma-separated domains to scan (default: all CNAs)")
    args = parser.parse_args()

    if args.domains:
        domains = [d.strip() for d in args.domains.split(",")]
    else:
        domains = extract_domains()

    print(f"Scanning {len(domains)} domains for {len(FILES_TO_CHECK)} well-known files...")
    print(f"Max concurrent workers: {args.workers}")
    print(f"Data repo: {DATA_REPO}")
    print()

    # Scan all domains
    all_results = {}
    found_count = 0
    saved_count = 0

    def process_domain(domain):
        return domain, scan_domain(domain)

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(process_domain, d): d for d in domains}
        done = 0
        for future in concurrent.futures.as_completed(futures):
            done += 1
            domain, results = future.result()
            all_results[domain] = results

            # Save valid content and count
            domain_found = []
            for filename, data in results.items():
                if data["result"] is not None:
                    domain_found.append(filename)
                    if data["content"]:
                        path = save_content(domain, filename, data["content"])
                        if path:
                            saved_count += 1

            if domain_found:
                found_count += 1
                if done % 50 == 0 or done == len(domains):
                    print(f"  [{done}/{len(domains)}] {domain}: {', '.join(domain_found)}")
            elif done % 100 == 0:
                print(f"  [{done}/{len(domains)}] scanning...")

    # Build well_known summary for entity entries
    print(f"\n{'='*60}")
    print(f"Results: {found_count} domains with at least one well-known file")
    print(f"Files saved: {saved_count}")
    print()

    # Write summary JSON
    summary = {}
    for domain in sorted(all_results.keys()):
        well_known = {}
        for filename in FILES_TO_CHECK:
            data = all_results[domain].get(filename, {})
            if data.get("result") is not None:
                well_known[filename] = data["result"]
            else:
                well_known[filename] = None
        # Only include domains that have at least one file
        if any(v is not None for v in well_known.values()):
            summary[domain] = well_known

    summary_path = os.path.join(os.path.dirname(__file__), "..", "seed", "well-known-scan.json")
    os.makedirs(os.path.dirname(summary_path), exist_ok=True)
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"Summary written to: {summary_path}")
    print(f"Domains with files: {len(summary)}")

    # Print top-level stats
    file_counts = {}
    for domain_data in summary.values():
        for filename, result in domain_data.items():
            if result is not None:
                file_counts[filename] = file_counts.get(filename, 0) + 1

    print(f"\nFile prevalence:")
    for filename in FILES_TO_CHECK:
        count = file_counts.get(filename, 0)
        pct = (count / len(domains) * 100) if domains else 0
        bar = "#" * (count // 5)
        print(f"  {filename:<35} {count:>4} ({pct:4.1f}%) {bar}")


if __name__ == "__main__":
    main()
