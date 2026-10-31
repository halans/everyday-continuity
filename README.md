# Everyday Continuity

An independent, conflict-focused civilian preparedness website for Australia. Reference edition: 29 October 2026. This is a new standalone project; it does not import, modify, deploy over, or depend on the user's separate general emergency site.

## Layout

```
public/    The public asset. Deploy this directory and nothing else.
  index.html                    complete self-contained website (generated)
  sitemap.xml, robots.txt       for search engines (generated)
  llms.txt, llms-full.txt       for AI agents and answer engines (generated)
  og-image.png                  link-preview image (static, rendered from src/og-image.html)
src/       Editable source
  content.json                  source of truth: site URL, sources, checklist, guides, quick answers
  template.html                 design, safety articles and application logic
  og-image.html                 source for og-image.png
build.py   Dependency-free build: src/ -> public/
test.py    22 dependency-free build/content contract tests; JavaScript syntax check uses Node
docs/      QA.md (browser test observations), SOURCE-NOTES.md (source limits), TEST-RESULTS.txt (captured test run)
```

Everything in `public/` except `og-image.png` is rebuilt by `build.py`; edit only `src/`.

## Run and rebuild

No npm install, package manager, CDN, API key or network connection is required. Python 3 and Node are only needed for rebuilding/testing, not for visitors.

```
python3 build.py
python3 test.py
```

Actual build output from this edition:

```
Built public/: index.html, sitemap.xml, robots.txt, llms.txt, llms-full.txt
```

The current test run passes all 22 checks. docs/TEST-RESULTS.txt is an older record. Rebuilding index.html twice produces identical bytes for the same template and content.

For local development, opening public/index.html directly works. Alternatively:

```
python3 -m http.server 8000 --directory public
```

## Deploy as a separate site

Create a NEW static-site project on your chosen host. Do not upload this project into an existing emergency-site project unless you deliberately want to replace it.

For Cloudflare Pages Direct Upload, create a new Pages project and upload the `public/` folder. No build command, server function, routing configuration or backend is required. The site is intended to live at https://prepper.downunder.blue/. That address is set once, as `siteUrl` in `src/content.json`, and the build writes it into the canonical link, link-preview tags, structured data, sitemap, robots.txt and llms.txt. If the address changes, edit `siteUrl` (it must start with https:// and end with /), rebuild, and regenerate `og-image.png` if you want the new address on the preview card. The host's domain and DNS settings are not configured by this project.

For other static hosts, publish public/index.html at the site root. This is a single-page anchor-navigation site, not a multi-page CMS. No redirects are needed. Do not add infrastructure-reserved application routes such as /run, /events or /health.

## Features

- Responsive layout with all navigation and tools retained on phones.
- 18-item checklist with local-browser persistence when available.
- 1–30-person water calculator with 3-, 7- and 14-day horizons.
- Print stylesheet produces a household worksheet with blank paper contact fields.
- Plain-text download includes current checked tasks, calculator settings and source URLs.
- Five keyboard-navigable disruption tabs: power/comms, water, food/payments/fuel, cyber/information, overseas family.
- Filterable official source directory with visible geographic and subject-matter scope.
- No accounts, analytics, tracking, external assets, live feeds or runtime network requests.

## Design and motion

Large display type, a pill header that becomes a full-screen menu on phones, and a page tone that fades between dark and light as each section scrolls into view. Section text lights up word by word, content rises into place, cards stack as you scroll, and the household checklist keeps the water calculator pinned beside it.

- Scroll effects use native CSS scroll-driven animations where the browser supports them (current Chrome, Edge and Safari). Other browsers get a one-off fade-in from an IntersectionObserver instead. Scrolling itself is never hijacked.
- `prefers-reduced-motion` turns all movement off and shows everything immediately. With JavaScript off, the text sections still read normally.
- No fonts, images, libraries or network requests. Type is the system sans-serif stack (Archivo first, if installed). To change the colours, edit the `:root` and `html[data-tone=dark]` variables at the top of the stylesheet in `src/template.html`.

## Search and AI discovery

- **Social account:** the Bluesky link is `social` in `src/content.json`. It appears in the footer, as `sameAs` in the structured data and in `llms.txt`.
- **Head tags:** title, description, robots, canonical, `hreflang`, Open Graph and Twitter card tags, and an inline icon. Title and description are set in `build.py`.
- **Structured data:** JSON-LD for the site, the page (with every official source as a citation) and a `FAQPage`. The FAQ is the visible Quick answers section, written in `src/content.json` under `faq`, so the page and the structured data cannot disagree. A test checks this.
- **Plain HTML for crawlers:** the checklist, guides and source list are drawn by JavaScript for visitors, and also written into the page as plain lists (inside `<noscript>`), so crawlers, AI agents and visitors without JavaScript can read them.
- **llms.txt and llms-full.txt:** a short summary with the key facts and links, and the whole guide as plain text. Both are generated from `content.json`.
- **sitemap.xml and robots.txt:** one URL, dated from the review date. Everything is allowed.
- **Link-preview image:** `public/og-image.png` (1200 by 630) is typography only. To change it, edit `src/og-image.html` and render it at 1200 by 630 with a headless browser.

When you change the review date in `content.json`, the sitemap, structured data and llms files pick it up on the next build. Check the facts before changing that date.

## Storage and privacy

Only checked task IDs and calculator people/day values are stored under `civil-ready-au-v1` in localStorage. The site does not ask for names, addresses, contact numbers, health details or locations. Data is not transmitted.

Storage may be unavailable in sandbox previews, private browsing, or under file:// restrictions. The site detects failure and displays a session-only notice. Printing/downloading remains available, subject to browser permissions. No persistence guarantee is made for the Hyperagent preview.

Printed/downloaded worksheets can contain sensitive details when a household fills them in later. Store them securely. Downloads and browser print dialogs depend on the visitor's browser and may be restricted inside embeds; standalone hosting is the preferred production experience.

## Offline behaviour

Once downloaded, public/index.html needs no network access for its layout, calculator, checklist, tabs, source filter, print styling or text generation. External official links still need a connection; their full third-party pages are not mirrored.

The page uses a system sans-serif stack with optional locally installed Archivo/Inter, avoiding remote font dependencies. Text and source content are authored locally; no upstream dataset must be fetched to rebuild.

## Editing safely

1. Edit sources/checklist/scenarios in src/content.json. Keep IDs unique.
2. Edit context, warnings, safety copy, styling or behaviour in src/template.html.
3. Run build.py then test.py.
4. Test calculator, tabs, filters, print and download in a browser at desktop and phone widths.
5. Review source scope and currency before changing the review date.
6. Deploy the rebuilt public/ directory or deployment ZIP to the separate site.

Add a source before making a new authoritative factual claim. Do not edit generated public/index.html directly: the next build will replace it.

When publishing an update to the existing Hyperagent artifact, use artifact ID cmvte97t10gx507ad22rvzcmj with the version you opened, rather than creating a new artifact. First published artifact version: 1.

## Editorial boundaries

This is educational civilian preparedness, not government advice, a live warning service, a prediction of war, a tactical manual or medical advice. It does not identify likely targets or invent shelter locations. No military operations or weapons instructions are included.

Three/seven/fourteen-day horizons are planning choices, not a nationwide wartime directive. Queensland and NSW guidance is identified as jurisdiction-specific and originally general emergency guidance. Policy announcements and inquiries are distinguished from operational capabilities. See SOURCE-NOTES.md.

## QA scope

Automated checks cannot establish the accuracy of changing government advice or certify household safety. Browser tests are documented in QA.md. Print/download logic and styling exist; no physical paper print or particular visitor browser's file-save behaviour is guaranteed.

## Branding update — 31 October 2026

Renamed from Civil Ready Australia to Everyday Continuity. Tagline: Keep everyday life working. The palette is deep teal, white and restrained blue, with a pale aqua diagram accent. Conflict-related civilian preparedness remains the purpose. Source review dates are still 29 October 2026: this was a branding update, not a new research pass. The internal directory name and civil-ready-au-v1 storage key are retained for compatibility; visitors’ saved planning choices are not intentionally discarded.

Revised packages use everyday-continuity filenames. Publish updates to the same artifact ID; the brand-update publication is version 2.
