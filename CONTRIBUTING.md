# Contributing to SecID

Contributions are welcome! SecID is a community project and benefits from diverse input.

## Ways to Contribute

- **Registry additions** - New namespaces, seed data, corrections
- **Documentation** - Improvements, examples, clarifications
- **Spec feedback** - Edge cases, clarifications (spec changes are rare)
- **Research** - Identifying security identifier systems to include

## How to Contribute

You don't need to write any code or YAML to contribute data.

### The easy path: issue forms

[**Open an issue**](https://github.com/CloudSecurityAlliance/SecID/issues/new/choose) and pick a form:

- **Add or update a namespace (source)** — a new security-knowledge source of any type (advisory, control, methodology, reference, …)
- **Add an organization or product (entity)** — short form; name + domain is enough
- **Report a problem** — a correction, broken link, or wrong resolution

Fill in the fields and submit. A maintainer turns it into a registry entry. This is the recommended path for most contributions.

### The direct path: pull requests

If you're comfortable editing registry files:

1. **Open an issue** first for anything non-trivial — discuss before starting work
2. **Fork the repository**
3. **Make your changes** (follow existing patterns; see the [guides](docs/guides/))
4. **Submit a pull request**

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
