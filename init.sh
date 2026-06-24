#!/bin/bash

# GitHub authentication — inherit host gh config on first run, then skip auth if already authenticated
if [ -d /tmp/host-gh-config ] && [ ! -d "$HOME/.config/gh" ]; then
  mkdir -p "$HOME/.config"
  cp -r /tmp/host-gh-config "$HOME/.config/gh"
  chmod -R go-rwx "$HOME/.config/gh"
fi

if gh auth status >/dev/null 2>&1; then
  echo "✓ gh already authenticated as $(gh api user --jq .login 2>/dev/null || echo unknown)"
else
  echo "gh not authenticated. Running gh auth login..."
  gh auth login
  if [ $? -ne 0 ]; then
    echo "Authentication failed. Please try again."
    exit 1
  fi
fi

cd /workspace

# Initialize Python project with uv (if pyproject.toml exists)
if [ -f "pyproject.toml" ]; then
  echo "Initializing Python project..."
  uv sync
fi

# Install the gedq CLI from the vendored wheel (used by gen_site to query the GEDCOM).
# Launcher is placed on PATH (/opt/venv/bin); the tool's own env stays isolated.
gedq_wheel="$(ls vendor/gedq-*.whl 2>/dev/null | head -1)"
if [ -n "$gedq_wheel" ]; then
  echo "Installing gedq CLI from $gedq_wheel..."
  UV_TOOL_BIN_DIR=/opt/venv/bin uv tool install --force "$gedq_wheel"
fi

# Install Node.js dependencies (if package.json exists)
if [ -f "package.json" ]; then
  echo "Installing Node.js dependencies..."
  npm install
fi

# Configure git user — inherit from host if unset in container, then prompt only if still unset
current_name="$(git config --global --get user.name || true)"
current_email="$(git config --global --get user.email || true)"

if [ -z "$current_name" ] && [ -f /tmp/host-gitconfig ]; then
  host_name="$(git config --file /tmp/host-gitconfig --get user.name 2>/dev/null || true)"
  if [ -n "$host_name" ]; then
    git config --global user.name "$host_name"
    current_name="$host_name"
    echo "Inherited git user.name from host: $host_name"
  fi
fi

if [ -z "$current_email" ] && [ -f /tmp/host-gitconfig ]; then
  host_email="$(git config --file /tmp/host-gitconfig --get user.email 2>/dev/null || true)"
  if [ -n "$host_email" ]; then
    git config --global user.email "$host_email"
    current_email="$host_email"
    echo "Inherited git user.email from host: $host_email"
  fi
fi

if [ -z "$current_name" ]; then
  read -r -p "Git global user.name is not set. Enter your full name: " user_name
  while [ -z "$user_name" ]; do
    read -r -p "Name cannot be empty. Enter your full name: " user_name
  done
  git config --global user.name "$user_name"
  echo "Set git global user.name to '$user_name'"
else
  echo "Git global user.name already set to '$current_name'"
fi

if [ -z "$current_email" ]; then
  read -r -p "Git global user.email is not set. Enter your email: " user_email
  while ! echo "$user_email" | grep -q -E '^[^@[:space:]]+@[^@[:space:]]+\.[^@[:space:]]+$'; do
    read -r -p "Please enter a valid email address (e.g. user@example.com): " user_email
  done
  git config --global user.email "$user_email"
  echo "Set git global user.email to '$user_email'"
else
  echo "Git global user.email already set to '$current_email'"
fi

echo "Environment ready for development!"
