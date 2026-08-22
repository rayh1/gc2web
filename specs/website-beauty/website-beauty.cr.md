---
slug: website-beauty
source: specs/website-beauty/website-beauty.prd.md
---

# Website visual refresh — verify and close gaps

## 1. Intent

Bring the site's visual refresh into verified conformance with its own requirements. The
redesign described by the PRD and DD (warm family-archive identity, homepage orientation,
entity grouping, richer result cards, breadcrumb navigation) was substantially implemented
outside any pipeline and never reviewed against its acceptance criteria.
<!-- from CR:prd#Context; CR:dd#Technical-Approach -->
<!-- observed: git log ce6ae552..HEAD — redesign landed from commit 9d8f11e "Improve website."; no build report or review exists in specs/website-beauty/ -->
This change request re-states the requirements against the current tree, verifies them, and
closes the gaps found — known at authoring time: the DD's cohesion e2e coverage was never
created, and the homepage e2e test fails against the shipped homepage.
<!-- observed: ls tests/e2e/ 2026-08-21 — no visual-refresh.spec.ts; `npx playwright test` 2026-08-21: 12 passed, 1 failed — homepage.spec.ts expects a heading /een warme ingang/i the built homepage does not render -->

## 2. Functional requirements

[R-1] **The homepage, shared navigation, search pages, and entity pages present one cohesive
warm family-archive visual system.**
<!-- from CR:prd#R-1 -->
- AC: The shared page shells and page files for all four surface types consume the shared
  archive token/utility layer (the `archive-` palette classes and shared shell classes) —
  no in-scope surface is styled off-system.
- AC: Dark mode derives from the same warm token system re-keyed dark, not a separate
  cool-gray palette. <!-- from CR:dd#1-Shared-warm-archive-visual-system -->
- AC (review-only): a visual QA pass over homepage, one entity page, one search page, and the
  shared navigation confirms one cohesive visual language (typography, palette, spacing,
  surface treatment). <!-- from CR:prd#Acceptance-Criteria R-1 -->

[R-2] **The homepage communicates the site's purpose and at least two primary onward actions
(search, browse all) on first view, desktop and mobile, without scroll-dependent discovery.**
<!-- from CR:prd#R-2 -->
- AC: The built homepage's initial static HTML carries a top-level heading and links to
  `/search` and `/entity`.
- AC: An e2e assertion verifies purpose text plus both actions are visible in the first
  viewport at a desktop and a mobile viewport size.
- AC (review-only): each top-level homepage section serves orientation, browsing, or search —
  no decorative filler. <!-- from CR:prd#Acceptance-Criteria R-2 -->

[R-3] **Entity pages group and label identity, relationship context, key life facts, and
source material so each is locatable without reading the page linearly; sparse entities render
intentionally (empty groups omitted) and dense entities render as separated regions.**
<!-- from CR:prd#R-3; CR:prd#E-1; CR:prd#E-2 -->
- AC: Grouping is driven by the generator-backed contract (frontmatter metadata and section
  structure emitted by `gen_site`), not by prose styling inference.
  <!-- from CR:dd#3-Generator-backed-entity-grouping-and-density-handling -->
- AC: e2e coverage exercises one sparse and one dense entity page.

[R-4] **Browse and search present the same result-card structure, showing lifespan and
contextual metadata (place, relationship) when the data exists, and falling back gracefully to
title plus ID when it does not.**
<!-- from CR:prd#R-4; CR:dd#4-Unified-browse-search-result-cards-from-normalized-metadata -->
- AC: A card whose frontmatter carries `lifespan` / place / `relationship_summary` renders
  them; a record lacking all optional metadata renders title plus ID without layout breakage.
- AC: Component tests cover the metadata and fallback rendering paths.

[R-5] **From every primary page type (homepage, browse, search, entity), visitors can reach
home, search, and the current page context on desktop and mobile; browse, search, and entity
pages carry breadcrumb-style context.**
<!-- from CR:prd#R-5; CR:dd#5-Sticky-navigation-plus-breadcrumb-context -->
- AC: e2e assertions at a desktop and a mobile viewport verify reachability and breadcrumb
  presence per page type.

[R-6] **Redesigned pages preserve accessibility and immediate readability: interactive
elements have visible focus indication, and primary content is readable on initial load
without waiting on animations, overlays, or decorative assets.**
<!-- from CR:prd#R-6 -->
- AC: A focus-visibility rule exists in the shared styles and applies to interactive elements.
- AC: Primary content is present in the built pages' static HTML (no client-render gate on
  primary content).

[R-7] **Where page structure changed relative to the pre-refresh site, previously published
entry points remain discoverable through equally clear or clearer replacement paths.**
<!-- from CR:prd#R-7 -->
- AC: Family/branch entry points remain reachable from the homepage or shared navigation.

[R-8] **The two locked test layers execute and pass on the current tree: the unit suite
(`npm run test:unit`) and the e2e suite (`npm run test:e2e`), and the e2e layer includes the
cohesion coverage the DD names for R-1 (a visual-refresh spec asserting the shared system
across home, search, and entity routes).**
<!-- from CR:dd#Testing-Strategy; CR:dd#Verification-Hooks R-1 -->
<!-- observed: cr4-check first evaluation 2026-08-21 — unit suite green (E9), e2e suite red on the homepage spec (E10), visual-refresh.spec.ts absent (E11) -->
- AC: `npm run test:unit` exits 0 with tests executed.
- AC: `npm run test:e2e` exits 0 with tests executed.
- AC: `tests/e2e/visual-refresh.spec.ts` exists and passes, asserting shared palette/typography
  usage across the home, search, and entity routes.

## 3. Technical constraints and decisions

- **Locked:** Astro + Tailwind stack; static-first rendering; the only always-hydrated islands
  are the search component and the theme toggle — no new always-hydrated islands.
  <!-- from CR:prd#Non-Goals; CR:dd#Cross-Cutting Performance -->
- **Locked:** the metadata contract is generator-backed and additive: `title` remains the only
  required frontmatter field; all card/grouping metadata fields are optional; generated entity
  frontmatter is the source for browse/search card metadata; genealogical content still
  originates in the `gen_site` pipeline. <!-- from CR:dd#3; CR:dd#Cross-Cutting Backward-compatibility -->
- **Locked:** ASCII tree blocks and citation/source links remain first-class preformatted
  content — never flattened into card chrome or re-wrapped. <!-- from CR:dd#3 -->
- **Locked:** canonical routes are preserved: `/`, `/search`, `/entity` (paginated browse),
  `/entity/{id}`. <!-- from CR:dd#Cross-Cutting Consumer-impact -->
- **Locked:** verification uses two layers: Playwright e2e smoke tests and Vitest component
  tests. <!-- from CR:dd#Testing-Strategy -->
- **Delegated:** exact palette values, font stacks, copy and wording, breadcrumb composition,
  section markup details, card layout details. The DD's token/markup snippets are
  illustrative, not contracts.

## 4. Invariants

[I-1] Every generated entity page that carries an ASCII tree renders it inside a
  preformatted `ascii-tree-block` element, unwrapped. <!-- from CR:dd#3 -->
[I-2] A title-only entity (no optional metadata) renders on every surface — entity page,
  browse card, search result — without error or broken layout. <!-- from CR:dd#Cross-Cutting Validation -->
[I-3] The built site introduces no new remote runtime origins (no new external scripts,
  styles, or data dependencies). <!-- from CR:dd#Cross-Cutting Security -->
[I-4] The built homepage's primary content — heading and both primary actions — is
  present in its static HTML. <!-- from CR:prd#Acceptance-Criteria R-6 -->

## 5. Scope fence

- No replacement of the Astro/Tailwind stack. <!-- from CR:prd#Non-Goals -->
- No rework of the genealogy data model or the generation pipeline beyond the additive
  metadata/grouping contract. <!-- from CR:prd#Non-Goals -->
- No new features unrelated to presentation, orientation, or discovery. <!-- from CR:prd#Non-Goals -->
- No blocking splash screens and no autoplay media. <!-- from CR:prd#Non-Goals -->
