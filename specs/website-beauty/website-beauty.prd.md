# Website Visual Refresh PRD

## PRD Type

functional

## Context

This site publishes genealogical content and search surfaces, but the current presentation prioritizes raw information over atmosphere, hierarchy, and visual cohesion. The requested effort is to make the site feel more beautiful across the homepage, entity pages, shared navigation, search results, typography, and mobile layouts, while remaining readable and fast.

## Why

A warmer, more polished presentation should make the archive feel more inviting and easier to explore. The redesign should help visitors understand the site's purpose faster, connect emotionally with the material, and move through dense genealogical information without losing clarity.

## Goals

- Establish a cohesive warm family-archive visual identity across the public site.
- Improve how visitors scan, orient themselves, and move between homepage, entity, and search experiences.
- Allow page structure and interaction changes where they materially improve comprehension or discovery.
- Preserve or improve readability, accessibility, responsiveness, and immediate usability on mobile and desktop.

## Non-Goals

- Replacing the Astro/Tailwind stack.
- Reworking the genealogy data model, content generation pipeline, or source data.
- Adding unrelated genealogy features purely to make the redesign feel more substantial.
- Shipping a visually richer experience that depends on blocking splash screens, autoplay media, or slower-feeling first views.

## Requirements

1. [R-1] The site shall present a consistent warm family-archive visual system across the homepage, shared navigation, search pages, and entity pages.
2. [R-2] The homepage shall communicate the site's purpose more clearly and guide visitors toward primary exploration actions without depending on prior site knowledge.
3. [R-3] Entity pages shall group and label genealogical information so visitors can quickly distinguish identity, relationships, key facts, and supporting source material.
4. [R-4] Search pages and results shall make it easier to interpret and compare results by presenting clearer hierarchy and more contextual cues for each result when that context exists.
5. [R-5] Shared navigation and layout patterns shall keep visitors oriented across desktop and mobile views, including clear access to home, search, and the current page context.
6. [R-6] The redesign shall preserve or improve accessibility and immediate readability, including visible focus states, legible text treatment, and content availability without waiting on decorative elements.
7. [R-7] If page structure or interaction patterns change, currently published content shall remain discoverable through equally clear or clearer replacement paths.

## Acceptance Criteria

- [R-1] Visual QA across the homepage, one entity page, one search page, and shared navigation confirms the same typography system, color palette, spacing logic, and surface treatment are applied as one cohesive visual language.
- [R-2] On desktop and mobile first view, the homepage shows the site purpose and at least two primary onward actions for exploration or search without requiring the visitor to infer where to start.
- [R-2] The homepage may add or reorder sections, but each top-level section has a distinct purpose and supports orientation, browsing, or search rather than decorative filler.
- [R-3] On an entity page, identity information, relationship context, key life facts, and source or citation material can each be located through explicit grouping or labeling without reading the entire page linearly.
- [R-4] Search results present enough visible context to distinguish similar entries when distinguishing data already exists in the content, such as relationship context, date, place, or other identifying metadata.
- [R-4] Search result layouts support quick comparison without forcing users to open each result before understanding why it may be relevant.
- [R-5] From every primary page type in scope, visitors can reach home, search, and the current page context on both desktop and mobile without dead ends or hidden-only navigation paths.
- [R-6] Primary content on homepage, entity pages, and search pages is readable on initial load without waiting for animations, overlays, or decorative assets to finish loading.
- [R-6] Interactive elements on redesigned pages have visible focus indication, and text remains legible at default zoom on mobile and desktop viewports.
- [R-7] If a prior entry point or content grouping is removed, the redesign provides a replacement path on the same page or via shared navigation that is at least as easy to find.

## Edge Cases

- [E-1] Entity pages with very sparse data must still feel intentional rather than visually broken or empty.
- [E-2] Entity pages with dense notes, sources, or relationship sections must remain scannable without collapsing into a wall of text.
- [E-3] Search results with many similar names must still expose enough context to support disambiguation when that context exists.
- [E-4] Mobile layouts must preserve orientation and readability even when page sections are reordered or condensed.

## Unknowns & Questions

None.

## Risks

- [K-1] A strong visual direction could reduce information density too far and make research tasks slower if hierarchy is favored over scan speed.
- [K-2] Broader page-structure changes could unintentionally hide familiar entry points for returning users if replacement paths are not obvious.
- [K-3] A richer aesthetic could create perceived-performance regressions if decorative treatment competes with immediate access to primary content.
