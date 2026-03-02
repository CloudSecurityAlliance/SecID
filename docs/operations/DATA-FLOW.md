# Registry Data Flow

How registry data moves from this repo (source of truth) to SecID-Service (where it's served to consumers).

**Status: Outline.** Architecture is decided. Implementation details will be confirmed during SecID-Service development.

## The Problem

Registry data is authored and reviewed in this repo (`registry/**/*.json`). SecID-Service needs that data to resolve SecIDs. How does the data get from here to there?

## Current Architecture: Build-Time Embedding

From [INFRASTRUCTURE.md](../reference/INFRASTRUCTURE.md): all registry JSON files are compiled into a single TypeScript object and bundled directly into the Worker.

```
SecID repo                        SecID-Service repo
registry/**/*.json  ──build──→    src/registry.ts  ──wrangler──→  Cloudflare Worker
```

**Why embedding (not runtime fetch):**
- Fast: no external fetch on every request
- Simple: no KV/R2 complexity, no cache invalidation
- Reliable: no dependency on external data availability
- Versioned: registry data version is pinned to the deploy

**Trade-off:** Every registry change requires a Service rebuild and deploy. This is acceptable because registry changes are infrequent (compared to API request volume) and deploys are fast (Cloudflare Workers deploy in seconds).

## The Trigger Question

When someone merges a registry change to this repo, how does SecID-Service know to rebuild?

### Option A: GitHub Actions `repository_dispatch`

A workflow in this repo fires a `repository_dispatch` event to SecID-Service when registry files change.

```
SecID push → "did registry/**/*.json change?" → yes → dispatch to SecID-Service → rebuild + deploy
```

**Pros:** Immediate. Registry changes go live within minutes.
**Cons:** Requires a GitHub token with cross-repo dispatch permissions.

### Option B: Scheduled Rebuild

SecID-Service rebuilds on a schedule (e.g., daily or hourly), pulling latest registry data.

**Pros:** No cross-repo coupling. Simple.
**Cons:** Delay between registry change and it going live. Unnecessary rebuilds when nothing changed.

### Option C: Manual Trigger

Someone manually triggers a Service rebuild after significant registry changes.

**Pros:** Full human control. No automation complexity.
**Cons:** Easy to forget. Doesn't scale.

### Recommendation

**Start with Option A (repository_dispatch) for registry data changes, with Option C as fallback.** The automation is straightforward, the latency is low, and the cross-repo token is the only coordination needed. If the dispatch mechanism proves fragile, fall back to scheduled rebuilds.

## Build Process

In SecID-Service:

1. **Fetch:** Clone or download `registry/**/*.json` from this repo (specific commit or latest main)
2. **Compile:** Merge all JSON files into a single registry object, organized by type → namespace → source
3. **Generate:** Write `src/registry.ts` exporting the compiled object
4. **Bundle:** `wrangler deploy` bundles registry.ts into the Worker

The build script lives in SecID-Service (`scripts/build-registry.ts`). This repo provides the data; Service owns the compilation.

## Version Pinning

**Current plan:** Service always builds from latest main of this repo. The deployed Worker's version effectively includes "SecID registry at commit X".

**Future consideration:** If registry stability becomes important (e.g., for reproducible builds or rollbacks), the Service could pin to a specific commit or tag of this repo. Not needed initially.

## Future: KV Migration

From INFRASTRUCTURE.md: if the registry grows too large to embed in the Worker bundle (Cloudflare Workers have a 10MB limit after compression), migrate to Cloudflare KV.

```
registry/**/*.json  ──build──→  KV namespace  ←──read──  Cloudflare Worker
```

This changes the build process (write to KV instead of generating TypeScript) but not the trigger mechanism. The same `repository_dispatch` pattern works.

**When to migrate:** When the compiled registry exceeds ~5MB (leaving headroom for Worker code). At current scale (100+ namespaces), we're nowhere near this limit.
