# Namespace Migration Mapping: Short Names → Domain Names

This document maps all SecID namespaces from the old short-name format to the new domain-name format.

## Advisory Namespaces

| Old | New | Notes |
|-----|-----|-------|
| `aiaaic` | `aiaaic.org` | AI Incident Database Repository |
| `alibaba` | `alibaba.com` | |
| `apache` | `apache.org` | |
| `apple` | `apple.com` | |
| `atlassian` | `atlassian.com` | |
| `avid` | `avidml.org` | AI Vulnerability Database |
| `aws` | `aws.amazon.com` | |
| `baidu` | `baidu.com` | |
| `cadmv` | `dmv.ca.gov` | California DMV |
| `cert` | `cert.org` | CERT/CC |
| `cisa` | `cisa.gov` | |
| `cisco` | `cisco.com` | |
| `debian` | `debian.org` | |
| `digitalocean` | `digitalocean.com` | |
| `embracethered` | `embracethered.com` | |
| `fda` | `fda.gov` | |
| `fortinet` | `fortinet.com` | |
| `github` | `github.com/advisories` | GHSA; entity stays `github.com` |
| `go` | `go.dev` | Go vulnerability database |
| `google` | `google.com` | |
| `hetzner` | `hetzner.com` | |
| `huawei` | `huawei.com` | |
| `ibm` | `ibm.com` | |
| `linux` | `kernel.org` | Linux kernel security |
| `microsoft` | `microsoft.com` | |
| `mitre` | `mitre.org` | |
| `mozilla` | `mozilla.org` | |
| `nhtsa` | `nhtsa.gov` | |
| `nist` | `nist.gov` | |
| `openssl` | `openssl.org` | |
| `oracle` | `oracle.com` | |
| `ovh` | `ovhcloud.com` | |
| `paloalto` | `paloaltonetworks.com` | |
| `partnershiponai` | `partnershiponai.org` | |
| `protectai` | `protectai.com` | |
| `pypi` | `pypi.org` | |
| `redhat` | `redhat.com` | |
| `rustsec` | `rustsec.org` | |
| `suse` | `suse.com` | |
| `tencent` | `tencent.com` | |
| `ubuntu` | `ubuntu.com` | |
| `vmware` | `vmware.com` | |

## Control Namespaces

| Old | New | Notes |
|-----|-----|-------|
| `advbench` | `github.com/llm-attacks` | AdvBench benchmark |
| `ai2` | `allenai.org` | Allen AI |
| `arc` | `alignment.org` | ARC Evals |
| `biasbench` | `github.com/nyu-mll` | Bias benchmarks collection |
| `cais` | `safe.ai` | Center for AI Safety |
| `cis` | `cisecurity.org` | |
| `concordia` | `concordia-ai.com` | |
| `csa` | `cloudsecurityalliance.org` | |
| `documentation` | `documentation` | Multi-org standards; see notes |
| `eu` | `europa.eu` | EU AI Act controls |
| `google` | `google.com` | SAIF |
| `ieee` | `ieee.org` | |
| `iso` | `iso.org` | |
| `jailbreakbench` | `jailbreakbench.github.io` | |
| `mcpshark` | `mcpshark.sh` | |
| `meta` | `meta.com` | |
| `metr` | `metr.org` | |
| `mlcommons` | `mlcommons.org` | |
| `nist` | `nist.gov` | |
| `openai` | `openai.com` | |
| `owasp` | `owasp.org` | |
| `sac` | `tc260.org.cn` | China Standards Committee |
| `safetybench` | `github.com/thu-coai` | Tsinghua SafetyBench |
| `singapore` | `imda.gov.sg` | Singapore IMDA |
| `trustllm` | `trustllmbenchmark.github.io` | |

## Entity Namespaces

| Old | New | Notes |
|-----|-----|-------|
| `cisco` | `cisco.com` | |
| `csa` | `cloudsecurityalliance.org` | |
| `debian` | `debian.org` | |
| `first` | `first.org` | |
| `github` | `github.com` | |
| `google` | `google.com` | |
| `mcpshark` | `mcpshark.sh` | |
| `microsoft` | `microsoft.com` | |
| `mitre` | `mitre.org` | |
| `nist` | `nist.gov` | |
| `owasp` | `owasp.org` | |
| `paperpile` | `paperpile.com` | |
| `redhat` | `redhat.com` | |

## Reference Namespaces

| Old | New | Notes |
|-----|-----|-------|
| `acm` | `acm.org` | |
| `aisi` | `aisi.gov.uk` | AI Safety Institutes (UK-led) |
| `arxiv` | `arxiv.org` | |
| `asin` | `amazon.com` | Amazon Standard ID Number |
| `dblp` | `dblp.org` | |
| `doi` | `doi.org` | |
| `iacr` | `iacr.org` | |
| `ieee` | `ieee.org` | |
| `ietf` | `ietf.org` | |
| `isbn` | `isbn.org` | |
| `issn` | `issn.org` | |
| `ndss` | `ndss-symposium.org` | |
| `openalex` | `openalex.org` | |
| `pubmed` | `nih.gov` | NIH/NLM PubMed |
| `semanticscholar` | `semanticscholar.org` | |
| `ssrn` | `ssrn.com` | |
| `techrxiv` | `techrxiv.org` | |
| `ukgov` | `gov.uk` | UK Government reports |
| `usenix` | `usenix.org` | |
| `whitehouse` | `whitehouse.gov` | |
| `zenodo` | `zenodo.org` | |

## Regulation Namespaces

| Old | New | Notes |
|-----|-----|-------|
| `eu` | `europa.eu` | |
| `us` | `govinfo.gov` | US federal law |
| `us-ca` | `ca.gov` | California |
| `us-ny` | `ny.gov` | New York |

## TTP Namespaces

| Old | New | Notes |
|-----|-----|-------|
| `lockheed` | `lockheedmartin.com` | Cyber Kill Chain |
| `mitre` | `mitre.org` | ATT&CK, CAPEC, ATLAS |
| `unifiedkillchain` | `unifiedkillchain.com` | |
| `veris` | `veriscommunity.net` | VERIS Framework |

## Weakness Namespaces

| Old | New | Notes |
|-----|-----|-------|
| `anthropic` | `anthropic.com` | |
| `avid` | `avidml.org` | |
| `biml` | `berryvilleiml.com` | Berryville IML |
| `enisa` | `enisa.europa.eu` | EU Agency for Cybersecurity |
| `gpai` | `gpai.ai` | Global Partnership on AI |
| `ibm` | `ibm.com` | |
| `mit` | `mit.edu` | MIT AI Risk Repository |
| `mitre` | `mitre.org` | CWE |
| `mlcommons` | `mlcommons.org` | |
| `nist` | `nist.gov` | |
| `oecd` | `oecd.org` | |
| `owasp` | `owasp.org` | |
| `stanford` | `stanford.edu` | Stanford CRFM |

## Deferred Namespaces

| Old | New | Notes |
|-----|-----|-------|
| `_deferred/cti/actor` | TBD | Deferred type |
| `_deferred/cti/campaign` | TBD | Deferred type |
| `_deferred/cti/malware` | TBD | Deferred type |

## Special Cases

### `documentation` (control)
Multi-org documentation standards (Model Cards from Google, Datasheets from Microsoft, System Cards from various). No single domain owner. Kept as `documentation` pending restructuring into per-org namespaces.

### `github` (advisory → `github.com/advisories`)
GitHub's advisory database (GHSA) becomes a platform sub-namespace `github.com/advisories`, while the entity remains `github.com`.

### `aisi` (reference → `aisi.gov.uk`)
Covers AI Safety Institutes from UK, US, Japan. Uses UK AISI domain since UK was first and hosts the primary website. May be restructured into per-country namespaces in the future.
