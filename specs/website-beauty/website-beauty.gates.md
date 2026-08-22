Derived-from: specs/website-beauty/website-beauty.cr.md
Spec-sha: f24e05ca1f0f

- [x] E1 shared-token-consumption
  CHECK: for f in src/layouts/PageLayout.astro src/layouts/BlogPostLayout.astro src/components/Header.astro src/components/Footer.astro src/pages/index.astro src/pages/search.astro; do grep -Eq "archive-|page-shell|content-frame|PageLayout|BlogPostLayout" "$f" || { echo "$f"; exit 1; }; done
  EXPECT: exit=0
  SOURCE: "The shared page shells and page files for all four surface types consume the shared archive token/utility layer (the `archive-` palette classes and shared shell classes)"
  SOURCE: "[R-1] **The homepage, shared navigation, search pages, and entity pages present one cohesive"
  EVIDENCE: exit=0; 1 clause(s) satisfied; T=/tmp/cr4-gate-wzb2j6wh

- [x] E2 dark-mode-same-system
  CHECK: grep -Eq "dark:(bg|text|border)-archive-dark" src/styles/global.css
  EXPECT: exit=0
  SOURCE: "Dark mode derives from the same warm token system re-keyed dark, not a separate cool-gray palette."
  SOURCE: "[R-1] **The homepage, shared navigation, search pages, and entity pages present one cohesive"
  EVIDENCE: exit=0; 1 clause(s) satisfied; T=/tmp/cr4-gate-mwqrtyp9

- [x] E3 homepage-static-actions
  CHECK: npx astro build > $T/build.log 2>&1 || exit 2; grep -q "<h1" dist/index.html && grep -q 'href="/search"' dist/index.html && grep -q 'href="/entity"' dist/index.html
  EXPECT: exit=0
  SOURCE: "The built homepage's initial static HTML carries a top-level heading and links to `/search` and `/entity`."
  SOURCE: "[R-2] **The homepage communicates the site's purpose and at least two primary onward actions"
  EVIDENCE: exit=0; 1 clause(s) satisfied; T=/tmp/cr4-gate-8f3fbgxp

- [x] E4 homepage-first-view-e2e
  CHECK: npx astro build > $T/build.log 2>&1 || exit 2; npx playwright test tests/e2e/homepage.spec.ts
  EXPECT: exit=0
  SOURCE: "An e2e assertion verifies purpose text plus both actions are visible in the first viewport at a desktop and a mobile viewport size."
  SOURCE: "[R-2] **The homepage communicates the site's purpose and at least two primary onward actions"
  EVIDENCE: exit=0; 1 clause(s) satisfied; T=/tmp/cr4-gate-ou_017w0

- [x] E5 entity-grouping-e2e
  CHECK: npx astro build > $T/build.log 2>&1 || exit 2; npx playwright test tests/e2e/entity-page.spec.ts
  EXPECT: exit=0
  SOURCE: "e2e coverage exercises one sparse and one dense entity page."
  SOURCE: "[R-3] **Entity pages group and label identity, relationship context, key life facts, and"
  EVIDENCE: exit=0; 1 clause(s) satisfied; T=/tmp/cr4-gate-oq09ne7g

- [x] E6 card-metadata-component-tests
  CHECK: npx vitest run src/components/__tests__/PostListItem.test.tsx
  EXPECT: exit=0
  SOURCE: "Component tests cover the metadata and fallback rendering paths."
  SOURCE: "[R-4] **Browse and search present the same result-card structure, showing lifespan and"
  EVIDENCE: exit=0; 1 clause(s) satisfied; T=/tmp/cr4-gate-ksc8ec1r

- [x] E7 navigation-orientation-e2e
  CHECK: npx astro build > $T/build.log 2>&1 || exit 2; npx playwright test tests/e2e/navigation.spec.ts
  EXPECT: exit=0
  SOURCE: "e2e assertions at a desktop and a mobile viewport verify reachability and breadcrumb presence per page type."
  SOURCE: "[R-5] **From every primary page type (homepage, browse, search, entity), visitors can reach"
  EVIDENCE: exit=0; 1 clause(s) satisfied; T=/tmp/cr4-gate-dr2xsjeo

- [x] E8 focus-visibility-rule
  CHECK: grep -E "(a|button|input|summary):focus-visible" src/styles/global.css
  EXPECT: exit=0
  SOURCE: "A focus-visibility rule exists in the shared styles and applies to interactive elements."
  SOURCE: "[R-6] **Redesigned pages preserve accessibility and immediate readability: interactive"
  EVIDENCE: exit=0; 1 clause(s) satisfied; T=/tmp/cr4-gate-6uc8y_tx

- [x] E9 unit-suite-green
  CHECK: npm run test:unit
  EXPECT: exit=0
  SOURCE: "`npm run test:unit` exits 0 with tests executed."
  SOURCE: "[R-8] **The two locked test layers execute and pass on the current tree: the unit suite"
  EVIDENCE: exit=0; 1 clause(s) satisfied; T=/tmp/cr4-gate-6ipgi2l1

- [x] E10 e2e-suite-green
  CHECK: npx astro build > $T/build.log 2>&1 || exit 2; npm run test:e2e
  EXPECT: exit=0
  SOURCE: "`npm run test:e2e` exits 0 with tests executed."
  SOURCE: "[R-8] **The two locked test layers execute and pass on the current tree: the unit suite"
  EVIDENCE: exit=0; 1 clause(s) satisfied; T=/tmp/cr4-gate-yb6_ulr_

- [x] E11 visual-refresh-coverage
  CHECK: test -f tests/e2e/visual-refresh.spec.ts || exit 2; npx astro build > $T/build.log 2>&1 || exit 3; npx playwright test tests/e2e/visual-refresh.spec.ts
  EXPECT: exit=0
  SOURCE: "`tests/e2e/visual-refresh.spec.ts` exists and passes, asserting shared palette/typography usage across the home, search, and entity routes."
  SOURCE: "[R-8] **The two locked test layers execute and pass on the current tree: the unit suite"
  EVIDENCE: exit=0; 1 clause(s) satisfied; T=/tmp/cr4-gate-0iizvmpy

- [x] E12 ascii-tree-preformatted
  CHECK: npx astro build > $T/build.log 2>&1 || exit 2; grep -q '<pre class="ascii-tree-block"' dist/entity/I00005/index.html
  EXPECT: exit=0
  SOURCE: "renders it inside a preformatted `ascii-tree-block` element, unwrapped."
  SOURCE: "[I-1] Every generated entity page that carries an ASCII tree renders it inside a"
  EVIDENCE: exit=0; 1 clause(s) satisfied; T=/tmp/cr4-gate-zb340_dr

- [x] E13 no-new-hydrated-islands
  CHECK: grep -rE "client:(load|idle|visible|only)" src --include=*.astro --include=*.tsx | grep -vE "Search|ThemeToggle"
  EXPECT: exit=1
  SOURCE: "the only always-hydrated islands are the search component and the theme toggle — no new always-hydrated islands."
  SOURCE: "Astro + Tailwind stack; static-first rendering; the only always-hydrated islands"
  EVIDENCE: exit=1; 1 clause(s) satisfied; T=/tmp/cr4-gate-8kdzduj5

- [x] E14 schema-additive-title-only-required
  CHECK: ! grep -E "^\s+\w+: z\." src/content.config.ts | grep -v "title:" | grep -v "schema:" | grep -v "optional()" | grep -q .
  EXPECT: exit=0
  SOURCE: "`title` remains the only required frontmatter field; all card/grouping metadata fields are optional"
  SOURCE: "the metadata contract is generator-backed and additive: `title` remains the only"
  EVIDENCE: exit=0; 1 clause(s) satisfied; T=/tmp/cr4-gate-_pufrtg5

- [x] E15 canonical-routes-built
  CHECK: npx astro build > $T/build.log 2>&1
  EXPECT: exit=0; exists dist/index.html; exists dist/search/index.html; exists dist/entity/index.html; exists dist/entity/I00005/index.html
  SOURCE: "canonical routes are preserved: `/`, `/search`, `/entity` (paginated browse), `/entity/{id}`."
  EVIDENCE: exit=0; 5 clause(s) satisfied; T=/tmp/cr4-gate-rprltf7r

- [x] E17 no-legacy-palette
  CHECK: grep -rn "primary-" src/styles/global.css
  EXPECT: exit=1
  SOURCE: "[R-1] **The homepage, shared navigation, search pages, and entity pages present one cohesive"
  SOURCE: "no in-scope surface is styled off-system."
  EVIDENCE: exit=1; 1 clause(s) satisfied; T=/tmp/cr4-gate-8y8zg2yr

- [x] E16 no-autoplay-media
  CHECK: npx astro build > $T/build.log 2>&1 || exit 2; grep -rql "autoplay" dist --include=*.html
  EXPECT: exit=1
  SOURCE: "No blocking splash screens and no autoplay media."
  EVIDENCE: exit=1; 1 clause(s) satisfied; T=/tmp/cr4-gate-r7wcy809

NO-GATE [I-2]: covered-by:E6 — the PostListItem fallback tests plus E5's sparse-entity e2e exercise title-only rendering
NO-GATE [I-3]: not-mechanizable — "no NEW remote origins" needs a pre-refresh baseline comparison; routed to review with the delta in hand
NO-GATE [I-4]: covered-by:E3 — the static-HTML grep is exactly this invariant's check
NO-GATE [R-7]: covered-by:E4 — homepage e2e asserts the branch entry points remain reachable; navigation e2e (E7) covers the shared-nav paths
NO-GATE "ASCII tree blocks and citation/source links remain first-class preformatted content": covered-by:E12
NO-GATE "verification uses two layers: Playwright e2e smoke tests and Vitest component tests": covered-by:E9 — together with E10; the suites running IS the two-layer decision
NO-GATE "No replacement of the Astro/Tailwind stack.": review-only — a stack swap is unmissable in the delta
NO-GATE "No rework of the genealogy data model or the generation pipeline beyond the additive metadata/grouping contract.": review-only — conformance is a delta judgment, not a command
NO-GATE "No new features unrelated to presentation, orientation, or discovery.": review-only — relevance is a judgment call

NEVER-RED E1: pre-existing — the archive token classes shipped with commit 9d8f11e; observed in index.astro and global.css 2026-08-21
NEVER-RED E2: pre-existing — dark:archive-dark-* classes observed in index.astro 2026-08-21
NEVER-RED E3: pre-existing — both action hrefs read in src/pages/index.astro 2026-08-21; the build succeeded the same day
NEVER-RED E5: pre-existing — entity-page.spec.ts shipped with the redesign; green at first evaluation 2026-08-21
NEVER-RED E6: pre-existing — PostListItem tests shipped with the redesign; green at first evaluation 2026-08-21
NEVER-RED E7: pre-existing — navigation.spec.ts shipped with the redesign; green at first evaluation 2026-08-21
NEVER-RED E8: pre-existing — focus-visible rules shipped in global.css; green at first evaluation 2026-08-21
NEVER-RED E9: pre-existing — the unit suite shipped green; first evaluation 2026-08-21 confirmed
NEVER-RED E12: pre-existing — <pre class="ascii-tree-block"> observed in src/content/entity/I00005.md 2026-08-21
NEVER-RED E13: invariant-over-existing — the islands constraint holds on the current tree and must keep holding
NEVER-RED E14: pre-existing — schema read 2026-08-21: every field after title carries .optional()
NEVER-RED E15: pre-existing — 859 pages built successfully 2026-08-21
NEVER-RED E16: invariant-over-existing — no autoplay exists today; the fence forbids introducing it
