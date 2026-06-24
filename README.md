# gc2web

Generates a static genealogy website (Astro) from a GEDCOM file. GEDCOM parsing
and Markdown generation live in `gen_site/` (Python); the site is built from the
generated Markdown by Astro.

## Development

Open in VS Code with the Dev Containers extension:

1. Open this folder in VS Code
2. Click "Reopen in Container" when prompted
3. Wait for the container to build (`init.sh` runs automatically and installs Node + Python dependencies)

## Using without VS Code

The dev container works with plain Docker too:

- Start an interactive shell: `docker compose -f .devcontainer/compose.yaml run --rm main bash`
- After `docker compose up`, find the mapped host port for the Astro dev server: `docker compose -f .devcontainer/compose.yaml port main 4321`

## Getting Started

- Generate the Markdown corpus from a GEDCOM file: `python gen_site/gen_site.py <file.ged>`
- Run the Astro dev server: `npm run dev`
- Build the static site: `npm run build`
