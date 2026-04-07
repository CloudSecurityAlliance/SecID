# SecID Plugin

Local Claude Code plugin for resolving security identifiers. Provides three MCP tools (resolve, lookup, describe) by calling the SecID REST API.

## Three Ways to Use SecID

| Option | Best for | Setup |
|--------|----------|-------|
| **Remote MCP server** | Simplest — nothing to install | Add `https://secid.cloudsecurityalliance.org/mcp` as a remote MCP server |
| **This plugin** | Local install, internal resolvers, offline config | Install plugin, runs `server.py` locally |
| **REST API directly** | Building apps, scripts, integrations | `GET https://secid.cloudsecurityalliance.org/api/v1/resolve?secid=...` |
| **Client SDKs** | Python, TypeScript, Go libraries | [SecID-Client-SDK](https://github.com/CloudSecurityAlliance/SecID-Client-SDK) |

**Use the remote MCP server** unless you need to point to an internal resolver or want local control. The plugin and the remote MCP server provide the same three tools with the same results.

## Install

```bash
pip install mcp httpx
```

## Usage

The plugin runs a local MCP server that calls the public SecID API. Three tools:

- **resolve** — resolve a full SecID string to URLs and data
- **lookup** — look up by type + identifier (constructs the SecID for you)
- **describe** — browse types, namespaces, and sources

## Internal Resolvers

To point to an internal SecID resolver instead of (or in addition to) the public one:

```bash
python3 server.py --base-url https://internal-secid.example.org
```

Or edit `.mcp.json`:

```json
{
  "mcpServers": {
    "secid": {
      "command": "python3",
      "args": ["${CLAUDE_PLUGIN_ROOT}/server.py", "--base-url", "https://internal-secid.example.org"]
    }
  }
}
```

## Links

- **Live service:** [secid.cloudsecurityalliance.org](https://secid.cloudsecurityalliance.org/)
- **Remote MCP server:** `https://secid.cloudsecurityalliance.org/mcp`
- **REST API:** `GET https://secid.cloudsecurityalliance.org/api/v1/resolve?secid=...`
- **Spec + Registry:** [github.com/CloudSecurityAlliance/SecID](https://github.com/CloudSecurityAlliance/SecID)
- **Service source:** [github.com/CloudSecurityAlliance/SecID-Service](https://github.com/CloudSecurityAlliance/SecID-Service)
- **Client SDKs:** [github.com/CloudSecurityAlliance/SecID-Client-SDK](https://github.com/CloudSecurityAlliance/SecID-Client-SDK)
