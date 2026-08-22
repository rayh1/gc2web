CR: specs/back-to-top/back-to-top.cr.md
Spec-sha: 18a2dfa8b8c9
Reviewed-at: WORKING-TREE:3886e00d6749
Findings: 0,0
Reduced: false
Lanes: tests:clean,constitution:clean

Tasks #1–#4 are BOUND bindings (gate-file writes licensed by the [GATE] banking path); #5 is
the pass's one finding, a gate repair.

- [x] #1 bind T1 [GATE] T1 — faithful: tests/e2e/back-to-top.spec.ts::back-to-top control appears in the lower-right after scrolling down [AUTO] [high confidence]
- [x] #2 bind T2 [GATE] T2 — faithful: tests/e2e/back-to-top.spec.ts::back-to-top control stays hidden while the page is at the top [AUTO] [high confidence]
- [x] #3 bind T3 [GATE] T3 — faithful: tests/e2e/back-to-top.spec.ts::back-to-top control scrolls the page back to the very top [AUTO] [high confidence]
- [x] #4 bind T4 [GATE] T4 — faithful: tests/e2e/back-to-top.spec.ts::back-to-top control carries the exact Dutch accessible name [AUTO] [high confidence]
- [x] #5 repair E1 [GATE] E1 — added-lines grep vacuous on untracked files [AUTO] [high confidence]
  Finding ref: [F-1]
  Files: specs/back-to-top/back-to-top.gates.md
  Success criteria: E1's CHECK sees new files' content without depending on transient index state — prepend `git add -N src` so `git diff` includes untracked additions; the gate then genuinely scans added lines whether or not intent-to-add is already set.
  Verify: git stash the -N entries would be disruptive; instead confirm `git diff d6f01f9e1469 -- src` shows BackToTop.astro content after the CHECK runs on a fresh index state.
  Reference: [I-1]
