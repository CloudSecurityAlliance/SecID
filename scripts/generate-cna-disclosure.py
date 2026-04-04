#!/usr/bin/env python3
"""Generate disclosure registry JSON files for all CVE CNA partners.

Run from repo root: python3 scripts/generate-cna-disclosure.py

Reads: working-data/cna/partner-details.json, seed/cve-cna-partners-raw.json
Writes: registry/disclosure/<tld>/<domain>.json (one file per namespace)
"""

import json
import os
import re
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlparse

DETAILS_FILE = Path("working-data/cna/partner-details.json")
SEED_FILE = Path("seed/cve-cna-partners-raw.json")
REGISTRY_DIR = Path("registry/disclosure")

# Manual domain overrides for partners where auto-derivation fails or is wrong
DOMAIN_OVERRIDES = {
    # Failed scrapes (8 timeouts)
    "BlackDuck": "blackduck.com",
    "Checkmarx": "checkmarx.com",
    "Danfoss": "danfoss.com",
    "Joomla": "joomla.org",
    "PandoraFMS": "pandorafms.com",
    "Samsung_Mobile": "samsung.com",
    "VulnCheck": "vulncheck.com",
    "tibco": "tibco.com",
    # Domain corrections where auto-derivation picks a subdomain or wrong domain
    "cloud.com": None,  # handled per-slug below
    "Jaspersoft": "cloud.com",
    "NetScaler": "cloud.com",
    "Spotfire": "cloud.com",
}

# Official names for known namespaces (domain -> (official, common))
# Auto-generated entries will derive from partner name
KNOWN_NAMES = {
    "redhat.com": ("Red Hat, Inc.", "Red Hat"),
    "google.com": ("Google LLC", "Google"),
    "cisa.gov": ("Cybersecurity and Infrastructure Security Agency", "CISA"),
    "mitre.org": ("The MITRE Corporation", "MITRE"),
    "github.com": ("GitHub, Inc.", "GitHub"),
    "samsung.com": ("Samsung", "Samsung"),
    "broadcom.com": ("Broadcom Inc.", "Broadcom"),
    "cisco.com": ("Cisco Systems, Inc.", "Cisco"),
    "chromium.org": ("The Chromium Projects", "Chromium"),
}


def derive_domain(p):
    """Derive org's primary domain from URLs and emails."""
    candidates = Counter()

    for c in p.get("contacts", []):
        if c["type"] == "email":
            domain = c["value"].split("@")[-1]
            if domain not in ("gmail.com", "outlook.com", "yahoo.com", "protonmail.com"):
                candidates[domain] += 10

    for pol in p.get("policy_urls", []):
        d = urlparse(pol.get("url", "")).netloc.removeprefix("www.")
        if d and "cve.org" not in d:
            candidates[d] += 5

    for cp in p.get("contact_pages", []):
        d = urlparse(cp.get("url", "")).netloc.removeprefix("www.")
        if d and "cve.org" not in d:
            candidates[d] += 3

    if p.get("advisories_url"):
        d = urlparse(p["advisories_url"]).netloc.removeprefix("www.")
        if d and "cve.org" not in d:
            candidates[d] += 3

    for link in p.get("other_links", []):
        d = urlparse(link.get("url", "")).netloc.removeprefix("www.")
        if d and "cve.org" not in d:
            candidates[d] += 1

    if not candidates:
        return None

    # Group by root domain
    root_scores = Counter()
    for domain, score in candidates.most_common():
        parts = domain.split(".")
        if len(parts) >= 2:
            root = ".".join(parts[-2:])
            if parts[-2] in ("co", "or", "com", "ac", "go", "ne", "org", "gov", "europa") and len(parts) >= 3:
                root = ".".join(parts[-3:])
            root_scores[root] += score

    return root_scores.most_common(1)[0][0] if root_scores else None


def domain_to_path(domain):
    """Convert domain to registry filesystem path."""
    parts = domain.split(".")
    if len(parts) == 2:
        return REGISTRY_DIR / parts[1] / f"{parts[0]}.json"
    elif len(parts) == 3:
        return REGISTRY_DIR / parts[2] / parts[1] / f"{parts[0]}.json"
    else:
        raise ValueError(f"Unexpected domain format: {domain}")


MULTI_SCOPE_RE = re.compile(
    r"((?:Top-Level )?Root Scope|CNA-LR Scope|CNA Scope|ADP Scope|Secretariat Scope):\s*"
)


def parse_multi_scope(scope_text):
    """Split 'Root Scope: ... CNA Scope: ...' into dict."""
    parts = MULTI_SCOPE_RE.split(scope_text)
    if len(parts) <= 1:
        return None
    result = {}
    for i in range(1, len(parts), 2):
        label = parts[i].strip()
        text = parts[i + 1].strip() if i + 1 < len(parts) else ""
        if text:
            result[label] = text
    return result if result else None


def make_node_name(slug, roles, all_slugs_for_domain):
    """Generate a match_node name from slug and roles."""
    role_text = ", ".join(roles).lower()

    # Special cases for multi-CNA same org
    if len(all_slugs_for_domain) > 1:
        # Use slug-based disambiguation
        slug_lower = slug.lower()
        # Known patterns
        name_map = {
            "github_m": "cna",
            "github_p": "cna-products",
            "icscert": "cna-ics",
            "cisa-cg": "cna-civilian",
            "samsung_mobile": "cna-mobile",
            "samsung.tv_appliance": "cna-tv-appliance",
            "google_android": "cna-android",
            "googlecloud": "cna-cloud",
            "google_devices": "cna-devices",
            "mandiant": "cna-mandiant",
            "chrome": "cna-chrome",
            "chromeos": "cna-chromeos",
            "talos": "cna-talos",
            "brocade": "cna-brocade",
            "ca": "cna-ca",
            "symantec": "cna-symantec",
            "vmware": "cna-vmware",
            "becdx": "cna-diagnostics",
            "becls": "cna-life-sciences",
            "s21sec": "cna-s21sec",
            "jaspersoft": "cna-jaspersoft",
            "netscaler": "cna-netscaler",
            "spotfire": "cna-spotfire",
        }
        if slug_lower in name_map:
            return name_map[slug_lower]

    # Determine from role text
    if "top-level root" in role_text and "secretariat" in role_text:
        return "cna-secretariat"
    if "top-level root" in role_text:
        return "cna-tlr"
    if "cna-lr" in role_text:
        return "cna-lr"
    if "adp" in role_text:
        return "cna-adp"
    # "Root" without "CNA" in the same role entry = Root-only role
    if "root" in role_text and "cna" not in role_text.replace("root", ""):
        return "cna-root"

    return "cna"


def get_weight(name):
    """Assign weight based on node name."""
    weights = {
        "cna": 80,
        "cna-root": 60,
        "cna-lr": 50,
        "cna-tlr": 40,
        "cna-adp": 40,
        "cna-secretariat": 30,
    }
    # Default 80 for specific product/division CNAs
    return weights.get(name, 80)


def build_contacts(p):
    """Build contacts array from partner detail."""
    contacts = []
    for c in p.get("contacts", []):
        if c["type"] == "email":
            contacts.append({"type": "email", "value": c["value"], "note": c.get("label")})
    for c in p.get("contact_pages", []):
        contacts.append({"type": "web", "value": c["url"], "note": c.get("text")})
    return contacts or None


def build_urls(p):
    """Build urls array from partner detail."""
    urls = []
    for pol in p.get("policy_urls", []):
        urls.append({"type": "docs", "url": pol["url"], "note": "Disclosure policy"})
    if p.get("advisories_url"):
        urls.append({"type": "website", "url": p["advisories_url"], "note": "Security advisories"})
    urls.append({"type": "website", "url": p["source_url"], "note": "CVE partner page"})
    return urls


def build_urls_from_seed(seed_entry):
    """Build minimal urls for partners without detail data."""
    return [{"type": "website", "url": seed_entry["partner_url"], "note": "CVE partner page"}]


def main():
    details = json.load(open(DETAILS_FILE))["partners"]
    seed = json.load(open(SEED_FILE))

    # Build seed lookup by slug
    seed_by_slug = {}
    for p in seed["partners"]:
        slug = p["partner_url"].split("/partner/")[-1]
        seed_by_slug[slug] = p

    # Step 1: Map all slugs to domains
    slug_to_domain = {}

    for slug, p in details.items():
        if slug in DOMAIN_OVERRIDES:
            slug_to_domain[slug] = DOMAIN_OVERRIDES[slug]
        else:
            slug_to_domain[slug] = derive_domain(p)

    # Add failed-scrape partners from overrides
    for slug, domain in DOMAIN_OVERRIDES.items():
        if domain and slug not in slug_to_domain:
            slug_to_domain[slug] = domain

    # Step 2: Group by domain
    by_domain = defaultdict(list)
    for slug, domain in slug_to_domain.items():
        if domain:
            by_domain[domain].append(slug)

    print(f"Mapping: {len(slug_to_domain)} slugs -> {len(by_domain)} unique domains")

    # Step 3: Generate files
    generated = 0
    total_nodes = 0

    for domain, slugs in sorted(by_domain.items()):
        path = domain_to_path(domain)

        # Skip the CSA entry (hand-crafted)
        if domain == "cloudsecurityalliance.org":
            continue

        # Determine namespace-level metadata
        official, common = KNOWN_NAMES.get(domain, (None, None))
        if not official:
            # Use the first partner's name, or shortest name
            names = []
            for s in slugs:
                if s in details:
                    names.append(details[s].get("partner", ""))
                elif s in seed_by_slug:
                    names.append(seed_by_slug[s].get("partner", ""))
            official = min(names, key=len) if names else domain
            common = None

        countries = set()
        for s in slugs:
            if s in details:
                c = details[s].get("table", {}).get("Country*", "")
                if c:
                    countries.add(c)
            elif s in seed_by_slug:
                c = seed_by_slug[s].get("country", "")
                if c:
                    countries.add(c)

        # Build match_nodes
        match_nodes = []
        for slug in slugs:
            if slug in details:
                p = details[slug]
                roles = p.get("table", {}).get("Program Role", [])
                if isinstance(roles, str):
                    roles = [roles]
                scope = p.get("table", {}).get("Scope", "")
                org_types = p.get("table", {}).get("Organization Type", [])
                if isinstance(org_types, str):
                    org_types = [org_types]
            elif slug in seed_by_slug:
                s = seed_by_slug[slug]
                roles = [s.get("program_role", "CNA")]
                scope = s.get("scope", "")
                org_types = [s.get("organization_type", "")]
            else:
                continue

            multi_scope = parse_multi_scope(scope)

            if multi_scope and len(roles) > 1:
                # Multi-role: create separate nodes per role
                for role_text in roles:
                    name = make_node_name(slug, [role_text], slugs)
                    # Find matching scope
                    role_lower = role_text.lower()
                    matched_scope = None
                    if "top-level root" in role_lower:
                        matched_scope = multi_scope.get("Top-Level Root Scope") or multi_scope.get("Root Scope")
                    elif "cna-lr" in role_lower:
                        matched_scope = multi_scope.get("CNA-LR Scope")
                    elif "root" in role_lower:
                        matched_scope = multi_scope.get("Root Scope")
                    elif "adp" in role_lower:
                        matched_scope = multi_scope.get("ADP Scope")
                    elif "secretariat" in role_lower:
                        matched_scope = multi_scope.get("Secretariat Scope")
                    else:
                        matched_scope = multi_scope.get("CNA Scope")
                    if not matched_scope:
                        matched_scope = scope

                    node = {
                        "patterns": [f"(?i)^{re.escape(name)}$"],
                        "description": role_text,
                        "weight": get_weight(name),
                        "data": {
                            "scope": matched_scope,
                            "cve_program_role": role_text,
                            "organization_type": ", ".join(org_types) if org_types != ["N/A"] else None,
                            "contacts": build_contacts(p) if slug in details else None,
                            "urls": build_urls(p) if slug in details else build_urls_from_seed(seed_by_slug.get(slug, {})),
                            "examples": [],
                        },
                    }
                    match_nodes.append(node)
            else:
                # Single role
                name = make_node_name(slug, roles, slugs)
                node = {
                    "patterns": [f"(?i)^{re.escape(name)}$"],
                    "description": ", ".join(roles) if roles else "CNA",
                    "weight": get_weight(name),
                    "data": {
                        "scope": scope,
                        "cve_program_role": ", ".join(roles),
                        "organization_type": ", ".join(org_types) if org_types != ["N/A"] else None,
                        "contacts": build_contacts(p) if slug in details else None,
                        "urls": build_urls(p) if slug in details else build_urls_from_seed(seed_by_slug.get(slug, {})),
                        "examples": [],
                    },
                }
                match_nodes.append(node)

        if not match_nodes:
            continue

        entry = {
            "schema_version": "1.0",
            "namespace": domain,
            "type": "disclosure",
            "status": "draft",
            "status_notes": "Generated from CVE CNA partner data (cve.org), 2026-04-03.",
            "official_name": official,
            "common_name": common,
            "alternate_names": None,
            "notes": f"CVE Program partner. Country: {', '.join(sorted(countries))}." if countries else None,
            "wikidata": None,
            "wikipedia": None,
            "urls": [{"type": "website", "url": f"https://{domain}"}],
            "match_nodes": match_nodes,
        }

        os.makedirs(path.parent, exist_ok=True)
        path.write_text(json.dumps(entry, indent=2, ensure_ascii=False))
        total_nodes += len(match_nodes)
        generated += 1

    print(f"Generated {generated} disclosure files with {total_nodes} total match_nodes")


if __name__ == "__main__":
    main()
