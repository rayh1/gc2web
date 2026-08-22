# website-beauty — review pass 2 (2026-08-22)

Delta: baseline `beba027` (HEAD, main; auto rule), tip = working tree, repo root
/workspace/gc2web. Effort delta: tests/e2e/{homepage,navigation,entity-page}.spec.ts modified,
tests/e2e/visual-refresh.spec.ts new (build stage), src/styles/global.css (fix stage),
src/last_modified.ts (machine-updated build stamp, incidental). specs/birthday-today dirt
pre-exists this effort.

Fix-delta since pass 1: src/styles/global.css only — `.btn` restyled onto archive tokens
(accent bg, paper text, archive-dark variants) AND the hand-written prose link rule scoped to
`.prose a:not(.btn)`; the unguarded `.prose a` (specificity 0,1,1) had been overriding `.btn`'s
label color — the root cause of BOTH the original poor contrast and an accent-on-accent
invisible label after the first restyle attempt. Task #1 had been ticked prematurely on its
mechanical verify before the visual re-check; it was un-ticked, completed, and re-verified —
measured in-browser: label rgb(255,249,241) on rgb(157,91,51), element screenshot legible at
both viewports. Notably: the full e2e suite (26 tests) passed WITH the invisible label — the
suites do not look at the CTA; only the visual pass caught it, twice.

Pass 1 (superseded, for the audit trail): findings 0,3 at identity WORKING-TREE:4f9940a87bd6 —
F-1 off-palette `.btn` (from the review-only visual QA; all mechanical gates were green past
it), F-2 [GATE] new no-legacy-palette gate E17, F-3 [GATE] E8 selector binding; J pass found
E1/E2/E8 weakened with F-1 as live counterexample; verifier spot-check that pass: 4/12 re-read,
0 overturned; reconcile clean with builder-MET vs review-partially on R-1 (the pipeline
working). All three tasks applied this pass: gate edits banked by a checker run while their
[GATE] tasks were open (E17 first evaluated RED before the code fix — a valid red-first record),
then ticked.

Element verdicts (each decided by a literally-read clause; evidence per pass 1 plus the fix
re-reads): R-1 → **satisfied** (was partially) — `.btn` all-archive, prose-link exclusion in
place, verifier-confirmed with read_line proof; E17 green after the fix. R-2 through R-8 and
I-1 through I-4 re-affirmed satisfied — evidence unchanged from pass 1 (viewport e2e, generator
grouping + sparse/dense e2e, card component tests, navigation matrix, focus rule
global.css:131-136, branch entries, suites green, ASCII pre, fallback rendering, no remote
origins in delta, static homepage content).

Lanes (reviewer's own runs, final tree): verdict clean — tests lane via explicit
`--tests "npm run test:unit" --tests "npm run test:e2e"` after verify.py's two-suite refusal
(both exit 0; exit codes only, no JUnit), constitution lane clean (C-1 PASS). The gen_site
`uv run pytest` suite was not run: no gen_site code in the delta; recorded, not a finding.

Pass-verdict spot-check: 3/12 re-read by verifier subagent, 0 overturned.

Gate-set audit (J pass, pass-2 state): E17 faithful (negative, red-first discharged by
observation); E8 now faithful (selector-bound); E1/E2 remain presence-checks but their weakened
residue is covered by E17 + the visual-refresh e2e; E16 weakened-by-design (splash half not
mechanizable; discharged by screenshots); all other gates faithful as in pass 1. Waivers and
NEVER-RED discharges unchanged and sound.

Build cross-check: reconcile re-run against the unchanged build report — all agree (R-1 now
satisfied matches builder MET); all `test:` fields resolve.

Observation, recorded not filed: `src/components/Search.tsx:125` still uses `border-primary-500`
on a transient loading spinner — outside F-1's scope (shared styles), invisible in the
loaded-page QA screenshots, and outside E17's boundary (global.css). A future sweep could
retire the whole legacy `primary` palette from tailwind.config.cjs.

review status: {"findings_open": 0, "spec_findings": 0, "code_findings": 0}
review reduced: {"reduced": false, "reason": ""}
review element: {"id": "R-1", "kind": "requirement", "verdict": "satisfied", "findings": ""}
review element: {"id": "R-2", "kind": "requirement", "verdict": "satisfied", "findings": ""}
review element: {"id": "R-3", "kind": "requirement", "verdict": "satisfied", "findings": ""}
review element: {"id": "R-4", "kind": "requirement", "verdict": "satisfied", "findings": ""}
review element: {"id": "R-5", "kind": "requirement", "verdict": "satisfied", "findings": ""}
review element: {"id": "R-6", "kind": "requirement", "verdict": "satisfied", "findings": ""}
review element: {"id": "R-7", "kind": "requirement", "verdict": "satisfied", "findings": ""}
review element: {"id": "R-8", "kind": "requirement", "verdict": "satisfied", "findings": ""}
review element: {"id": "I-1", "kind": "invariant", "verdict": "satisfied", "findings": ""}
review element: {"id": "I-2", "kind": "invariant", "verdict": "satisfied", "findings": ""}
review element: {"id": "I-3", "kind": "invariant", "verdict": "satisfied", "findings": ""}
review element: {"id": "I-4", "kind": "invariant", "verdict": "satisfied", "findings": ""}
