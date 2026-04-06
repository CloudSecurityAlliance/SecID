---
name: secid-describe
description: Describe a SecID type — what it covers, how many namespaces, examples. Use when the user asks "what is the methodology type?" or "what types does SecID have?"
arguments:
  - name: type
    description: "SecID type to describe (advisory, capability, control, disclosure, entity, methodology, reference, regulation, ttp, weakness)"
    required: false
---

Use the SecID MCP server's `describe` tool.

If `$ARGUMENTS.type` is provided, describe that specific type.
If no type is given, list all 10 types with their descriptions and namespace counts.
