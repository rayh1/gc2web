# gc2web

Instructions for coding agents working in this repository. This file is the project's own:
the template wrote it once and never changes it, so edit it as the project grows.

## Commands

Run these in the dev container, from the repository root.

- `bash .devcontainer/check.sh` — install the dependencies, then run the project's checks.
  Run it before you call a change done, and fix what it reports.

## Where this project comes from

The dev container comes from the Copier template `tdp-template`. The project owner updates
it with `tdp update`, which runs `copier update`.

- The template's files are `.devcontainer/` (apart from the project's files below), `.vscode/`,
  `.gitignore`, `.gitattributes`, `.editorconfig`,
  `.dockerignore` and `.python-version`. A change to them can conflict with the
  next update: ask the project owner first.
- The project's own files are this file, `CLAUDE.md` (it imports this file for Claude Code),
  `README.md`, `pyproject.toml`,
  `package.json`,
  `osv-scanner.toml`, and in `.devcontainer/`: `check.sh` (the project's checks go below its
  marker line), `extra-packages.txt` (apt packages), `extra.sh` (a build hook) and
  `compose.extra.yaml` (extra services). `.devcontainer/README.md` explains them.
- Never edit `.copier-answers.yml`: Copier keeps it.
- Never run `tdp update` or `copier update` yourself.

## Decisions

Nothing recorded yet. List here what an agent must not change without asking the project owner.

## Architecture

Nothing recorded yet.

## Tests

Nothing recorded yet.
