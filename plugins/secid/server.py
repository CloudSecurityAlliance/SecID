#!/usr/bin/env python3
"""SecID MCP Server — local server that calls the SecID REST API.

Install: pip install mcp httpx
Run:     python server.py
         python server.py --base-url https://internal-secid.example.org

Configure in Claude Code:
  .mcp.json: {"mcpServers": {"secid": {"command": "python", "args": ["server.py"]}}}
"""

import argparse
import json
import httpx
from mcp.server.fastmcp import FastMCP

SECID_TYPES = [
    "advisory", "capability", "control", "disclosure", "entity",
    "methodology", "reference", "regulation", "ttp", "weakness",
]

DEFAULT_BASE_URL = "https://secid.cloudsecurityalliance.org"

parser = argparse.ArgumentParser(description="SecID MCP Server")
parser.add_argument(
    "--base-url",
    default=DEFAULT_BASE_URL,
    help=f"SecID API base URL (default: {DEFAULT_BASE_URL})",
)
args, _ = parser.parse_known_args()

mcp = FastMCP(
    "SecID",
    instructions="Resolve, look up, and describe security knowledge identifiers across 700+ sources — CVEs, CWEs, ATT&CK, NIST controls, and more.",
)
client = httpx.Client(timeout=30.0)


def _resolve(secid: str) -> dict:
    """Call the SecID REST API and return the JSON response."""
    resp = client.get(
        f"{args.base_url}/api/v1/resolve",
        params={"secid": secid},
    )
    resp.raise_for_status()
    return resp.json()


@mcp.tool()
def resolve(secid: str) -> str:
    """Resolve a SecID string to URLs and registry data.

    Examples:
      secid:advisory/mitre.org/cve#CVE-2021-44228  → CVE record URL
      secid:weakness/mitre.org/cwe#CWE-79          → CWE definition URL
      secid:ttp/mitre.org/attack#T1059.003          → ATT&CK technique URL
      secid:control/nist.gov/csf@2.0#PR.AC-1        → NIST CSF control
      secid:methodology/first.org/cvss@4.0           → CVSS v4.0 specification
      secid:advisory/CVE-2021-44228                  → cross-source search
    """
    return json.dumps(_resolve(secid), indent=2)


@mcp.tool()
def lookup(type: str, identifier: str) -> str:
    """Look up a security identifier by type and identifier string.

    Args:
        type: Security knowledge type (advisory, capability, control, disclosure,
              entity, methodology, reference, regulation, ttp, weakness)
        identifier: The identifier to search for (e.g., CVE-2021-44228, CWE-79, T1059.003)
    """
    secid = f"secid:{type}/{identifier}"
    return json.dumps(_resolve(secid), indent=2)


@mcp.tool()
def describe(secid: str) -> str:
    """Describe a SecID type, namespace, or source — what it covers, how many entries, examples.

    Examples:
      secid:advisory                    → list all advisory namespaces
      secid:advisory/mitre.org          → describe MITRE's advisory sources
      secid:advisory/mitre.org/cve      → describe the CVE source specifically
      secid:methodology                 → list all methodology namespaces
    """
    # Strip subpath for describe
    hash_idx = secid.find("#")
    if hash_idx != -1:
        secid = secid[:hash_idx]
    return json.dumps(_resolve(secid), indent=2)


if __name__ == "__main__":
    mcp.run()
