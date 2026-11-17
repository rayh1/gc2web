# The gc2web dev container

Ten-Day Project (python, node) rendered from the `tdp-template` copier template. Python
is part of every project; the other languages come from the `languages` answer in
`.copier-answers.yml`.

This file belongs to the template and `copier update` keeps it current. The project's own
documentation belongs in the top-level `README.md`, which the template never overwrites.

## Getting started

1. Open this folder in VS Code and choose **Reopen in Container**. The image builds from
   `.devcontainer/Dockerfile` with the versions pinned in `.devcontainer/.env`. On create,
   `bash .devcontainer/update.sh` syncs the dependencies and runs `bash .devcontainer/devkit.sh`,
   which installs Charm's DevKit (skills, prompts and docs) and the Codex CLI and Copilot CLI.
   wo-cli, the WebOffice CLI, is not installed in this container.
   The first create writes the lockfiles — `uv.lock` and, for a node project, `package-lock.json`
   — into the workspace: commit and push them, so every later create installs the same versions.
2. Git identity, the Codex login and the gh login are copied from the host on every attach.
3. **Sync Dependencies** runs `bash .devcontainer/update.sh`; **Refresh DevKit** runs
   `bash .devcontainer/devkit.sh` again. Every hook and task runs its script through `bash`, so
   a checkout without the executable bit (Windows cannot store it) works too; `.gitattributes`
   keeps the scripts and the Dockerfile on LF whatever `core.autocrlf` says.

## Logins that stay manual

- `tea` (the Gitea CLI) is installed without a login; log in by hand with `tea login add` when
  you need it.
- Copilot CLI: `copilot login`, unless `GH_TOKEN` is set on the host.

## The workspace is a named volume

`/workspace` inside the container is a Docker named volume seeded from the image, not a mount of
this folder. Edits inside the container do not reach the host folder; push your branches to
the remote to get work out. `docker compose down -v` deletes the volume and with it all work that
was not pushed. A plain `docker compose down` (or VS Code's rebuild) keeps it.

Package caches (`uv`, `npm`) and shell history also
live in named volumes and survive rebuilds. Nothing credential-like does: the `gh`, Codex and
Copilot logins live in the container's own filesystem and are gone after a container recreate.

## DevKit-managed content

`.github/` is DevKit's target directory (`.devcontainer/devkit.sh` passes
`--target-dir /workspace/.github`) and is ignored by git, as is `.agents/`, where the current
DevKit installer places the skills and docs. Both are rebuilt by **Refresh DevKit**; do not commit
them.

## Tools in the image

`uv` with a pinned CPython, Node, `gh`, Playwright with Chromium (browsers in `/opt/playwright`),
`tea`, `osv-scanner`, `git`, `jq`, `rg`.
`playwright-cli`, the browser command line, is there too, with its own Chromium in `/opt/playwright`:
`playwright-cli open --browser=chromium <url>` opens a page without a download.
The project's Python environment is `.venv` in the workspace, created by `uv sync` from
`.python-version`.

## Download checks

The image build checks every tool it downloads, and every apt signing key, against a pin in
`.devcontainer/.env` before using it (`.devcontainer/verify-download.sh` does the check): a tool's
archive or binary must match its SHA-256 hash pin, and a signing key file must hold exactly the
one key with the pinned fingerprint. A download that does not match stops the build with the line
`checksum mismatch: <name>` or `signing key mismatch: <name>`.

A version bump in `.devcontainer/.env` needs the tool's hash pin updated as well, or the next
build stops at that download. After editing a version, run
`bash .devcontainer/update-hashes.sh` (it needs internet) in the dev container. It reads the
version pins, fetches each tool's published checksum for amd64 and arm64, and rewrites the hash
pins in `.devcontainer/.env`. It leaves the version pins and the signing-key fingerprints as they
are: a changed signing key is for a person to check. When a fetch or a check fails, it changes
nothing. Where each hash pin comes from, for a check by hand (`<version>` is the tool's version
pin, `<arch>` is `amd64` or `arm64` as in the pin's name):

- `UV_SHA256_AMD64`, `UV_SHA256_ARM64` — the file
  `https://releases.astral.sh/github/uv/releases/download/<version>/uv-<target>-unknown-linux-gnu.tar.gz.sha256`,
  where `<target>` is `x86_64` for amd64 and `aarch64` for arm64.
- `TEA_SHA256_AMD64`, `TEA_SHA256_ARM64` — the file
  `https://dl.gitea.com/tea/<version>/tea-<version>-linux-<arch>.sha256`.
- `GH_SHA256_AMD64`, `GH_SHA256_ARM64` — the `gh_<version>_linux_<arch>.tar.gz` line of
  `https://github.com/cli/cli/releases/download/v<version>/gh_<version>_checksums.txt`.
- `OSV_SCANNER_SHA256_AMD64`, `OSV_SCANNER_SHA256_ARM64` — the `osv-scanner_linux_<arch>` line of
  `https://github.com/google/osv-scanner/releases/download/v<version>/osv-scanner_SHA256SUMS`.

`NODESOURCE_KEY_FINGERPRINT` is the full fingerprint of the
signing key's primary key; `gpg --show-keys <key file>` prints it.

## Host files used by the container

The home directory is `HOME` on Linux and macOS and `USERPROFILE` on Windows (compose's
`${HOME:-${USERPROFILE}}` fallback in `.devcontainer/compose.yaml`); `~` below means that directory.

- `~/.gitconfig` (read-only): `user.name` and `user.email` are copied in when unset.
- `~/.codex` (read-only, the whole directory): its `auth.json` — the Codex login — is copied to
  `~/.codex/auth.json` in the container when that file exists and holds a login. A host without
  a Codex login ends up with an empty `.codex` directory, which is harmless.
- `~/.config/gh` (read-only): the gh login (`hosts.yml`) is copied in when present and the
  container has none.
- Environment: `GH_TOKEN` is passed through when set; `USER_UID`/`USER_GID`
  select the container user's ids (default `1000`). Compose lets shell variables override
  `.devcontainer/.env`, so a `NODE_VERSION` or `PYTHON_VERSION` exported in your shell would
  replace the pin; unset such variables before building.

## Checks and continuous integration

`.devcontainer/check.sh` is the project's check. It installs the dependencies with
`TDP_CI=1 bash .devcontainer/update.sh`, then runs the template's default checks,
`bash .devcontainer/default-checks.sh`, then the project's own checks. The default checks are
those of every language whose manifest is at the top of the repository: `uv run ruff check`,
`uv run ruff format --check --extend-exclude '*.md'` and `uv run pytest` for `pyproject.toml` (no
tests collected counts as a pass); `npm run check` for `package.json` when it has a `check`
script, otherwise `npm run lint` and `npm test` where present; `mvn -B verify` for `pom.xml`;
`flutter analyze`, `dart format --output=none --set-exit-if-changed .`, and `flutter test` when a
`test` folder exists, for `pubspec.yaml`; then the dependency scans described below. Every check
runs even when an earlier one fails, and each failure prints `==> FAILED: <command>`; the exit
code is 1 when any failed. A failing dependency install stops the run at once.

`.devcontainer/default-checks.sh` is template-owned: `copier update` rewrites it, so a default
check the template adds later reaches the project with the next update. Do not edit it.
`.devcontainer/check.sh` is project-owned and the place for the project's own checks: add each as
`check <command>` between the line `# The project's own checks go below this line.` and the final
`exit "$failed"` line; a check added after the `exit` line never runs. They run even when a
default check failed. A project that wants a different
default set edits or drops the `default-checks.sh` call in its `check.sh`.

In a project rendered from tdp-template v0.20.0 on, `check.sh` holds one such check from the
start: `uv run mypy`, strict type checking of the project's Python code, which fails as
`==> FAILED: uv run mypy`. The command takes no arguments: what mypy checks and how strictly is
set in the `[tool.mypy]` table of `pyproject.toml`, which the stub fills with `strict = true` and
`files = ["."]` (and `mypy` joins the `dev` dependency group). Narrow the files
(`files = ["src"]`), relax strictness or add overrides for the tests in that table, without
touching `check.sh`. The check is skipped, printing nothing, when `pyproject.toml` has no line
starting with `[tool.mypy` or `[[tool.mypy` (as after a starter brings its own `pyproject.toml`
without mypy settings), or when the project holds no Python file (`.py` or `.pyi`) outside the
folders mypy always skips: `node_modules`, `__pycache__`, `site-packages` and every folder whose
name starts with a dot, such as `.venv`. The `files` and `exclude` settings of `[tool.mypy]` do
not count for the skip: when they leave no Python file to check (`files = ["src"]` with no Python
file in `src/`, or an `exclude` that covers every Python file), the check runs and fails with
mypy's own message, such as `There are no .py[i] files in directory 'src'`. Change `files` or
`exclude` so that they take in a Python file, or remove the `[tool.mypy]` table (and any
`[[tool.mypy.overrides]]`) to turn the check off. A project rendered from an older release has
no mypy check, since `copier update` never touches `check.sh` or `pyproject.toml`; it adopts
mypy by adding a `[tool.mypy]` table to `pyproject.toml`, `mypy` to its `dev` dependency group,
and the line `check uv run mypy` to its `check.sh`.

`TDP_CI=1` makes `update.sh` skip the DevKit install, which the checks do not need.

The two format checks change no file: they fail when a file is not formatted the way
`uv run ruff format` or `dart format .` would write it, and running that command fixes it. The
Python format check leaves Markdown files out, so a Python example in the docs never fails it;
drop `--extend-exclude '*.md'` to check those too. Each tool takes its style from its own settings
(for example `[tool.ruff]` in `pyproject.toml`). Dart's style follows the language version: with
the seed's `sdk: ">=3.0.0 <4.0.0"` in `pubspec.yaml`, `dart format` writes the older short style.
Raising a Flutter project's SDK lower bound to 3.7 or later switches `dart format` to the tall
style, which reformats many of its files: the check fails until you run `dart format .`.

- In the dev container, the **Run Checks** task (the default test task) runs
  `bash .devcontainer/check.sh`.
- `.devcontainer/ci.sh` runs the same check the way CI does, on any host with Docker (not inside
  the dev container): it builds the image from the working tree with the pins in
  `.devcontainer/.env`, starts the services of `.devcontainer/compose.extra.yaml` when it
  declares any, runs `bash .devcontainer/check.sh` in a fresh container from that image, then
  removes the image and the services, pass or fail. Its exit code is the check's.
- This project has no CI workflow. To add one, run `bash .devcontainer/ci.sh` from your CI
  system's job on a host with Docker.

CI starts the services of `compose.extra.yaml` as a compose project of its own and runs the
checks on that project's network, so a check reaches each service by its service name (`db`,
port `5432`), the same as `main` does. A service declared there must therefore:

- publish container ports only (`"5432"`), never a fixed host mapping such as `"5432:5432"`,
  which collides with another run or project on the same host;
- set none of `networks:`, `network_mode:` and `container_name:`.

Give a service a `healthcheck` (the PostgreSQL example has one), so that CI's
`docker compose up --wait` returns only once the service accepts connections.

### Dependency scans

After the language checks, `osv-scanner` scans the dependencies each manifest resolved to, one
scan per manifest, for known vulnerabilities: `uv.lock` for `pyproject.toml`, `package-lock.json`
for `package.json`, `pubspec.lock` for `pubspec.yaml`, and for `pom.xml` a CycloneDX list of every
resolved dependency, test scope included, that the CycloneDX Maven plugin writes to
`target/bom.json` right before the scan (an old list is removed first). Each scan runs
`osv-scanner scan source --config osv-scanner.toml -L <lockfile>` and looks each exact package
version up in the OSV.dev vulnerability database. The scan reads whatever lockfile the install
left, committed or not; commit your lockfiles (`uv.lock`, `package-lock.json`, `pubspec.lock`), so
that every run and every machine scans the same versions.

Each scan sends the project's dependency names and versions (never its code) to Google's OSV.dev
web service, which answers with the matching advisories. There is no offline mode: when the
database cannot be reached, the scan fails.

Only osv-scanner's exit code decides the check, never its printed summary:

- `0`: packages were found and none has a known vulnerability; the scan passes.
- `1`: known vulnerabilities were found; the scan fails.
- `127`: a general error, such as a missing or broken lockfile, an unreachable database or a bad
  `osv-scanner.toml`; the scan fails.
- `128`: no packages were found. This passes only when the manifest declares no dependencies,
  and the output then says so, for example
  `==> package.json: no dependencies declared, nothing to scan`; a fresh node or java project
  passes this way. When the manifest does declare a dependency (or cannot be read), finding no
  packages fails the scan. A `pubspec.yaml` always counts as declaring, since every Flutter
  project depends on the Flutter SDK packages.
- Any other exit code fails the scan.

To accept a known risk, list its advisory in `osv-scanner.toml` at the top of the repository,
which every scan reads. An entry with an `ignoreUntil` date accepts the advisory until that date
and fails the scan again after it:

```toml
[[IgnoredVulns]]
id = "GHSA-xxxx-xxxx-xxxx"
ignoreUntil = 2027-01-31
reason = "Why the risk is accepted, who decided it, and when."
```

The rendered `osv-scanner.toml` holds this example commented out.

## Troubleshooting

- The container create fails with `all predefined address pools have been fully subnetted`:
  Docker has run out of subnets for compose networks. Remove networks of projects you no longer
  use (`docker network ls`, then `docker compose down` in that project), or give Docker a larger
  pool in Docker Desktop's engine settings (Settings > Docker Engine, the `default-address-pools`
  key, e.g. `"default-address-pools": [{"base": "10.201.0.0/16", "size": 24}]`) and restart Docker.

## Project-owned extension points

- `README.md` — the project's own README at the top of the repository: written once, a short
  stub to replace with the project's documentation.
- `AGENTS.md` and `CLAUDE.md` — instructions for coding agents at the top of the repository,
  written once. `AGENTS.md` is a stub for the project to fill in (a starter may bring its own);
  `CLAUDE.md` holds only the line `@AGENTS.md`, which makes Claude Code read `AGENTS.md`.
- `package.json` — the project's Node manifest at the top of the repository: written once from a
  stub, then the project's own to change or replace (a starter may bring its own). An update that
  drops node from the languages removes it.
- `pyproject.toml` — the project's Python manifest at the top of the repository: written once
  from a stub, then the project's own to change or replace (a starter may bring its own).
- `.devcontainer/extra-packages.txt` — apt packages, one per line, installed at image build.
- `.devcontainer/extra.sh` — runs as root at the end of the image build.
- `.devcontainer/compose.extra.yaml` — extra compose services next to `main` (a PostgreSQL
  database, an object store), with their volumes and ports. `compose.yaml` pulls it in through
  compose's `include`, so a service written there joins the project's network and is reachable
  from `main` by its service name. The rendered file is a commented-out PostgreSQL example.
- `.devcontainer/check.sh` — the project's checks, run by the **Run Checks** task and by
  `.devcontainer/ci.sh`: the call of the template-owned `.devcontainer/default-checks.sh`, then
  the project's own checks; see "Checks and continuous integration" above.
- `osv-scanner.toml` — the project's accepted vulnerability risks for the dependency scans, at
  the top of the repository: written once as a commented example; see "Dependency scans" above.
- `extra_extensions` in `.copier-answers.yml` — extra VS Code extension ids, comma-separated.
- `extra_dockerignore` in `.copier-answers.yml` — extra `.dockerignore` patterns, comma-separated
  (for example `work/, tmp/`): each becomes its own line of `.dockerignore`, after the template's
  own lines, so those paths stay out of the image build.
- `dropped_stubs` in `.copier-answers.yml` — the project-owned files above that the project
  deleted on purpose, as a list (for example `[/osv-scanner.toml]`). A template update writes a
  missing project-owned file again unless it is listed here. Set it once with
  `copier update --trust --data 'dropped_stubs=["/osv-scanner.toml"]'`.

`copier update` carries template changes into this project and never overwrites the
project-owned files above; it keeps the two answers and renders them again. To change an answer,
pass it to the update, for example `copier update --trust --data extra_dockerignore='work/, tmp/'`.
