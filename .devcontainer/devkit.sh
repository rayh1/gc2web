#!/usr/bin/env bash
# Install or refresh Charm's DevKit: the skills, prompts and docs and the AI CLIs (Codex CLI,
# Copilot CLI). This call leaves out DevKit's --python-tools (wo-cli, the WebOffice CLI) and its
# --tooling (tea and playwright-cli, which the image already has). Runs on container create (from
# update.sh) and from the "Refresh DevKit" task. Never prompts. DevKit and its installs come from
# public repositories, so no login is needed.
set -euo pipefail
export GIT_TERMINAL_PROMPT=0
export CI=1

DEVKIT_URL="http://git.charm.nl:3000/Charm/DevKit"

if [ -d /tmp/DevKit ]; then
  git -C /tmp/DevKit pull
else
  git clone "$DEVKIT_URL" /tmp/DevKit
fi

uv run /tmp/DevKit/install.py --target-dir /workspace/.github --skills --prompts --docs --cli --codex --no-vscode-settings
