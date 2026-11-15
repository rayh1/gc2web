#!/usr/bin/env bash
# Check one download against its pin from .devcontainer/.env, before the image build uses it:
#
#   bash verify-download.sh <file> <pinned value> <name>
#
# A <name> ending in `-key` is an apt signing key: the file must hold exactly one primary key, and
# that key's fingerprint must be the pinned 40-hex-character fingerprint. Any other <name> is a tool
# download: the file's SHA-256 must be the pinned 64-hex-character hash. On a mismatch, an empty pin
# or a pin of the wrong form, it prints one line, `checksum mismatch: <name>` or
# `signing key mismatch: <name>`, and exits 1. Template-owned: `copier update` rewrites it.
set -uo pipefail

file="${1:-}"
expected="${2:-}"
name="${3:-}"

if [ -z "$name" ]; then
  echo "usage: verify-download.sh <file> <pinned value> <name>" >&2
  exit 2
fi

case "$name" in
  *-key)
    fail() { echo "signing key mismatch: ${name}" >&2; exit 1; }
    [[ "$expected" =~ ^[0-9A-Fa-f]{40}$ ]] || fail
    [ -f "$file" ] || fail
    home=$(mktemp -d) || fail
    # Every primary key in the file, each with the fingerprint record that follows it.
    listing=$(GNUPGHOME="$home" gpg --batch --show-keys --with-colons --with-fingerprint "$file" 2> /dev/null)
    rc=$?
    rm -rf "$home"
    [ "$rc" = 0 ] || fail
    primaries=$(printf '%s\n' "$listing" | awk -F: '
      $1 == "pub" || $1 == "sec" { primary = 1; next }
      $1 == "fpr" && primary { print $10; primary = 0; next }
      $1 != "fpr" { primary = 0 }')
    [ "$(printf '%s\n' "$listing" | grep -cE '^(pub|sec):')" = 1 ] || fail
    [ "$(printf '%s' "$primaries" | tr '[:lower:]' '[:upper:]')" = "$(printf '%s' "$expected" | tr '[:lower:]' '[:upper:]')" ] || fail
    ;;
  *)
    fail() { echo "checksum mismatch: ${name}" >&2; exit 1; }
    [[ "$expected" =~ ^[0-9A-Fa-f]{64}$ ]] || fail
    [ -f "$file" ] || fail
    actual=$(sha256sum "$file" | cut -d ' ' -f 1) || fail
    [ "$actual" = "$(printf '%s' "$expected" | tr '[:upper:]' '[:lower:]')" ] || fail
    ;;
esac
