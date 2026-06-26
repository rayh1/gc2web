---
code0_ref: ce6ae552598e71f1b02cea00ebede9f5eb34108d
depth: full-design
---

# Website Visual Refresh Design Document

PRD: specs/website-beauty/website-beauty.prd.md

## Codebase Analysis

- Shared page chrome is centralized in two layouts plus the header/footer components, so a site-wide redesign can be applied through a small set of high-leverage files rather than per-page duplication.
  - Evidence: `src/layouts/PageLayout.astro` renders the shared page shell and prose container; `src/layouts/BlogPostLayout.astro` does the same for entity pages; `src/components/Header.astro` and `src/components/Footer.astro` provide global navigation and footer chrome. Search method: targeted file reads.
- The homepage is currently a minimal static page with a hero image, a one-sentence description, and two hardcoded family entry links, which leaves the PRD's orientation and onward-action requirements largely unmet.
  - Evidence: `src/pages/index.astro` contains a single image, one descriptive paragraph, and an unordered list of two links. Search method: targeted file read.
- Search and browse surfaces currently expose very little result context, and the content schema only guarantees a title field, so richer comparison requires an explicit metadata contract instead of pure restyling.
  - Evidence: `src/content.config.ts` defines the `entity` schema as `z.object({ title: z.string() })`; `src/components/Search.tsx` searches `data.title`, `data.description`, and `id`; `src/components/PostListItem.tsx` renders only the title and ID. Search method: targeted file reads.
- Entity pages render generated markdown directly through Astro content rendering, and the generated content already uses heading-based semantic groupings plus preformatted ASCII tree blocks and inline citation links.
  - Evidence: `src/pages/entity/[id].astro` calls `render(post)` and places `<Content />` inside `BlogPostLayout`; `src/content/entity/I00005.md` contains `### Gegevens`, `### Ouders`, `### Chronologie`, `### Bronnen lijst`, and a `<pre class="ascii-tree-block">` section. Search method: targeted file reads.
- Mobile navigation is already sticky and toggle-based, but it does not expose explicit page-context cues beyond the active link state, which is insufficient for the breadcrumb-style orientation locked in for this effort.
  - Evidence: `src/components/Header.astro` defines a sticky header, a hamburger menu, and active links for `/entity` and `/search`, but no breadcrumb or current-context region. Search method: targeted file read.

## Technical Approach

This effort keeps the Astro/Tailwind stack and preserves the current route/content model while explicitly expanding the visual system, generated metadata contract, and page composition. The redesign remains static-first: shared shells, homepage sections, entity grouping, and browse/search cards render server-side wherever possible, while the existing client-side search and theme toggle remain the only always-hydrated interactions.

### 1. Shared warm archive visual system

Lock a semantic design-token layer across Tailwind and global CSS so the homepage, entity pages, browse/search surfaces, header, and footer all draw from the same palette, spacing system, and type hierarchy. Titles and section headings use a restrained display-serif stack to create the archival feel, while body text, metadata, and controls stay on a legible sans stack. Dark mode remains supported, but it is re-authored as the same warm system in a dark key rather than a separate cool-gray theme.

```css
:root {
  --color-ink: #2f241d;
  --color-paper: #f6f0e7;
  --color-surface: #fffaf4;
  --color-accent: #9d5b33;
  --font-display: "Iowan Old Style", "Palatino Linotype", serif;
  --font-body: "Inter", "Segoe UI", sans-serif;
}

.page-shell {
  @apply bg-[var(--color-paper)] text-[var(--color-ink)];
}
```

### 2. Homepage as an editorial landing page

Lock the homepage to three explicit jobs: identify the archive, offer two primary onward actions, and provide family-specific entry points. The page may add or reorder sections, but the structure stays purposeful: a hero with the site's purpose and primary actions, a section for starting families or branches, and a short exploration section that explains how to browse or search the archive. Decorative sections that do not improve orientation or discovery are out.

```astro
<main class="page-shell">
  <section class="home-hero">...</section>
  <section class="home-actions">
    <a href="/search">Zoeken</a>
    <a href="/entity">Alles bekijken</a>
  </section>
  <section class="home-branches">...</section>
</main>
```

### 3. Generator-backed entity grouping and density handling

Lock entity-page grouping to a generator-backed contract rather than trying to infer all grouping only from prose styling. The generator may restructure output if needed, but the content source model stays the same: genealogical content still originates in the generation pipeline and emitted markdown files. The preferred contract is additive: generated entity files gain normalized metadata plus stable grouping hooks for identity, family relationships, chronology, sources, and ancillary sections. The rendering layer then uses those hooks to present sparse pages intentionally and dense pages as clearly separated content regions. ASCII tree blocks and source/footnote links remain first-class content and must not be flattened into card chrome or wrapped in ways that break preformatted layout.

```yaml
---
title: Petrus Johannes Hoofman (1890-1972)
lifespan: 1890-1972
birth_place: Muiden
death_place: Amsterdam
branch: Hoofman
section_order: [identity, parents, relationships, chronology, sources]
---
```

### 4. Unified browse/search result cards from normalized metadata

Lock browse and search to the same result-card structure. Instead of title and ID only, result cards show a title, lifespan when known, and one or two context lines such as relationship hints or place data when that metadata exists. To make that reliable, the generation pipeline and `src/content.config.ts` must evolve together: generated entity frontmatter becomes the source for normalized browse/search metadata, and the search index keys expand to use those fields. If a record lacks contextual metadata, the card falls back gracefully to title plus ID without breaking the layout.

```ts
schema: z.object({
  title: z.string(),
  lifespan: z.string().optional(),
  birth_place: z.string().optional(),
  death_place: z.string().optional(),
  relationship_summary: z.string().optional(),
  branch: z.string().optional(),
});
```

### 5. Sticky navigation plus breadcrumb context

Keep the sticky header and mobile drawer, but add explicit breadcrumb-style current-context cues for paginated browse pages, search pages, and entity pages. The breadcrumb stays lightweight: it clarifies location and return paths without becoming a second primary navigation system. Desktop can render breadcrumbs inline beneath the header; mobile keeps them visible in a condensed row under the sticky chrome so orientation survives long content scrolls and section reordering.

```astro
<Header
  currentContext={[
    { label: "Home", href: "/" },
    { label: "Alles", href: "/entity" },
    { label: title },
  ]}
/>
```

## Requirements Mapping

- **[R-1] Cohesive warm archive visual system**
  - Extend `tailwind.config.cjs` and `src/styles/global.css` with semantic palette, spacing, border, and type tokens.
  - Refactor `src/layouts/PageLayout.astro`, `src/layouts/BlogPostLayout.astro`, `src/components/Header.astro`, and `src/components/Footer.astro` to consume the shared shell and typography hierarchy.
- **[R-2] Homepage orientation and onward actions**
  - Rebuild `src/pages/index.astro` around a hero, primary action area, and family/archive entry sections.
  - Reuse shared shell styles so homepage sections visually match browse, search, and entity surfaces.
- **[R-3] Entity grouping and labeling**
  - Extend `gen_site/gen_site.py` and generated entity frontmatter so the rendering layer can distinguish identity, relationships, chronology, and source-oriented sections.
  - Update `src/content.config.ts`, `src/pages/entity/[id].astro`, and `src/layouts/BlogPostLayout.astro` to render grouped entity regions while preserving markdown content, ASCII trees, and citations.
- **[R-4] Result hierarchy and contextual comparison**
  - Extend generated metadata and `src/content.config.ts` so search/browse cards can display lifespan, place, and relationship context when available.
  - Update `src/components/Search.tsx`, `src/components/PostListItem.tsx`, `src/components/PostList.astro`, and `src/pages/entity/[...page].astro` to render the richer result-card structure consistently.
- **[R-5] Shared navigation and orientation**
  - Refactor `src/components/Header.astro` to include breadcrumb-style context and preserve clear access to home and search in desktop and mobile states.
  - Pass page-context data from `src/pages/index.astro`, `src/pages/search.astro`, `src/pages/entity/[id].astro`, and `src/pages/entity/[...page].astro` through the layouts.
- **[R-6] Accessibility and immediate readability**
  - Encode focus-visible, contrast-conscious, and typography rules in `src/styles/global.css` and shared layout classes.
  - Avoid new blocking interactions; keep primary content readable on initial load and keep hydration limited to the existing interactive islands unless a new island is justified.
- **[R-7] Discoverability through changed structure**
  - Preserve canonical routes and prominent entry points in shared navigation, homepage actions, and breadcrumb context.
  - Where sections move or become cards, ensure their replacement paths are visible in-page or in shared chrome rather than hidden behind purely decorative treatments.

## Verification Hooks

- **[R-1] Proved by:** `tests/e2e/visual-refresh.spec.ts` (to be created) asserting shared palette/typography classes across home, search, and entity routes; reviewer-assisted visual QA pass on desktop and mobile sample pages.
- **[R-2] Proved by:** `tests/e2e/homepage.spec.ts` (to be created) verifying homepage first view exposes the site purpose plus at least two onward actions without scrolling-dependent discovery.
- **[R-3] Proved by:** `tests/e2e/entity-page.spec.ts` (to be created) checking grouped entity regions appear on sparse and dense sample entities; `src/components/__tests__/entity-layout.test.ts` (to be created) validating grouping fallbacks when optional metadata is missing.
- **[R-4] Proved by:** `tests/e2e/search.spec.ts` (to be created) verifying result cards show contextual metadata when available and remain comparable in place; `src/components/__tests__/PostListItem.test.tsx` (to be created) covering metadata fallbacks and highlight rendering.
- **[R-5] Proved by:** `tests/e2e/navigation.spec.ts` (to be created) at mobile and desktop viewports, asserting access to home, search, and current-context breadcrumbs from each page type.
- **[R-6] Proved by:** `src/components/__tests__/Header.test.tsx` and `src/components/__tests__/Search.test.tsx` (both to be created) for keyboard/focus states and empty-state messaging; reviewer-assisted keyboard sweep covering homepage, search, and entity pages.
- **[R-7] Proved by:** `tests/e2e/navigation.spec.ts` and `tests/e2e/homepage.spec.ts` confirming legacy entry points remain discoverable via homepage actions, shared nav, or breadcrumb paths after restructuring.

## Cross-Cutting Checklist

- **Consumer impact (Applicable):** Keep canonical public routes and familiar archive entry points intact while replacing weaker in-page navigation with clearer homepage actions and breadcrumb context. Verification hook: `tests/e2e/navigation.spec.ts` route traversal from `/`, `/entity`, `/search`, and representative entity pages.
- **Validation & error handling (Applicable):** Treat generated metadata as optional input with graceful fallbacks to existing title/ID behavior so sparse or partially normalized records still render intelligibly. Verification hook: `src/components/__tests__/PostListItem.test.tsx` fallback cases and `tests/e2e/search.spec.ts` no-result state.
- **Testing & coverage (Applicable):** Add both browser smoke coverage and component-level tests for the redesigned surfaces, and run them alongside build validation. Verification hook: `npm test` (to be introduced) and `npm run build`.
- **Performance & scalability (Applicable):** Keep the redesign static-first, avoid new always-hydrated UI except where justified, and keep decorative treatments lightweight enough that initial content remains immediately readable. Verification hook: `npm run build` plus reviewer check that only search and theme-toggle islands remain hydrated by default.
- **Security (Applicable):** Preserve the static-content model and avoid introducing new remote data dependencies, HTML injection points, or client-side secrets while expanding generator metadata. Verification hook: reviewer check on generator output and content rendering paths in `gen_site/gen_site.py` and Astro templates.
- **Backward compatibility & versioning (Applicable):** Make metadata additions additive so generated content remains consumable during the transition from title-only schema to richer cards. Verification hook: regenerate content and smoke-test a pre-existing entity route plus browse/search pages.
  Considered but not applicable: Configuration & secrets, Data persistence & migrations, API/contract compatibility, Authentication/authorization, Observability, Concurrency/idempotency, Rollout/feature flags

## Testing Strategy

This effort locks in two complementary test layers plus a manual QA pass.

- **Browser smoke tests:** add Playwright-based route coverage against the built site to verify homepage actions, breadcrumb navigation, mobile menu behavior, search results, and representative sparse/dense entity pages.
- **Component-level tests:** add Vitest-based tests for the interactive or condition-heavy components, especially `Header`, `Search`, and `PostListItem`.
- **Manual QA:** run a visual and keyboard pass on desktop and mobile viewports for the homepage, one sparse entity page, one dense entity page, browse results, and search results.

Planned test/config touchpoints:

- `playwright.config.ts` (to be created)
- `vitest.config.ts` (to be created)
- `tests/e2e/homepage.spec.ts` (to be created)
- `tests/e2e/navigation.spec.ts` (to be created)
- `tests/e2e/search.spec.ts` (to be created)
- `tests/e2e/entity-page.spec.ts` (to be created)
- `src/components/__tests__/Header.test.tsx` (to be created)
- `src/components/__tests__/Search.test.tsx` (to be created)
- `src/components/__tests__/PostListItem.test.tsx` (to be created)

Representative assertion shape:

```ts
test("homepage exposes two primary exploration actions", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("link", { name: /zoeken/i })).toBeVisible();
  await expect(page.getByRole("link", { name: /alles/i })).toBeVisible();
  await expect(page.getByRole("main")).toContainText(/genealog/i);
});
```

## Edge Case Handling

- **[E-1] Sparse entity pages:** render a strong identity/header region even when only minimal supporting sections exist; omit empty groups instead of showing broken placeholders.
- **[E-2] Dense entity pages:** render major groups as clearly separated regions, keep ASCII trees isolated in preformatted blocks, and preserve citation/source density without collapsing everything into one prose column.
- **[E-3] Similar-name search results:** show normalized contextual metadata when available; if metadata is absent, retain title plus stable ID so disambiguation never becomes worse than today.
- **[E-4] Mobile orientation:** keep breadcrumb context visible in condensed form and stack grouped content into a single readable column without losing access to search, browse, or the current page identity.

## Risk Mitigation

- **[K-1] Information density regression:** keep metadata compact, avoid oversized decorative treatments on research-heavy pages, and validate the dense-entity experience explicitly during browser smoke and manual QA.
- **[K-2] Hidden familiar entry points:** preserve navigation redundancy through homepage actions, sticky header links, and breadcrumbs so returning users still have obvious paths to browse/search.
- **[K-3] Perceived performance regression:** avoid large animation dependencies or heavyweight new hydration; prefer CSS/layout changes and static rendering over new runtime behavior.

## File Touchpoints

Existing files to modify:

- `tailwind.config.cjs`
- `src/styles/global.css`
- `src/layouts/PageLayout.astro`
- `src/layouts/BlogPostLayout.astro`
- `src/components/Header.astro`
- `src/components/Footer.astro`
- `src/pages/index.astro`
- `src/pages/search.astro`
- `src/pages/entity/[id].astro`
- `src/pages/entity/[...page].astro`
- `src/components/Search.tsx`
- `src/components/Searchbar.astro`
- `src/components/PostList.astro`
- `src/components/PostListItem.tsx`
- `src/content.config.ts`
- `package.json`
- `gen_site/gen_site.py`

Files likely to be created:

- `src/components/Breadcrumbs.astro`
- `playwright.config.ts`
- `vitest.config.ts`
- `tests/e2e/homepage.spec.ts`
- `tests/e2e/navigation.spec.ts`
- `tests/e2e/search.spec.ts`
- `tests/e2e/entity-page.spec.ts`
- `src/components/__tests__/Header.test.tsx`
- `src/components/__tests__/Search.test.tsx`
- `src/components/__tests__/PostListItem.test.tsx`

Generated artifacts (do not edit):

- Generated file patterns: `src/content/entity/*.md`
- Source-of-truth inputs: `gen_site/Hoofman.ged`, `gen_site/gen_site.py`
- Regeneration command: `cd gen_site && PYTHONPATH=. python gen_site.py Hoofman.ged`
