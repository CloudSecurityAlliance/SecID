# secid-user

**Status: Stub — not yet built.** Blocked on SecID-Service (Cloudflare Worker REST API + MCP server) and registry stabilization before building.

## Purpose

Single skill for anyone who wants to **use SecID** — consuming, referencing, looking up, or integrating security knowledge identifiers. One entry point, the skill figures out what the user needs.

## Audience

- Security practitioners referencing vulnerabilities, controls, techniques in documents
- AI agents that need to find or cite security knowledge
- Tool builders integrating SecID into their products
- Anyone asking "what is this SecID?" or "give me the SecID for X"

## What This Skill Will Cover

### Resolve
Given a SecID string, find the resource. Parse the identifier, look it up in the registry, return URL(s). Handle version disambiguation (when version is omitted and the source requires it, return all matches with guidance).

### Lookup (Reverse Resolve)
Given a security concept ("OWASP Top 10 A01", "prompt injection", "CWE-79"), find the corresponding SecID(s). Search across registry files by name, known_values, descriptions.

### Reference
Create properly formatted SecID strings. For document authors who know what they want to reference but need the correct syntax. Validate against the registry. Batch formatting ("here are 10 CVEs, give me SecIDs").

### Explain
Given a SecID, explain what it identifies in human-readable terms. Uses registry notes, known_values, descriptions, and version context to provide meaningful explanation beyond just a URL.

### Integrate
Guidance for building tools that consume SecID. Grammar rules, parsing algorithm, resolution pipeline, encoding rules for URLs/filenames, how to handle the version disambiguation response.

## Dependencies Before Building

- [ ] Registry has sufficient coverage (~500+ namespaces per ROADMAP.md v1.0 target)
- [ ] SecID-Service deployed (Cloudflare Worker REST API — does parse → lookup → URL)
- [ ] SecID-Service MCP server operational (so AI agents can call resolution as a tool)
- [ ] SPEC.md grammar is stable (v1.0)
- [ ] Version resolution behavior implemented in SecID-Service (not just documented)
- [ ] Compliance test suite passing (see [skills/compliance-testing/](../compliance-testing/))

This skill cannot be built until a working resolver exists — you can't use SecID without one.

## Resources This Skill Will Bundle

- SecID grammar reference (from SPEC.md)
- Type definitions and when to use each
- Resolution behavior documentation
- Version disambiguation explanation
- Encoding rules for different contexts (URLs, filenames, databases)
- Example SecIDs across all types

## Open Questions

- How much of the registry data should the skill have access to directly vs. calling an API?
- Should the skill include offline resolution (embedded registry snapshot) or always require API access?
- How to handle "I don't know this SecID" gracefully — suggest similar, explain what types/namespaces exist?
