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

# Files to check — root-level conventions + .well-known security/AI/auth/privacy URIs
FILES_TO_CHECK = [
    # Root-level conventions
    "llms.txt",
    "llms-full.txt",
    "robots.txt",
    "sitemap.xml",
    "security.txt",
    "humans.txt",
    "skill.md",
    "SKILL.MD",
    # Security — vulnerability disclosure, advisories, SBOM
    ".well-known/security.txt",
    ".well-known/csaf/provider-metadata.json",
    ".well-known/csaf-aggregator",
    ".well-known/sbom",
    # Auth & identity infrastructure
    ".well-known/openid-configuration",
    ".well-known/oauth-authorization-server",
    ".well-known/oauth-protected-resource",
    ".well-known/openid-federation",
    ".well-known/webauthn",
    ".well-known/uma2-configuration",
    ".well-known/gnap-as-rs",
    ".well-known/hoba",
    ".well-known/did.json",
    ".well-known/did-configuration.json",
    ".well-known/ssf-configuration",
    ".well-known/idp-proxy",
    # Encryption & PKI
    ".well-known/est",
    ".well-known/cmp",
    ".well-known/pki-validation",
    ".well-known/posh",
    ".well-known/acme-challenge",
    ".well-known/ssh-known-hosts",
    ".well-known/sshfp",
    ".well-known/stun-key",
    ".well-known/edhoc",
    ".well-known/brski",
    # Email & transport security
    ".well-known/mta-sts.txt",
    ".well-known/enterprise-transport-security",
    ".well-known/enterprise-network-security",
    # Privacy
    ".well-known/gpc.json",
    ".well-known/dnt-policy.txt",
    ".well-known/ohttp-gateway",
    ".well-known/private-token-issuer-directory",
    # Network
    ".well-known/looking-glass",
    ".well-known/probing.txt",
    # App linking
    ".well-known/assetlinks.json",
    # Host metadata
    ".well-known/host-meta",
    ".well-known/host-meta.json",
    # MCP endpoints (checked via POST separately, but GET here for discovery)
    "mcp",
    "_api/mcp",
]

TIMEOUT = 8  # seconds per request


# ── Content Validation ──

def _is_html(content: str) -> bool:
    """Check if content looks like an HTML page (soft 404 detector)."""
    s = content.strip()[:200].lower()
    return s.startswith("<!doctype") or s.startswith("<html") or s.startswith("<head") or s.startswith("<!-")


def _is_valid_json_with(content: str, *required_keys: str) -> bool:
    """Check if content is valid JSON containing at least one of the required keys."""
    try:
        data = json.loads(content.strip())
        if isinstance(data, dict):
            return any(k in data for k in required_keys)
        return False
    except (json.JSONDecodeError, ValueError):
        return False


# Map of filename → validator function. If not listed, falls through to default.
# Validators return True if content is genuine, False if it's a soft 404.
_VALIDATORS = {
    # Root-level conventions
    "llms.txt":       lambda c: c.strip().startswith("#"),
    "llms-full.txt":  lambda c: c.strip().startswith("#"),
    "skill.md":       lambda c: c.strip().startswith("#") or c.strip().startswith("---"),
    "SKILL.MD":       lambda c: c.strip().startswith("#") or c.strip().startswith("---"),
    "robots.txt":     lambda c: any(k in c.lower() for k in ("user-agent:", "disallow:", "allow:")),
    "sitemap.xml":    lambda c: any(k in c[:500] for k in ("<?xml", "<urlset", "<sitemapindex")),
    "security.txt":   lambda c: "contact:" in c.lower(),
    "humans.txt":     lambda c: not _is_html(c),

    # Security — vulnerability disclosure, advisories, SBOM
    ".well-known/security.txt":                lambda c: "contact:" in c.lower(),
    ".well-known/csaf/provider-metadata.json": lambda c: _is_valid_json_with(c, "publisher", "metadata_version", "canonical_url"),
    ".well-known/csaf-aggregator":             lambda c: _is_valid_json_with(c, "aggregator", "csaf_providers"),
    ".well-known/sbom":                        lambda c: _is_valid_json_with(c, "sbom", "bom") or not _is_html(c),

    # Auth & identity — all JSON discovery documents
    ".well-known/openid-configuration":        lambda c: _is_valid_json_with(c, "issuer", "authorization_endpoint"),
    ".well-known/oauth-authorization-server":  lambda c: _is_valid_json_with(c, "issuer", "authorization_endpoint"),
    ".well-known/oauth-protected-resource":    lambda c: _is_valid_json_with(c, "resource"),
    ".well-known/openid-federation":           lambda c: not _is_html(c) and len(c.strip()) > 20,
    ".well-known/webauthn":                    lambda c: _is_valid_json_with(c, "origins", "rpId") or (not _is_html(c) and len(c.strip()) > 10),
    ".well-known/uma2-configuration":          lambda c: _is_valid_json_with(c, "issuer"),
    ".well-known/gnap-as-rs":                  lambda c: _is_valid_json_with(c, "grant_request_endpoint"),
    ".well-known/hoba":                        lambda c: not _is_html(c),
    ".well-known/did.json":                    lambda c: _is_valid_json_with(c, "id", "@context"),
    ".well-known/did-configuration.json":      lambda c: _is_valid_json_with(c, "linked_dids", "@context"),
    ".well-known/ssf-configuration":           lambda c: _is_valid_json_with(c, "issuer", "delivery_methods_supported"),
    ".well-known/idp-proxy":                   lambda c: not _is_html(c),

    # Encryption & PKI
    ".well-known/est":                         lambda c: not _is_html(c),
    ".well-known/cmp":                         lambda c: not _is_html(c),
    ".well-known/pki-validation":              lambda c: not _is_html(c),
    ".well-known/posh":                        lambda c: _is_valid_json_with(c, "fingerprints", "expires"),
    ".well-known/acme-challenge":              lambda c: not _is_html(c),
    ".well-known/ssh-known-hosts":             lambda c: not _is_html(c) and ("ssh-" in c or "ecdsa-" in c),
    ".well-known/sshfp":                       lambda c: not _is_html(c),
    ".well-known/stun-key":                    lambda c: not _is_html(c),
    ".well-known/edhoc":                       lambda c: not _is_html(c),
    ".well-known/brski":                       lambda c: not _is_html(c),

    # Email & transport security
    ".well-known/mta-sts.txt":                 lambda c: "version:" in c.lower() and "mode:" in c.lower(),
    ".well-known/enterprise-transport-security": lambda c: not _is_html(c) and len(c.strip()) > 10,
    ".well-known/enterprise-network-security":   lambda c: not _is_html(c) and len(c.strip()) > 10,

    # Privacy
    ".well-known/gpc.json":                    lambda c: _is_valid_json_with(c, "gpc"),
    ".well-known/dnt-policy.txt":              lambda c: "tracking" in c.lower() or "dnt" in c.lower(),
    ".well-known/ohttp-gateway":               lambda c: not _is_html(c),
    ".well-known/private-token-issuer-directory": lambda c: _is_valid_json_with(c, "token-keys") or not _is_html(c),

    # Network
    ".well-known/looking-glass":               lambda c: not _is_html(c),
    ".well-known/probing.txt":                 lambda c: not _is_html(c) and "probe" in c.lower(),

    # App linking
    ".well-known/assetlinks.json":             lambda c: c.strip().startswith("[") and "target" in c,

    # Host metadata
    ".well-known/host-meta":                   lambda c: "<?xml" in c[:200] or "<XRD" in c[:200],
    ".well-known/host-meta.json":              lambda c: _is_valid_json_with(c, "links"),

    # MCP — GET won't return MCP data, but may reveal an info page
    "mcp":                                     lambda c: not _is_html(c) or "mcp" in c.lower()[:500],
    "_api/mcp":                                lambda c: not _is_html(c) or "mcp" in c.lower()[:500],
}


def validate_content(filename: str, content: str) -> bool:
    """Check if content is a real file, not a soft 404 / homepage HTML."""
    if not content or len(content.strip()) < 10:
        return False

    validator = _VALIDATORS.get(filename)
    if validator:
        return validator(content)

    # Default: not HTML = probably real
    return not _is_html(content)


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
