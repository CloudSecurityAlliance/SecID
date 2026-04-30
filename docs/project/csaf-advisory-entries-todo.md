# TODO: Add CSAF Provider Advisory Entries

**Date:** 2026-04-30
**Priority:** High
**Context:** 19 CSAF providers identified worldwide. Need advisory registry entries for each.

## What Needs Doing

Add CSAF provider metadata URL as a source in advisory registry entries. For providers without advisory entries, create new ones.

### Already have advisory entries (5) — add CSAF source:

| Provider | Advisory entry | CSAF metadata URL |
|----------|---------------|-------------------|
| CISA | `registry/advisory/gov/cisa.json` | `https://www.cisa.gov/sites/default/files/csaf/provider-metadata.json` |
| Cisco PSIRT | `registry/advisory/com/cisco.json` | `https://www.cisco.com/.well-known/csaf/provider-metadata.json` |
| Huawei PSIRT | `registry/advisory/com/huawei.json` | `https://www.huawei.com/.well-known/csaf/provider-metadata.json` |
| Microsoft MSRC | `registry/advisory/com/microsoft.json` | `https://msrc.microsoft.com/csaf/provider-metadata.json` |
| Red Hat | `registry/advisory/com/redhat.json` | `https://security.access.redhat.com/data/csaf/v2/provider-metadata.json` |

### Need new advisory entries (14):

| Provider | Namespace | CSAF metadata URL | Country |
|----------|-----------|-------------------|---------|
| ABB PSIRT | abb.com | `https://psirt.abb.com/.well-known/csaf/provider-metadata.json` | CH |
| BSI / CERT-Bund | cert-bund.de | `https://wid.cert-bund.de/.well-known/csaf/provider-metadata.json` | DE |
| Hitachi Energy PSIRT | hitachienergy.com | via CERT-Bund aggregator | CH |
| IDS Innomic | innomic.com | `https://www.innomic.com/.well-known/csaf/provider-metadata.json` | DE |
| Intevation GmbH | intevation.de | `https://intevation.de/.well-known/csaf/provider-metadata.json` | DE |
| KUNBUS PSIRT | kunbus.com | `https://psirt.kunbus.com/.well-known/csaf/provider-metadata.json` | DE |
| Nozomi Networks | nozominetworks.com | `https://csaf.data.security.nozominetworks.com/provider-metadata.json` | US |
| Open-Xchange GmbH | open-xchange.com | `https://www.open-xchange.com/.well-known/csaf/provider-metadata.json` | DE |
| Schneider Electric | se.com | `https://www.se.com/.well-known/csaf/provider-metadata.json` | FR |
| SICK PSIRT | sick.com | `https://www.sick.com/.well-known/csaf/provider-metadata.json` | DE |
| Siemens ProductCERT | siemens.com | `https://cert-portal.siemens.com/productcert/csaf/provider-metadata.json` | DE |
| Stackable | stackable.tech | `https://advisories.stackable.tech/.well-known/csaf/provider-metadata.json` | DE |
| SUSE | suse.de | `https://suse.de/.well-known/csaf/provider-metadata.json` | DE |
| TIBCO PSIRT | tibco.com | `https://tibco.com/.well-known/csaf/provider-metadata.json` | US |

### How to add CSAF to an advisory entry

Add a `csaf` source as a new match_node or as a URL on an existing source. The CSAF provider-metadata.json URL should be in the source-level `urls` array with `"type": "csaf_provider"` and the format metadata fields:

```json
{
  "type": "csaf_provider",
  "url": "https://www.cisco.com/.well-known/csaf/provider-metadata.json",
  "parsability": "structured",
  "schema": "secid:reference/oasis-open.org/csaf@2.0",
  "notes": "CSAF trusted provider. Advisory directory at .well-known/csaf/"
}
```

### Data source

Complete CSAF provider database at:
`~/GitHub/CloudSecurityAlliance-DataSets/dataset-private-website-files/docs/csaf-providers.json`
