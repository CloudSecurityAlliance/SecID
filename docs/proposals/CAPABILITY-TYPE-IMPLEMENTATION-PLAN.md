# Capability Type Implementation Plan

Implements the `capability` type as the 9th SecID type, plus adds the previously-missing `disclosure` type to the Client SDKs.

## Repos Affected

| Repo | Changes |
|------|---------|
| **SecID** (spec + registry) | SPEC.md, type definition, registry template, CLAUDE.md, README.md, type-level JSON |
| **SecID-Service** | SECID_TYPES, MCP descriptions, website, KV upload, deploy |
| **SecID-Client-SDK** | Python, TypeScript, Go — type lists, docs, examples |

## Phase 1: Spec + Registry (SecID repo)

### 1.1 Update SPEC.md
- Add `capability` to the type list (Section 1, type table)
- Add `capability` component description
- Add capability examples to the format examples

### 1.2 Create type definition files
- Create `registry/capability.md` — type description (purpose, identifier format, namespaces, notes)
- Create `registry/capability.json` — type-level JSON (description, purpose, format, examples, empty namespaces array)
- Create `registry/capability/_template.md` — template for new capability namespace files

### 1.3 Update documentation
- CLAUDE.md — add capability to type table, update type count from 8 to 9
- README.md — add capability to type table, update type count, add capability examples
- PRINCIPLES.md — no changes needed (principles are type-agnostic)
- docs/reference/REGISTRY-JSON-FORMAT.md — add capability-specific data fields (configuration, audit, remediation, iac)
- docs/reference/DATA-HOSTING-RULES.md — note capability as largest V2 data type

### 1.4 Update counts
- Run `./scripts/update-counts.sh`

### 1.5 Initial proof-of-concept registry entries
- `registry/capability/com/amazon/aws.json` — 3-5 well-known capabilities (S3 encryption, CloudTrail multi-region, IAM MFA root)
- Validates the pattern before scaling

## Phase 2: Service Update (SecID-Service repo)

### 2.1 Add capability to SECID_TYPES
- `src/types.ts` — add `"capability"` to SECID_TYPES array

### 2.2 Update MCP tool descriptions
- `src/mcp.ts` — add capability examples to resolve, lookup, describe tool descriptions
- Add CAPABILITY section explaining: "Use type=capability to find specific product security features with configuration options and CLI/API commands"
- Update registry resource description (9 types, new count)
- Update TYPE_DESCRIPTIONS in website explorer

### 2.3 Update website
- `website/src/pages/index.astro` — "Nine Types of Security Knowledge" with capability card
- Update namespace counts
- Add capability example to resolver examples

### 2.4 Upload and deploy
- Re-upload KV with capability type data
- Deploy worker

### 2.5 Tests
- Add parser test for capability type
- Update MCP resource count test

## Phase 3: Client SDK Update (SecID-Client-SDK repo)

### 3.1 Python SDK
- `secid_client.py` — update lookup() type docstring to include `disclosure` and `capability`
- `README.md` — add disclosure and capability examples
- `test_secid_client.py` — add capability test case

### 3.2 TypeScript SDK
- `src/secid-client.ts` — update lookup() type docstring
- `README.md` — add disclosure and capability examples
- Add type definition for SecIDType if one exists

### 3.3 Go SDK
- `secid.go` — update Lookup() type documentation
- Add capability example to package doc

### 3.4 Tests
- `tests/` directory — add cross-SDK capability tests

## Phase 4: Registry Population (future, after pattern is validated)

### 4.1 AWS capabilities
- Extract from AWS documentation and CIS AWS Benchmark
- Start with top 20 services by security relevance (S3, IAM, CloudTrail, EC2, RDS, Lambda, KMS, VPC, EBS, CloudFront, ECS, EKS, SNS, SQS, DynamoDB, API Gateway, WAF, GuardDuty, SecurityHub, Config)

### 4.2 Azure capabilities
- Extract from Azure documentation and CIS Azure Benchmark

### 4.3 GCP capabilities
- Extract from GCP documentation and CIS GCP Benchmark

### 4.4 DISA STIGs
- Parse XCCDF XML into per-check capability entries
- Public domain — no licensing concerns

## Execution Order

1. **SecID repo first** — spec changes, registry files, docs (everything else depends on this)
2. **SecID-Service second** — type recognition, MCP descriptions, website, deploy
3. **SecID-Client-SDK third** — SDK updates reference the live service
4. **Registry population fourth** — proof of concept, then scale

Phases 1-3 can be done in one session. Phase 4 is ongoing work.

## Open Questions for Implementation

1. **Sub-namespace depth for cloud services** — `amazon.com/aws/s3` is 3 levels. Do we need `amazon.com/aws/s3/encryption` or is `amazon.com/aws/s3#default-encryption` sufficient? Proposal: keep the service as the name, features as subpath. Consistent with how other types work.

2. **Capability-specific JSON fields** — need to formalize: `configuration` (options, defaults), `audit` (cli, api, console, expected), `remediation` (cli, api, console, iac). These are unique to capability type.

3. **Relationship to CIS Benchmarks** — CIS Benchmark checks reference capabilities. Should the capability entry include `checked_by` references, or should that be relationship-layer data? Proposal: include in V2 data, not in registry.
