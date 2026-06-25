# ASCII Tree Pages PRD

## PRD Type

Functional

## Context

Generated individual entity pages currently show a PlantUML-based family tree near the top of the page inside a collapsible section. The requested change is to replace that tree with an always-visible ASCII-style family tree that is comparable in genealogical content to the tree `gedq` can produce, while fitting the existing generated page flow.

## Why

The current PlantUML rendering adds indirection, depends on an external diagram rendering flow, and hides the tree behind a collapsed affordance. Readers should be able to see a useful genealogical tree immediately when the page loads, without expanding anything and without relying on diagram output to understand the family structure.

## Goals

- Show an always-visible ASCII-style family tree on every generated individual entity page.
- Preserve the core family relationships currently conveyed by the page tree section.
- Make the tree readable on both color-capable and non-color-capable page renderings.
- Keep the tree positioned near the top of the page where the current tree section lives.

## Non-Goals

- Reproducing `gedq` tree formatting byte-for-byte.
- Introducing collapsible UI around the tree.
- Replacing other genealogical sections such as chronology, parents, relationships, or source lists.
- Requiring color in order to understand the tree.

## Requirements

1. [R-1] Each generated individual entity page must render a visible-by-default ASCII-style family tree near the top of the page in place of the current PlantUML tree section.
2. [R-2] The rendered tree must communicate the focal individual, direct parent relationship when available, spouse relationship when available, and child relationships when available.
3. [R-3] The tree must preserve the same core genealogical structure across generated pages as the existing page tree section, even if the formatting differs from PlantUML or `gedq` output.
4. [R-4] The tree presentation must remain readable when color styling is unavailable or not applied.
5. [R-5] When color styling is available, the tree may use functional color cues to improve readability without changing the underlying text content needed to understand the tree.
6. [R-6] Pages that do not have enough related people to form a larger tree must still render a sensible minimal tree representation rather than an empty or collapsed tree block.

## Acceptance Criteria

- [R-1] Generated individual entity pages no longer contain a collapsed PlantUML tree UI and instead show the replacement tree directly in the main page flow near the top of the page.
- [R-1] The replacement tree is present without any user interaction on initial page render.
- [R-2] For a person with known parents, the rendered tree identifies the direct parent-to-child relationship for the focal individual.
- [R-2] For a person with a spouse and children, the rendered tree identifies the spouse connection and the child connections.
- [R-2] For a person missing one or more relationship categories, the tree omits unavailable relationships without breaking the rest of the display.
- [R-3] For representative generated pages, the replacement tree reflects the same focal person and core direct family relationships that the current tree section represents.
- [R-3] Acceptance does not require byte-identical formatting to `gedq`, only comparable core relationship content.
- [R-4] The tree remains understandable using plain text alone, without relying on color to distinguish meaning.
- [R-4] If styling is removed or unsupported, the tree still shows the focal person and relationships in a legible text layout.
- [R-5] Any applied colors correspond to stable functional meaning such as relationship role or person type, rather than purely decorative variation.
- [R-5] Color styling does not remove or replace the textual cues required to interpret the tree.
- [R-6] A page with only the focal individual, or with only a partial set of relatives, still shows a minimal non-empty tree representation.

## Edge Cases

- [E-1] The focal individual has no recorded parents, spouse, or children.
- [E-2] Only one parent is known.
- [E-3] The focal individual has multiple families or multiple spouses.
- [E-4] The tree content is wider than the available mobile viewport.
- [E-5] Names or lifespan labels are long enough to affect ASCII alignment.

## Unknowns & Questions

None.

## Risks

- [K-1] A visually pleasing ASCII tree may still become hard to scan on narrow screens if relationship breadth is large.
- [K-2] Color cues could accidentally become semantic dependencies if the text layout is not strong enough on its own.
- [K-3] Existing pages with more complex family structures may expose layout edge cases that are not visible in simple examples.
