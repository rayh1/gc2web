---
slug: ascii-tree-pages
prd: specs/ascii-tree-pages/ascii-tree-pages.prd.md
code0_ref: 1a16193edf43a675b42dfb18b80b03355b903a79
depth: full-design
---

# ASCII Tree Pages Design Document

PRD reference: `specs/ascii-tree-pages/ascii-tree-pages.prd.md`

## Codebase Analysis

- The current tree section is emitted directly during markdown generation in `gen_site/gen_site.py`, where each individual page adds a `### Boom` section, wraps the content in `<details><summary>Toon</summary>`, and embeds a PlantUML SVG URL generated from `PlantUMLCreator.create_individual_diagram(individual)`.
- The available genealogical data for tree construction already lives on the loaded model objects. `Individual` exposes `famc`, `fams`, `father`, `mother`, and sibling/spouse/child traversal helpers; `Family` exposes `husband`, `wife`, and `children`. No new data-loading boundary is needed for the replacement tree.
- The existing PlantUML tree scope is intentionally limited to direct parents, the focal individual, spouse families, and children. It does not encode grandparents, aunts, uncles, or a full ancestry chart. The replacement should preserve that same scope unless a later requirement expands it.
- Page output is assembled as a `list[str]` and written as markdown in one pass. Multiline tree content fits this generation model naturally and can be emitted as a fenced block or equivalent structured markdown fragment.
- Site styling already supports prose content, preformatted blocks, and overflow handling in `src/styles/global.css`. The new tree can rely on a dedicated styled block inside the generated markdown without introducing a client-side renderer.

## Approach Constraints

- Replace the PlantUML image-based tree in generated individual entity pages; do not keep the collapsible UI.
- Keep the tree visible by default near the top of the page, in the same general placement as the current tree section.
- Preserve the core genealogical structure now shown by the page tree section rather than chasing byte-for-byte `gedq` formatting parity.
- The tree must remain understandable without color; any color is additive only.

## Technical Approach

### Locked-In Decisions

1. **Generator-side replacement, not Astro-side runtime rendering.**
   The tree will be generated during `gen_site.py` page creation, replacing the existing PlantUML URL emission in the markdown source. This keeps the feature inside the current static-generation architecture and avoids introducing a second rendering pipeline.

2. **Box-drawing text tree rendered in a styled preformatted block.**
   The tree output will use box-drawing characters such as `├──`, `└──`, and `│` to give a clear tree shape while staying text-first. The generated markdown will render the tree in a preformatted block so spacing and connectors remain stable.

3. **Horizontal scrolling is the width strategy.**
   Tree lines must preserve alignment. When the tree is wider than the viewport, the tree block will scroll horizontally rather than wrapping and damaging the branch structure.

4. **Compact labels: name plus lifespan years only.**
   Person entries in the tree will display the person name and the compact lifespan form already used elsewhere, e.g. `(1833-1874)`, rather than detailed dates. This preserves useful context while limiting line growth.

5. **Color semantics: focal person highlight only.**
   If color styling is applied, it will highlight the focal person only. Relationship meaning must continue to come from the text layout itself, not from color. Other people remain neutral so the visual system stays simple and accessibility-safe.

6. **Multi-family handling may reduce displayed breadth when needed.**
   People with multiple spouse families should not force an unreadable tree. The implementation may reduce the displayed set when breadth would become excessive, but the rendered result must still be sensible and deterministic rather than collapsing into an empty or broken layout.

### Delegated Decisions

- The exact traversal and ordering algorithm for spouse families and children is delegated to implementation, as long as it remains deterministic and preserves the locked-in scope.
- The exact threshold for when a multi-family tree is considered too wide to show in full is delegated to implementation.
- The exact markdown representation of the tree block is delegated, provided it remains preformatted and supports horizontal scrolling.

### Illustrative Output Shape

The intended output shape is text-first and readable without styling:

```text
Petrus Hoofman (1833-1874)
├── Constantia Engels (1838-1915) [focus]
│   ├── Augustinus Hoofman (1860-1918)
│   ├── Petrus Johannes Hoofman (1888-1890)
│   └── Anna Maria Christina Hoofman (1893-?)
└── other direct-family branches when shown
```

The exact characters and spacing can vary slightly in implementation, but the final layout must preserve a recognizable box-drawing tree with a clearly identifiable focal person.

### Illustrative Generator Integration

The replacement happens where the page currently emits the PlantUML section:

````python
content.append(f"{HEADER_PREFIX} Boom")
content.append("")
content.append("```text")
content.extend(render_ascii_tree(individual))
content.append("```")
````

The implementation may choose a custom HTML wrapper instead of a fenced block if that is the cleanest way to attach scrolling and focal-person styling, but the wrapper must still render as preformatted text and must not reintroduce collapsible behavior.

## Implementation Strategy

- Add a dedicated tree-rendering helper in the generator-side code path, parallel to the current PlantUML helper, so tree formatting logic is isolated from the rest of page assembly.
- Replace the current `### Boom` section emission in `gen_site/gen_site.py` with the new always-visible text tree block.
- Add tree-specific styling in `src/styles/global.css` for preformatted layout, horizontal overflow handling, and focal-person highlighting.
- Preserve the rest of the generated page structure unchanged so this feature remains scoped to tree rendering.

## Testing Strategy

- Add focused tests around the new tree helper for typical direct-family cases, missing-parent cases, and multi-family width-reduction behavior.
- Add or update generation-level verification that representative generated pages no longer include the PlantUML collapsible section and do include the new visible tree block.
- Validate the rendered output shape on narrow widths by asserting that the tree block uses horizontal overflow instead of wrapped connector lines.

## Edge Case Handling

- **No direct relatives:** render a minimal single-person tree rather than omitting the section.
- **Only one known parent:** show the available parent branch without placeholder text for the missing branch.
- **Multiple spouse families:** show a deterministic reduced subset when breadth would exceed the readable limit.
- **Long names:** keep the compact lifespan format and rely on horizontal scroll instead of soft wrapping.
- **Missing life dates:** preserve the existing `?`-style year output behavior rather than inventing new placeholder text.

## Risk Mitigation

- Use a dedicated helper rather than inline string assembly scattered through page generation, so layout fixes stay local.
- Keep color optional and focal-only to avoid recreating semantic coupling through presentation.
- Favor stable preformatted rendering over responsive wrapping, because broken connector alignment is worse than horizontal scrolling for a genealogy tree.

## Cross-Cutting Checklist

- **Rendering resilience:** The tree block must render as readable preformatted text in both styled and minimally styled contexts. Verification hook: inspect representative generated markdown and rendered page output with and without the focal-person style applied.
- **Responsive behavior:** The tree must preserve alignment on narrow screens by using horizontal overflow rather than wrapped connectors. Verification hook: inspect the tree block on a mobile-width viewport and confirm branch structure remains intact.
- **Accessibility/readability:** The tree must remain understandable without color and without expanding UI. Verification hook: review text-only rendered output for representative simple and complex family pages.
- **Generation stability:** Tree generation must stay inside the current static site generation flow and avoid external diagram dependencies. Verification hook: run the existing generator and confirm pages are emitted without PlantUML tree URLs.

Considered but not applicable: backend API compatibility, runtime data fetching, authentication, persistence, external service integration

## Verification Hooks

- [R-1] Verify generated individual pages no longer emit the `<details><summary>Toon</summary>` PlantUML wrapper and instead emit a visible tree block near the top of the page.
- [R-2] Verify representative pages with parents, spouse families, and children show those relationships in the rendered tree.
- [R-3] Compare representative old/new pages to confirm the same focal individual and core direct family relationships are represented.
- [R-4] Verify tree meaning remains intact when viewed as plain preformatted text without color.
- [R-5] Verify focal-person styling, when present, is additive and does not replace textual identification.
- [R-6] Verify sparse-family pages still emit a non-empty minimal tree.

## Requirements Mapping

- [R-1] Replace the PlantUML tree emission path in `gen_site/gen_site.py` with generator-side text tree output, and remove the collapsible wrapper.
- [R-2] Build the new tree from the existing `Individual`/`Family` relationships already exposed by the model layer, keeping scope to direct parents, focal person, spouse families, and children.
- [R-3] Mirror the existing tree section's relationship coverage rather than introducing broader genealogical expansion.
- [R-4] Render the tree in a preformatted text block whose meaning does not depend on CSS color.
- [R-5] Add styling support for focal-person highlighting only.
- [R-6] Ensure the helper returns sensible output for sparse data and deterministic reduced output for over-wide multi-family cases.

## File Touchpoints

- `gen_site/gen_site.py` — replace the current `Boom` section emission and integrate the new tree helper.
- `gen_site/util/PlantUMLCreator.py` — likely source of current direct-family tree logic to mirror or partially replace; may be retired from page-tree usage after migration.
- `gen_site/model/Individual.py` — existing relationship traversal APIs used by the new tree helper.
- `gen_site/model/Family.py` — existing spouse/child structure used by the new tree helper.
- `src/styles/global.css` — add tree block overflow and focal-person styling.
- `gen_site/test/test_migration_contract.py` and/or new focused tests — validate generator output and representative page behavior.
