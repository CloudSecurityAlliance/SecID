---
# Identity
namespace: ""
full_name: ""
type: disclosure
operator: ""  # e.g., "secid:entity/example.com" or "secid:entity/example.com/product"

# Access
urls:
  website: ""
  security_txt: ""  # URL to security.txt if applicable
  reporting_form: ""  # URL to vulnerability reporting form
  policy: ""  # URL to disclosure policy page

# Contact
contacts:
  - type: ""  # email, form, platform
    value: ""  # e.g., "security@example.com" or HackerOne program URL
    preferred: false

# Program Details
program_type: ""  # psirt, bug-bounty, security-txt, disclosure-policy
scope: ""  # What's in scope for reporting
safe_harbor: ""  # Safe harbor policy summary

# ID Routing (for platforms hosting multiple programs)
id_routing:
  - pattern: ""           # Regex pattern for program IDs
    system: ""            # Human-readable system name
    url: ""               # URL template with {id} placeholder

# Examples
examples: []

status: active  # active, deprecated, historical
---

# [Namespace Name]

[Brief description of the disclosure program or channel]

## Program

[Description of the vulnerability disclosure program, PSIRT, or bug bounty]

## Reporting

[How to report vulnerabilities — preferred channels, contact info, forms]

## Policy

[Disclosure timeline, safe harbor, scope]

## Resolution

[How to resolve identifiers to URLs]

## Notes

[Caveats, special cases, etc.]
