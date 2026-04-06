---
name: secid-resolve
description: Resolve a SecID string to its URL(s) and registry data. Use when given a full SecID like secid:advisory/mitre.org/cve#CVE-2021-44228 or a partial identifier.
arguments:
  - name: secid
    description: The SecID string to resolve (e.g., secid:advisory/mitre.org/cve#CVE-2021-44228)
    required: true
---

Use the SecID MCP server's `resolve` tool to resolve this identifier:

**Input:** `$ARGUMENTS.secid`

If the result status is `found`, present the resolved URL(s) and key data.
If `corrected`, show what was corrected and the resolved result.
If `related`, show what's available at the matched level.
If `not_found`, suggest similar identifiers or guide the user.
