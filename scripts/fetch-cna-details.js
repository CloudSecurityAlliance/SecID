#!/usr/bin/env node
// Fetches detail pages for all CVE CNA partners using Playwright.
// Run: npx playwright test --config=playwright.config.js scripts/fetch-cna-details.js
// Or simply: node scripts/fetch-cna-details.js (requires playwright installed)
//
// Outputs: working-data/cna/partner-details.json
// Depends on: seed/cve-cna-partners-raw.json (from the initial table scrape)

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const SEED_FILE = path.join(__dirname, '..', 'seed', 'cve-cna-partners-raw.json');
const OUTPUT_FILE = path.join(__dirname, '..', 'working-data', 'cna', 'partner-details.json');
const DELAY_MS = 1500; // polite delay between requests

// Extraction function run inside the browser
function extractPartnerDetail() {
  const main = document.querySelector('main') || document.body;
  const result = {};

  // Partner name from h1
  const h1 = main.querySelector('h1');
  result.partner = h1 ? h1.textContent.trim() : null;

  // Step 1: Disclosure policy links
  // Step 2: Contact links (emails, forms, pages)
  result.policy_urls = [];
  result.contacts = [];
  result.contact_pages = [];

  const allLinks = main.querySelectorAll('a');
  for (const a of allLinks) {
    const href = a.href;
    const text = a.textContent.trim();
    if (!href) continue;

    if (href.startsWith('mailto:')) {
      result.contacts.push({
        type: 'email',
        label: text,
        value: href.replace('mailto:', '')
      });
    } else if (text === 'View Policy' || text.toLowerCase().includes('policy')) {
      result.policy_urls.push({ text, url: href });
    } else if (text.toLowerCase().includes('contact page') || text.toLowerCase().includes('security contact')) {
      result.contact_pages.push({ text, url: href });
    } else if (text === 'View Advisories') {
      result.advisories_url = href;
    }
  }

  // Table data with structured scope parsing
  const rows = main.querySelectorAll('table tr');
  result.table = {};
  for (const row of rows) {
    const th = row.querySelector('th');
    const td = row.querySelector('td');
    if (!th || !td) continue;

    const key = th.textContent.trim();

    if (key === 'Scope') {
      // Parse structured scope with <strong> labels
      const container = td.querySelector('div') || td;
      const strongs = container.querySelectorAll('strong');
      if (strongs.length > 0) {
        const scopes = {};
        let currentLabel = null;
        for (const node of container.childNodes) {
          if (node.tagName === 'STRONG') {
            currentLabel = node.textContent.trim().replace(/:$/, '');
          } else if (currentLabel && node.textContent.trim()) {
            scopes[currentLabel] = (scopes[currentLabel] || '') + node.textContent.trim();
          }
        }
        result.table[key] = Object.keys(scopes).length > 0 ? scopes : td.textContent.trim();
      } else {
        result.table[key] = td.textContent.trim();
      }
    } else if (key === 'Program Role') {
      const lis = td.querySelectorAll('li');
      result.table[key] = lis.length > 0
        ? Array.from(lis).map(li => li.textContent.trim())
        : [td.textContent.trim()];
    } else if (key === 'Organization Type') {
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

async function main() {
  // Load seed data
  const seed = JSON.parse(fs.readFileSync(SEED_FILE, 'utf8'));
  const partners = seed.partners;
  console.log(`Loaded ${partners.length} partners from seed data`);

  // Load existing results for resume support
  let results = {};
  if (fs.existsSync(OUTPUT_FILE)) {
    try {
      const existing = JSON.parse(fs.readFileSync(OUTPUT_FILE, 'utf8'));
      results = existing.partners || {};
      console.log(`Resuming: ${Object.keys(results).length} already fetched`);
    } catch (e) {
      console.log('Could not load existing results, starting fresh');
    }
  }

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    userAgent: 'SecID-Registry-Research/1.0 (https://github.com/CloudSecurityAlliance/SecID)'
  });
  const page = await context.newPage();

  let fetched = 0;
  let skipped = 0;
  let failed = 0;

  for (let i = 0; i < partners.length; i++) {
    const p = partners[i];
    const slug = p.partner_url.split('/partner/').pop();

    // Skip if already fetched
    if (results[slug]) {
      skipped++;
      continue;
    }

    process.stdout.write(`[${i + 1}/${partners.length}] ${slug} ... `);

    try {
      await page.goto(p.partner_url, { waitUntil: 'networkidle', timeout: 15000 });
      // Wait for table to render
      await page.waitForSelector('table', { timeout: 10000 });

      const detail = await page.evaluate(extractPartnerDetail);
      results[slug] = {
        ...detail,
        slug,
        source_url: p.partner_url,
        fetched_at: new Date().toISOString()
      };
      fetched++;
      console.log('OK');
    } catch (e) {
      console.log(`FAILED: ${e.message.slice(0, 80)}`);
      failed++;
    }

    // Save progress every 25 pages
    if (fetched % 25 === 0) {
      const output = {
        scraped_at: new Date().toISOString(),
        source: 'https://www.cve.org/PartnerInformation/ListofPartners',
        total_fetched: Object.keys(results).length,
        partners: results
      };
      fs.writeFileSync(OUTPUT_FILE, JSON.stringify(output, null, 2));
    }

    await new Promise(r => setTimeout(r, DELAY_MS));
  }

  // Final save
  const output = {
    scraped_at: new Date().toISOString(),
    source: 'https://www.cve.org/PartnerInformation/ListofPartners',
    total_fetched: Object.keys(results).length,
    partners: results
  };
  fs.writeFileSync(OUTPUT_FILE, JSON.stringify(output, null, 2));

  await browser.close();
  console.log(`\nDone: ${fetched} fetched, ${skipped} skipped, ${failed} failed`);
}

main().catch(e => { console.error(e); process.exit(1); });
