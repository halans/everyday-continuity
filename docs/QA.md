# QA observations — 29 October 2026

## Build and content contracts

17/17 checks passed using python3 test.py. See TEST-RESULTS.txt for the actual captured run. Checks include unique IDs, resolving source references, data embedding equivalence, offline runtime dependencies, Node JavaScript syntax, offline text completeness, checksums, deployment ZIP contents and deterministic HTML rebuilding.

## Published render

Published preview, version 1. A page-health check returned healthy, no console errors and no failed requests. Desktop hero screenshot visually inspected at 1280px: clear typography and spacing, no overlap/clipping.

## Interactive browser

Actual browser action: clicked Build your household plan; the planner/checklist was visible.
Actual browser action: filled People in your household with 4; calculator showed 36 L for three days.

18/18 browser assertions passed:

- 18 checkbox tasks rendered.
- 20 source cards rendered.
- Four people / three days = 36 L.
- Four people / seven days = 84 L.
- Checking a task updates count to 1/18.
- Unchecking restores 0/18.
- Each of five tabs exposes exactly its matching panel.
- Policy-source filter displays three cards.
- All-source filter restores 20 cards.
- External source anchors use safe new-tab attributes.
- All in-page anchors have targets.
- Download text contains every source-of-truth checklist entry.
- Download text contains every source URL.
- Desktop has no horizontal overflow.

Calculator settings and tasks were reset to defaults after tests.

## Responsive browser layout

Real browser nested browsing contexts were created at widths 320, 390, 768 and 1280px, height 844px. Because the preview sandbox's origins prevent direct iframe DOM access, each context reported its own geometry using postMessage. All widths passed:

| Context width | Document scroll width | Horizontal overflow | All six nav links inside bounds | Tasks | Tabs |
|---|---:|---|---|---:|---:|
| 320 | 315 | None | Yes | 18 | 5 |
| 390 | 375 | None | Yes | 18 | 5 |
| 768 | 753 | None | Yes | 18 | 5 |
| 1280 | 1265 | None | Yes | 18 | 5 |

Mobile screenshot capture of the nested context returned blank and was not treated as visual evidence. Phone layout validation is based on the real responsive browsing-context geometry/DOM checks above; a physical phone visual/touch test has not been performed.

## Known environmental limits

The sandboxed preview blocked localStorage. The fallback notice rendered correctly and interactions remained functional. Persistent-storage behaviour on a separately hosted first-party origin was not verified in this preview.

An attempt to install a local browser testing package was blocked by registry access (403); no dependency was added to the project. Existing browser tools were used instead.

Print stylesheet inspected in source; no physical paper print made. Download text equivalence tested; visitor browser download/save permissions depend on host/embed settings. No blanket assistive-technology conformance certification is claimed.

## Branding revision — 31 October 2026

Preview updated in place to version 2: Everyday Continuity. All 18 build/content tests passed (including a new branding consistency test). Render health check healthy with no console errors or failed requests. Desktop screenshot visually inspected: revised masthead, teal-blue palette, headline and navigation fit without overlap.

Real browser responsive-context checks at 320, 390, 768 and 1280px all passed: no horizontal overflow, all navigation links inside bounds, revised brand inside bounds. Browser assertions confirmed the old visible name is absent, the text worksheet has the new brand and all 18 planning tasks remain. Source review date deliberately remains 29 October 2026; this was not a source-refresh task.
