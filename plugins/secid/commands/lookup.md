---
name: secid-lookup
description: Look up what SecID knows about a type, namespace, or source. Use for browsing and discovery — "what advisory sources does Red Hat have?" or "what types exist?"
arguments:
  - name: query
    description: "Type, namespace, or source to look up (e.g., advisory, redhat.com, mitre.org/cve)"
    required: true
---

Use the SecID MCP server's `lookup` tool to browse registry data:

**Type:** infer from `$ARGUMENTS.query`
**Identifier:** infer from `$ARGUMENTS.query`

Present the results as a navigable list. If the user is exploring, suggest next steps they can drill into.
