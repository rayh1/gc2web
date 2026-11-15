#!/usr/bin/env bash
# Runs on every attach (postAttachCommand). Silent steps only, never a prompt:
#   1. copy user.name / user.email from the host's git config when unset here
#   2. copy the host's Codex login (~/.codex/auth.json, mounted as the directory ~/.codex) when present
#   3. copy the host's gh login (~/.config/gh) when present here and absent in the container
set -u

HOST_GITCONFIG="/tmp/host-gitconfig"
HOST_CODEX_DIR="/tmp/host-codex"
HOST_CODEX_AUTH="$HOST_CODEX_DIR/auth.json"
HOST_GH_CONFIG="/tmp/host-gh-config"

copy_git_identity() {
  [ -f "$HOST_GITCONFIG" ] || return 0
  local key value
  for key in user.name user.email; do
    if [ -z "$(git config --global --get "$key" 2>/dev/null || true)" ]; then
      value="$(git config -f "$HOST_GITCONFIG" --get "$key" 2>/dev/null || true)"
      [ -n "$value" ] && git config --global "$key" "$value"
    fi
  done
  return 0
}

copy_codex_auth() {
  # Only when the host file exists and is non-empty; otherwise $HOME/.codex is left untouched
  # (absent, when nothing else created it).
  { [ -f "$HOST_CODEX_AUTH" ] && [ -s "$HOST_CODEX_AUTH" ]; } || return 0
  mkdir -p "$HOME/.codex" \
    && cp "$HOST_CODEX_AUTH" "$HOME/.codex/auth.json" \
    && chmod 0600 "$HOME/.codex/auth.json"
  return 0
}

copy_gh_login() {
  # Only when the host has a gh login and this container has none yet; never overwrites.
  [ -f "$HOST_GH_CONFIG/hosts.yml" ] || return 0
  [ -e "$HOME/.config/gh/hosts.yml" ] && return 0
  local dest="$HOME/.config/gh"
  if mkdir -p "$dest" && cp -R "$HOST_GH_CONFIG/." "$dest/"; then
    chmod 0700 "$dest"
    find "$dest" -type f -exec chmod 0600 {} +
  else
    rm -rf "$dest"
  fi
  return 0
}

copy_git_identity
copy_codex_auth
copy_gh_login
