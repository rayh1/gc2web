# gc2web

Generates a static genealogy website (Astro) from a GEDCOM file. GEDCOM parsing
and Markdown generation live in `gen_site/` (Python); the site is built from the
generated Markdown by Astro.

## Development

The dev container comes from tdp-template; `.devcontainer/README.md` describes it.
Open this folder in VS Code and choose **Reopen in Container**. On create it installs
the Python dependencies (gedq among them, from the wheel in `vendor/`) and the Node
dependencies.

- **Run Checks** (or `bash .devcontainer/ci.sh` on any host with Docker) runs ruff, the
  Python tests, `npm run check` (unit tests, site build, Playwright tests) and the
  osv-scanner dependency scans.
- The Astro dev server listens on port 3000; find its host port with
  `docker compose -f .devcontainer/compose.yaml port main 3000`.

## Getting Started

- Generate the Markdown corpus from a GEDCOM file: `uv run python gen_site/gen_site.py <file.ged>`
- Run the Astro dev server: `npm run dev`
- Build the static site: `npm run build`
