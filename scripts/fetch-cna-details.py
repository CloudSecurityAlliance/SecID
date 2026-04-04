#!/usr/bin/env python3
"""Fetch detail pages for all CVE CNA partners using Playwright.

Run from repo root: python3 scripts/fetch-cna-details.py

Outputs: working-data/cna/partner-details.json
Depends on: seed/cve-cna-partners-raw.json (from the initial table scrape)
"""

import json
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

SEED_FILE = Path("seed/cve-cna-partners-raw.json")
OUTPUT_FILE = Path("working-data/cna/partner-details.json")
DELAY_S = 1.0  # polite delay between requests

# JS extraction function
EXTRACT_JS = """
() => {
  const main = document.querySelector('main') || document.body;
  const result = {};

  const h1 = main.querySelector('h1');
  result.partner = h1 ? h1.textContent.trim() : null;

  // Links from the steps nav section
  result.policy_urls = [];
  result.contacts = [];
  result.contact_pages = [];
  result.advisories_url = null;
  result.other_links = [];

  const allLinks = main.querySelectorAll('a');
  for (const a of allLinks) {
    const href = a.href;
    const text = a.textContent.trim();
    if (!href || !text) continue;
    if (href.startsWith('mailto:')) {
      result.contacts.push({ type: 'email', label: text, value: href.replace('mailto:', '') });
    } else if (text === 'View Policy') {
      result.policy_urls.push({ text, url: href });
    } else if (text.toLowerCase().includes('contact')) {
      result.contact_pages.push({ text, url: href });
    } else if (text === 'View Advisories') {
      result.advisories_url = href;
    } else if (href.includes('cve.org/PartnerInformation')) {
      // Skip internal CVE partner links (Top-Level Root references)
    } else {
      result.other_links.push({ text, url: href });
    }
  }

  // Table data
  const rows = main.querySelectorAll('table tr');
  result.table = {};
  for (const row of rows) {
    const th = row.querySelector('th');
    const td = row.querySelector('td');
    if (!th || !td) continue;
    const key = th.textContent.trim();

    if (key === 'Scope') {
      const container = td.querySelector('div') || td;
      const strongs = container.querySelectorAll('strong');
      if (strongs.length > 0) {
        const scopes = {};
        let cur = null;
        for (const node of container.childNodes) {
          if (node.tagName === 'STRONG') {
            cur = node.textContent.trim().replace(/:$/, '');
          } else if (cur && node.textContent.trim()) {
            scopes[cur] = (scopes[cur] || '') + node.textContent.trim();
          }
        }
        result.table[key] = Object.keys(scopes).length > 0 ? scopes : td.textContent.trim();
      } else {
        result.table[key] = td.textContent.trim();
      }
    } else if (key === 'Program Role' || key === 'Organization Type') {
      const lis = td.querySelectorAll('li');
      result.table[key] = lis.length > 0
        ? Array.from(lis).map(li => li.textContent.trim())
        : [td.textContent.trim()];
    } else if (key === 'Top-Level Root' || key === 'Root') {
      const link = td.querySelector('a');
      result.table[key] = {
        name: td.textContent.trim(),
        url: link ? link.href : null
      };
    } else {
      result.table[key] = td.textContent.trim();
    }
  }

  return result;
}
"""


def main():
    seed = json.loads(SEED_FILE.read_text())
    partners = seed["partners"]
    print(f"Loaded {len(partners)} partners from seed data")

    # Resume support
    results = {}
    if OUTPUT_FILE.exists():
        try:
            existing = json.loads(OUTPUT_FILE.read_text())
            results = existing.get("partners", {})
            print(f"Resuming: {len(results)} already fetched")
        except Exception:
            print("Could not load existing results, starting fresh")

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="SecID-Registry-Research/1.0 (https://github.com/CloudSecurityAlliance/SecID)"
        )
        page = context.new_page()

        fetched = 0
        skipped = 0
        failed = 0

        for i, partner in enumerate(partners):
            slug = partner["partner_url"].split("/partner/")[-1]

            if slug in results:
                skipped += 1
                continue

            sys.stdout.write(f"[{i+1}/{len(partners)}] {slug} ... ")
            sys.stdout.flush()

            try:
                page.goto(partner["partner_url"], wait_until="networkidle", timeout=15000)
                page.wait_for_selector("table", timeout=10000)
                detail = page.evaluate(EXTRACT_JS)
                results[slug] = {
                    **detail,
                    "slug": slug,
                    "source_url": partner["partner_url"],
                    "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                }
                fetched += 1
                print("OK")
            except Exception as e:
                print(f"FAILED: {str(e)[:80]}")
                failed += 1

            # Save every 25
            if fetched > 0 and fetched % 25 == 0:
                _save(results)
                print(f"  [saved checkpoint: {len(results)} total]")

            time.sleep(DELAY_S)

        browser.close()

    _save(results)
    print(f"\nDone: {fetched} fetched, {skipped} skipped, {failed} failed")
    print(f"Total: {len(results)} partner details in {OUTPUT_FILE}")


def _save(results):
    output = {
        "scraped_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "source": "https://www.cve.org/PartnerInformation/ListofPartners",
        "total_fetched": len(results),
        "partners": results,
    }
    OUTPUT_FILE.write_text(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
