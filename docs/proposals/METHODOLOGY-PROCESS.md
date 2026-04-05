# Methodology Authoring Process

How we research, document, and maintain methodology registry entries.

## Principles

1. **One file per namespace.** `registry/methodology/gov/nist.json` contains all NIST methodologies (IR 8477, RMF, 800-30, 800-61, 800-115).
2. **Follow the source's structure.** If NIST IR 8477 names four mapping styles, those become subpath match_nodes. Don't invent hierarchy the source doesn't have.
3. **Explicit "we looked and found nothing."** If a methodology has no sub-methodologies, use `children: []`. Null means researched; absent means not yet researched.
4. **The authoritative document is the source of truth.** Not blog posts, not summaries, not third-party descriptions.
5. **Verify the publisher domain.** SecID namespaces are domain names. Confirm the organization's actual domain before creating a file. SSVC is `cmu.edu` (CMU SEI/CERT/CC), not `cisa.gov` (CISA is an adopter).

## File Structure

Each namespace gets its own file:

```
registry/methodology/
├── gov/
│   ├── nist.json           # NIST: ir-8477, rmf, 800-30, 800-61, 800-115
│   └── cisa.json           # CISA: attck-mapping
├── org/
│   ├── first.json          # FIRST: cvss, epss, tlp
│   ├── iso.json            # ISO: 27005, 27035, 27037-27043, 29147, 30111, 31000, 27006, 27007, 17021
│   ├── mitre.json          # MITRE: ctid-framework-mapping, ctid-platform-mapping
│   ├── owasp.json          # OWASP: testing-guide
│   ├── opengroup.json      # The Open Group: fair
│   ├── cloudsecurityalliance.json  # CSA: ccm-mapping-methodology, incident-to-control, control-to-capability
│   ├── isecom.json         # ISECOM: osstmm
│   ├── verisframework.json # Verizon/VERIS: veris
│   └── commoncriteriaportal.json  # CCRA: cem
├── edu/
│   └── cmu.json            # CMU SEI/CERT/CC: ssvc
├── dev/
│   └── slsa.json           # OpenSSF: slsa
└── com/
    ├── microsoft.json      # Microsoft: stride
    ├── versprite.json      # VerSprite: pasta
    ├── threatmodeler.json  # ThreatModeler: vast
    └── pentest-standard.json  # PTES community: ptes (pentest-standard.org → com/pentest-standard.json)
```

## JSON Structure Per Namespace

```json
{
  "schema_version": "1.0",
  "namespace": "nist.gov",
  "type": "methodology",
  "status": "draft",
  "status_notes": "Initial research from NIST publication. Reviewed 2026-04-05.",

  "official_name": "National Institute of Standards and Technology",
  "urls": [
    {"type": "website", "url": "https://www.nist.gov/"}
  ],

  "match_nodes": [
    {
      "patterns": ["(?i)^ir-8477$"],
      "description": "NIST IR 8477: Mapping Relationships Between Documentary Standards, Regulations, Frameworks, and Guidelines",
      "weight": 100,
      "data": {
        "url": "https://csrc.nist.gov/pubs/ir/8477/final",
        "examples": ["ir-8477"]
      },
      "children": [
        {
          "patterns": ["(?i)^crosswalk$"],
          "description": "Crosswalk mapping: direct equivalence between elements from two documents",
          "weight": 100,
          "data": {
            "url": "https://csrc.nist.gov/pubs/ir/8477/final",
            "examples": [
              {"input": "crosswalk", "url": "https://csrc.nist.gov/pubs/ir/8477/final", "note": "Section describing crosswalk methodology"}
            ]
          }
        }
      ]
    }
  ]
}
```

## Research Process Per Methodology

### Pass 1: Identify and Verify (15 minutes)

1. Confirm the methodology is formally published (not just a blog concept)
2. Verify the publisher and their authoritative domain
3. Find the canonical URL for the methodology document
4. Identify if it has sub-methodologies (named components, steps, or metric groups)

### Pass 2: Document Structure (15 minutes)

1. Read the methodology document's table of contents / structure
2. Identify sub-components that should be independently referenceable (subpath match_nodes)
3. For versioned methodologies, check if `version_required` applies (do versions change the process materially?)
4. Note the canonical name the source uses

### Pass 3: Build Registry Entry (15 minutes)

1. Create the JSON entry following the schema above
2. Write match_node patterns (usually case-insensitive literal matches)
3. Write descriptions that explain what the methodology/sub-methodology does
4. Add resolution URLs
5. Add examples (bare strings at source level, ExampleObject at child level)

### Pass 4: Review (5 minutes)

1. Validate JSON parses: `python3 -c "import json; json.load(open('file.json'))"`
2. Check regex patterns are anchored (`^...$`)
3. Verify URLs are accessible
4. Confirm namespace matches filesystem path (reverse-DNS algorithm)

## Status Values

| Status | Meaning |
|--------|---------|
| `draft` | Entry created, needs review |
| `published` | Reviewed and verified against current source document |
| `needs-update` | Source has published a new version not yet reflected |

## Wave Plan

| Wave | Entries | Focus |
|------|---------|-------|
| 1 | IR 8477, CVSS, SSVC, CISA ATT&CK mapping, ISO 27005 | Validate pattern with high-priority standards |
| 2 | EPSS, ISO 29147, ISO 30111, NIST 800-61, ISO 27035, VERIS | Vulnerability & incident management |
| 3 | NIST 800-30, NIST RMF, FAIR, ISO 31000, NIST 800-115, CEM | Risk & assessment |
| 4 | STRIDE, PASTA, VAST, LINDDUN, TRIKE | Threat modeling |
| 5 | CSA CCM mapping, CTID, ISO forensics, TLP, SLSA, PTES, OWASP, OSSTMM, audit standards | Everything else |
| 6 | CSA incident-to-control, CSA control-to-capability | CSA draft methodologies (claim namespace) |
