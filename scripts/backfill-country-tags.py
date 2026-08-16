#!/usr/bin/env python3
"""Derive `tags.country` from a namespace's country-code TLD.

Country is one of the few facets worth filtering the whole registry by — "show
me every Japanese control framework" is a real question — but `tags.country` sat
at 5% coverage because every value had to be added by hand. A ccTLD answers it
mechanically for a fifth of the registry.

The tag stays the authority; the TLD is only a proxy for it. An existing
`tags.country` is never overwritten, and namespaces with no ccTLD
(cloudsecurityalliance.org is US-based, nist.gov is US) can only ever be
curated. Everything written here records that it was derived rather than
verified, so a later human pass can tell the two apart.

Two ways this proxy lies, both handled:

  * Vanity TLDs. `.io` is British Indian Ocean Territory and `.ai` is Anguilla,
    but in this registry they are 33 tech vendors and 19 AI-security vendors.
    Tagging them by TLD would be worse than leaving them untagged.
  * ccTLD is not the ISO code. The UK's ccTLD is `.uk`; its ISO 3166-1 alpha-2
    code is `GB`. `.eu` is not a country at all, and is emitted as `EU` per the
    convention already in the schema.

Usage:
    python3 scripts/backfill-country-tags.py --dry-run   # report, change nothing
    python3 scripts/backfill-country-tags.py             # write tags
    python3 scripts/backfill-country-tags.py --check     # exit 1 if any are missing
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATE = "2026-08-15"

# Two-letter TLDs that are sold as vanity domains rather than used as country
# signals. Derived from what is actually in this registry — see the module
# docstring. Anything here is left untagged rather than tagged wrongly.
VANITY_TLDS = {
    "io", "ai", "co", "me", "cc", "sh", "tv", "ly", "to", "st",
    "gg", "fm", "ws", "vc", "is",
}

# ccTLDs whose ISO 3166-1 alpha-2 code differs from the TLD string.
CCTLD_OVERRIDES = {
    "uk": "GB",   # ISO code for the United Kingdom is GB
    "eu": "EU",   # not a country; the schema documents EU as an allowed value
}


def country_for(namespace: str) -> str | None:
    """ISO code implied by the namespace's TLD, or None if it implies nothing."""
    domain = namespace.split("/")[0]
    tld = domain.rsplit(".", 1)[-1].lower()
    if tld in CCTLD_OVERRIDES:
        return CCTLD_OVERRIDES[tld]
    if len(tld) != 2 or tld in VANITY_TLDS:
        return None
    return tld.upper()


def insert_tags(text: str, country: str) -> str:
    """Append tags + provenance before the document's closing brace.

    Text surgery rather than json.dumps: reserialising would reformat every
    untouched line and bury a two-line change in a whole-file diff.
    """
    body = text.rstrip()
    assert body.endswith("}"), "registry file does not end with an object"
    head = body[:-1].rstrip()
    # the previous property now needs a separator
    if not head.endswith(","):
        head += ","
    block = (
        f'\n  "tags": {{"country": ["{country}"]}},\n'
        f'  "_country_provenance": {{\n'
        f'    "method": "derived from country-code TLD",\n'
        f'    "date": "{DATE}",\n'
        f'    "note": "Not verified against the organisation itself. A ccTLD implies '
        f'where a domain was registered, not necessarily where the body operates — '
        f'correct this field directly if it is wrong, and it will not be overwritten."\n'
        f'  }}\n}}\n'
    )
    return head + block


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if any namespace could be tagged but is not")
    args = ap.parse_args()

    would, skipped_curated, no_signal = [], 0, 0

    for path in sorted((REPO_ROOT / "registry").rglob("*.json")):
        if path.name.startswith("_"):
            continue
        text = path.read_text(encoding="utf-8")
        try:
            doc = json.loads(text)
        except json.JSONDecodeError:
            continue
        if not isinstance(doc, dict) or "match_nodes" not in doc:
            continue

        if (doc.get("tags") or {}).get("country"):
            skipped_curated += 1
            continue

        country = country_for(doc["namespace"])
        if not country:
            no_signal += 1
            continue

        would.append((path, doc["namespace"], country))
        if not (args.dry_run or args.check):
            new = insert_tags(text, country)
            json.loads(new)  # never write something that will not parse
            path.write_text(new, encoding="utf-8")

    verb = "would tag" if (args.dry_run or args.check) else "tagged"
    print(f"{verb} {len(would)} namespace(s)")
    print(f"  already curated : {skipped_curated}")
    print(f"  no country signal: {no_signal} (no ccTLD, or a vanity TLD)")

    by_country: dict[str, int] = {}
    for _, _, c in would:
        by_country[c] = by_country.get(c, 0) + 1
    if by_country:
        top = sorted(by_country.items(), key=lambda kv: -kv[1])[:12]
        print("  " + "  ".join(f"{c}:{n}" for c, n in top))

    if args.check and would:
        print("\nFAIL - run scripts/backfill-country-tags.py to tag these.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
