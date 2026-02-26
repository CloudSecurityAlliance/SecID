# Registry Conversion Review Prompt

Use this prompt to have an AI review JSON conversions of registry files.

---

## Prompt

You are reviewing pilot conversions of SecID registry files from YAML+Markdown format to JSON format. Your job is to check that the conversions are accurate and complete.

**First, read these files to understand the formats:**

1. `docs/reference/REGISTRY-JSON-FORMAT.md` — The target JSON schema specification. This is the authority on what the JSON should look like.
2. `docs/reference/REGISTRY-FORMAT.md` — The current YAML+Markdown format being converted from.

**Then, for each pair below, read the original `.md` file and the new `.json` file and check for problems:**

| Original | Converted |
|----------|-----------|
| `registry/advisory/org/mitre.md` | `registry/advisory/org/mitre.json` |
| `registry/weakness/org/owasp.md` | `registry/weakness/org/owasp.json` |
| `registry/control/org/cloudsecurityalliance.md` | `registry/control/org/cloudsecurityalliance.json` |
| `registry/advisory/com/redhat.md` | `registry/advisory/com/redhat.json` |

**What to check:**

1. **Data loss** — Is any information from the YAML frontmatter or Markdown body missing in the JSON? Every URL, pattern, example, and piece of context should be accounted for.
2. **Field mapping** — Do fields map correctly per the migration table in `docs/reference/REGISTRY-JSON-FORMAT.md`? (`full_name` → `official_name`, `website` → `urls[]`, flat `sources` → nested `match_nodes` tree, etc.)
3. **Dropped fields** — `operator`, `established`, and `versions[]` should NOT appear in the JSON (they moved to the data layer). But the information they carried should be preserved in `notes` if it's useful context.
4. **Pattern correctness** — Are `match_nodes` `patterns[]` values anchored with `^...$`? Do name-level patterns use `(?i)` for case-insensitive matching? Do subpath-level children match the same strings as the original `id_pattern`?
5. **URL completeness** — Are all URLs from the original present in the JSON? Are URL types (`website`, `lookup`, `api`, `bulk_data`, `docs`, `github`) assigned correctly?
6. **Notes quality** — Does the top-level `notes` capture organizational context from the Markdown body? Do source-level `notes` capture operational quirks and resolution guidance? Is anything important from the Markdown lost?
7. **known_values** — Where the Markdown had tables enumerating items (e.g., OWASP Top 10 lists, CCM domains), are those captured as `known_values` in the appropriate node's `data` object?
8. **Null vs absent** — Per the spec: `null` means "we looked, nothing to find." Absent means "not yet researched." Are these used correctly?
9. **Status** — Original files used `status: active`. JSON should use `draft` (since these haven't been reviewed against JSON spec completeness requirements).
10. **JSON validity** — Is the JSON well-formed?
11. **lookup_table** — When the source has URLs that can't be computed from a pattern template (inconsistent slugs, non-derivable paths), did the converter use `lookup_table` to map IDs directly to URLs? Is `provenance` included (method, date, source_url)?
12. **URL verification** — For any `lookup_table` entries, did the converter verify the actual URLs rather than guessing them from a pattern? Inconsistent slugs are the whole reason `lookup_table` exists — guessed URLs defeat the purpose.

**Report format:** For each file, list any issues found. If no issues, say so. At the end, note any patterns or recurring problems that should be fixed before bulk conversion.
