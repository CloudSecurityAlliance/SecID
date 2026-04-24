#!/usr/bin/env python3
"""Scan entity domains for MCP endpoints and API/MCP mentions in llms.txt.

Checks each domain for:
1. Live MCP endpoint at /mcp (POST with JSON-RPC initialize)
2. Wix-style MCP at /_api/mcp
3. MCP/API mentions in llms.txt and llms-full.txt content

Usage:
  python3 scripts/scan-mcp-endpoints.py
  python3 scripts/scan-mcp-endpoints.py --domains cisco.com,github.com
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

REGISTRY_DIR = os.path.join(os.path.dirname(__file__), "..", "registry")
DATA_REPO = os.path.join(os.path.dirname(__file__), "..", "..", "..",
                         "CloudSecurityAlliance-DataSets", "SecID-Entity-Data", "data")

TIMEOUT = 8

# MCP JSON-RPC initialize request
MCP_INITIALIZE = json.dumps({
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2025-03-26",
        "capabilities": {},
        "clientInfo": {"name": "secid-scanner", "version": "0.1.0"}
    }
})

# Paths to try for MCP endpoints
MCP_PATHS = ["/mcp", "/_api/mcp"]


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
    """Convert domain to reverse-DNS directory path."""
    parts = domain.split(".")
    return os.path.join(*reversed(parts))


def check_mcp_endpoint(domain: str, path: str) -> dict | None:
    """Try to connect to an MCP endpoint via POST with initialize request."""
    url = f"https://{domain}{path}"
    try:
        r = subprocess.run(
            ["curl", "-s", "-X", "POST",
             "-H", "Content-Type: application/json",
             "-H", "Accept: application/json, text/event-stream",
             "-d", MCP_INITIALIZE,
             "-w", "\n__CURL_META__%{http_code}",
             "--max-time", str(TIMEOUT),
             url],
            capture_output=True, text=True, timeout=TIMEOUT + 5
        )

        meta_match = re.search(r"\n__CURL_META__(\d+)$", r.stdout)
        if not meta_match:
            return None

        status = int(meta_match.group(1))
        content = r.stdout[:meta_match.start()].strip()

        # Check for valid MCP response
        if status == 200:
            # Try to parse as JSON-RPC response
            try:
                resp = json.loads(content)
                if "jsonrpc" in resp or "result" in resp:
                    return {
                        "url": url,
                        "status": 200,
                        "type": "jsonrpc",
                        "server_info": resp.get("result", {}).get("serverInfo", {}),
                    }
            except json.JSONDecodeError:
                pass

            # Check for SSE response (event stream)
            if content.startswith("event:") or content.startswith("data:"):
                # Try to parse SSE data for JSON-RPC
                for line in content.split("\n"):
                    if line.startswith("data:"):
                        try:
                            data = json.loads(line[5:].strip())
                            if "jsonrpc" in data or "result" in data:
                                return {
                                    "url": url,
                                    "status": 200,
                                    "type": "sse",
                                    "server_info": data.get("result", {}).get("serverInfo", {}),
                                }
                        except json.JSONDecodeError:
                            pass
                return {
                    "url": url,
                    "status": 200,
                    "type": "sse",
                    "server_info": {},
                }

        # 405 on GET could indicate MCP (stateless servers must 405 GET)
        # But we're POSTing, so 405 here means POST isn't accepted either

        return None

    except (subprocess.TimeoutExpired, Exception):
        return None


def scan_llms_for_mentions(domain: str) -> dict:
    """Check saved llms.txt files for MCP and API mentions."""
    domain_path = domain_to_path(domain)
    base = os.path.join(DATA_REPO, domain_path)

    mentions = {"mcp": [], "api": []}

    for filename in ["llms.txt", "llms-full.txt"]:
        filepath = os.path.join(base, filename)
        if not os.path.isfile(filepath):
            continue

        try:
            content = open(filepath, encoding="utf-8").read()
        except Exception:
            continue

        # Search for MCP mentions
        for line_num, line in enumerate(content.split("\n"), 1):
            if re.search(r"(?i)\bmcp\b|model.context.protocol", line):
                # Extract URLs from this line
                urls = re.findall(r"https?://[^\s\)\"'>`]+", line)
                mentions["mcp"].append({
                    "file": filename,
                    "line": line_num,
                    "text": line.strip()[:200],
                    "urls": urls,
                })

            # Search for API endpoint mentions
            if re.search(r"(?i)\bapi\b.*endpoint|rest\s*api|/api/v\d|graphql.*endpoint", line):
                urls = re.findall(r"https?://[^\s\)\"'>`]+", line)
                mentions["api"].append({
                    "file": filename,
                    "line": line_num,
                    "text": line.strip()[:200],
                    "urls": urls,
                })

    return mentions


def scan_domain(domain: str) -> dict:
    """Scan a single domain for MCP endpoints and llms.txt mentions."""
    result = {
        "mcp_endpoints": [],
        "llms_mentions": {"mcp": [], "api": []},
    }

    # Check live MCP endpoints
    for path in MCP_PATHS:
        endpoint = check_mcp_endpoint(domain, path)
        if endpoint:
            result["mcp_endpoints"].append(endpoint)

    # Check llms.txt for mentions
    result["llms_mentions"] = scan_llms_for_mentions(domain)

    return result


def main():
    parser = argparse.ArgumentParser(description="Scan for MCP endpoints and API mentions")
    parser.add_argument("--workers", type=int, default=20, help="Concurrent workers")
    parser.add_argument("--domains", type=str, help="Comma-separated domains")
    args = parser.parse_args()

    if args.domains:
        domains = [d.strip() for d in args.domains.split(",")]
    else:
        domains = extract_domains()

    print(f"Scanning {len(domains)} domains for MCP endpoints and API mentions...")
    print()

    all_results = {}

    def process_domain(domain):
        return domain, scan_domain(domain)

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(process_domain, d): d for d in domains}
        done = 0
        for future in concurrent.futures.as_completed(futures):
            done += 1
            domain, result = future.result()
            all_results[domain] = result

            has_endpoint = bool(result["mcp_endpoints"])
            has_mcp_mention = bool(result["llms_mentions"]["mcp"])
            has_api_mention = bool(result["llms_mentions"]["api"])

            if has_endpoint or has_mcp_mention:
                parts = []
                if has_endpoint:
                    urls = [e["url"] for e in result["mcp_endpoints"]]
                    parts.append(f"LIVE MCP: {', '.join(urls)}")
                if has_mcp_mention:
                    parts.append(f"MCP in llms.txt ({len(result['llms_mentions']['mcp'])} mentions)")
                if has_api_mention:
                    parts.append(f"API in llms.txt ({len(result['llms_mentions']['api'])} mentions)")
                print(f"  {domain}: {' | '.join(parts)}")

            if done % 100 == 0:
                print(f"  [{done}/{len(domains)}] scanning...")

    # Summary
    print(f"\n{'='*70}")

    live_mcp = {d: r for d, r in all_results.items() if r["mcp_endpoints"]}
    mcp_mentioned = {d: r for d, r in all_results.items() if r["llms_mentions"]["mcp"]}
    api_mentioned = {d: r for d, r in all_results.items() if r["llms_mentions"]["api"]}

    print(f"Live MCP endpoints found: {len(live_mcp)}")
    for domain, result in sorted(live_mcp.items()):
        for ep in result["mcp_endpoints"]:
            info = ep.get("server_info", {})
            name = info.get("name", "unknown")
            version = info.get("version", "?")
            print(f"  {ep['url']} ({ep['type']}) — {name} {version}")

    print(f"\nMCP mentioned in llms.txt: {len(mcp_mentioned)}")
    for domain in sorted(mcp_mentioned.keys()):
        print(f"  {domain}")

    print(f"\nAPI mentioned in llms.txt: {len(api_mentioned)}")
    for domain in sorted(api_mentioned.keys()):
        print(f"  {domain}")

    # Save results
    output = {
        "live_mcp_endpoints": {d: r["mcp_endpoints"] for d, r in sorted(live_mcp.items())},
        "mcp_in_llms": {d: r["llms_mentions"]["mcp"] for d, r in sorted(mcp_mentioned.items())},
        "api_in_llms": {d: r["llms_mentions"]["api"] for d, r in sorted(api_mentioned.items())},
    }
    out_path = os.path.join(os.path.dirname(__file__), "..", "seed", "mcp-api-scan.json")
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to: {out_path}")


if __name__ == "__main__":
    main()
