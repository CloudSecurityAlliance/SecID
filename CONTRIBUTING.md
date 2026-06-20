# Contributing to SecID

Contributions are welcome! SecID is a community project and benefits from diverse input.

## Ways to Contribute

- **Registry additions** - New namespaces, seed data, corrections
- **Documentation** - Improvements, examples, clarifications
- **Spec feedback** - Edge cases, clarifications (spec changes are rare)
- **Research** - Identifying security identifier systems to include

## How to Contribute

### Feedback: the `submit_feedback` MCP tool (AI/MCP-only)

SecID feedback intake is **MCP-only by design** — there is no web form or issue queue for submissions. AI/MCP clients connected to the [live MCP server](https://secid.cloudsecurityalliance.org/) call the **`submit_feedback`** tool to:

- **Request a missing source/org** — `category: "missing-namespace"` (e.g. after a `not_found`)
- **Report incorrect data** — `category: "correction"` (wrong URL, outdated contact, bad pattern)
- **Suggest an improvement** — `category: "suggestion"`

Submissions land in the `secid_FEEDBACK` store for AI-assisted triage. If you're a human, talk to SecID through any MCP-capable AI client.

### Direct contribution: pull requests

If you're editing registry files directly:

1. **Make your changes** — follow existing patterns; see the [guides](docs/guides/)
2. **Fork the repository**
3. **Submit a pull request**

## File Formats

**Registry files** use YAML frontmatter + markdown (Obsidian-compatible):

```markdown
---
type: advisory
namespace: example
common_name: Example Advisory
---

# Content here...
```

**Documentation files** use plain markdown.

See [README.md](README.md#file-format) and [SPEC.md](SPEC.md#72-markdown-body-rich-context) for format details.

## Guidelines

- Follow existing patterns in the registry
- Use percent encoding for special characters in identifiers (see [SPEC.md](SPEC.md#82-percent-encoding))
- For regex pattern changes, follow [docs/guides/REGEX-WORKFLOW.md](docs/guides/REGEX-WORKFLOW.md) and include regex safety checks in PR notes
- Keep commit messages clear and concise
- One logical change per pull request

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). Please read it before participating.

## Questions?

Open a GitHub issue for questions or discussion.
