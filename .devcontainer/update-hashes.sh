#!/usr/bin/env bash
# Rewrite the SHA-256 hash pins of a pin file from the tools' upstreams, after a version bump:
#
#   bash .devcontainer/update-hashes.sh [pin file]     (default: .devcontainer/.env)
#
# The pin file is a project's .devcontainer/.env (`KEY=value` lines) or the template's copier.yml
# `pins` (`KEY: "value"` lines). For every hash pin present in the file, the script reads the tool's
# version pin from the same file and fetches that release's published checksum for amd64 and arm64.
# Maven publishes only a SHA-512 and the Android command-line tools only a SHA-1: for those two the
# file is downloaded, checked against that checksum, and its SHA-256 computed. Only hash pins change;
# version pins, the signing-key fingerprint pins (a key change is for a person to check) and every
# other line stay as they are. Needs internet. When any fetch or check fails, it exits non-zero and
# leaves the file unchanged. Template-owned: `copier update` rewrites it.
set -euo pipefail

file="${1:-$(dirname "$0")/.env}"
if [ ! -f "$file" ]; then
  echo "update-hashes.sh: no pin file $file" >&2
  exit 2
fi

work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT

die() {
  echo "update-hashes.sh: $*; $file left unchanged" >&2
  exit 1
}

# has KEY: the file holds a pin line for KEY.
has() {
  grep -qE "^[[:space:]]*$1(=|:)" "$file"
}

# pin KEY: KEY's value in the file, from `KEY=value` or `KEY: "value"`.
pin() {
  local value
  value=$(sed -nE "s/^[[:space:]]*$1(=|:[[:space:]]*)\"?([^\"[:space:]]*)\"?[[:space:]]*\$/\\2/p" "$file" | head -n 1)
  [ -n "$value" ] || die "no $1 in the pin file"
  printf '%s' "$value"
}

fetch() {
  curl -fsSL --retry 3 -o "$2" "$1" || die "cannot fetch $1"
}

# listed SUMS NAME: the hash a checksum list gives for the file NAME.
listed() {
  local found
  found=$(awk -v name="$2" '{ f = $2; sub(/^\*/, "", f) } f == name { print $1 }' "$1" | sort -u)
  [[ "$found" =~ ^[0-9a-fA-F]{64}$ ]] || die "no single SHA-256 for $2 in its checksum list"
  printf '%s' "$found" | tr '[:upper:]' '[:lower:]'
}

declare -A hashes=()
any() {
  local key
  for key in "$@"; do
    if has "$key"; then return 0; fi
  done
  return 1
}

if any UV_SHA256_AMD64 UV_SHA256_ARM64; then
  v=$(pin UV_VERSION)
  for arch in amd64 arm64; do
    case "$arch" in amd64) target=x86_64 ;; arm64) target=aarch64 ;; esac
    name="uv-${target}-unknown-linux-gnu.tar.gz"
    fetch "https://releases.astral.sh/github/uv/releases/download/${v}/${name}.sha256" "$work/sums"
    hashes[UV_SHA256_${arch^^}]=$(listed "$work/sums" "$name")
  done
fi

if any TEA_SHA256_AMD64 TEA_SHA256_ARM64; then
  v=$(pin TEA_VERSION)
  for arch in amd64 arm64; do
    fetch "https://dl.gitea.com/tea/${v}/tea-${v}-linux-${arch}.sha256" "$work/sums"
    hashes[TEA_SHA256_${arch^^}]=$(listed "$work/sums" "tea-${v}-linux-${arch}")
  done
fi

if any GH_SHA256_AMD64 GH_SHA256_ARM64; then
  v=$(pin GH_VERSION)
  fetch "https://github.com/cli/cli/releases/download/v${v}/gh_${v}_checksums.txt" "$work/sums"
  for arch in amd64 arm64; do
    hashes[GH_SHA256_${arch^^}]=$(listed "$work/sums" "gh_${v}_linux_${arch}.tar.gz")
  done
fi

if any OSV_SCANNER_SHA256_AMD64 OSV_SCANNER_SHA256_ARM64; then
  v=$(pin OSV_SCANNER_VERSION)
  fetch "https://github.com/google/osv-scanner/releases/download/v${v}/osv-scanner_SHA256SUMS" "$work/sums"
  for arch in amd64 arm64; do
    hashes[OSV_SCANNER_SHA256_${arch^^}]=$(listed "$work/sums" "osv-scanner_linux_${arch}")
  done
fi

if any MAVEN_SHA256; then
  v=$(pin MAVEN_VERSION)
  url="https://archive.apache.org/dist/maven/maven-${v%%.*}/${v}/binaries/apache-maven-${v}-bin.tar.gz"
  fetch "${url}.sha512" "$work/maven.sha512"
  published=$(awk 'NR == 1 { print tolower($1) }' "$work/maven.sha512")
  [[ "$published" =~ ^[0-9a-f]{128}$ ]] || die "no SHA-512 in ${url}.sha512"
  fetch "$url" "$work/maven.tar.gz"
  [ "$(sha512sum "$work/maven.tar.gz" | cut -d ' ' -f 1)" = "$published" ] \
    || die "the Maven download does not match its published SHA-512"
  hashes[MAVEN_SHA256]=$(sha256sum "$work/maven.tar.gz" | cut -d ' ' -f 1)
  rm -f "$work/maven.tar.gz"
fi

if any FLUTTER_SHA256; then
  v=$(pin FLUTTER_VERSION)
  fetch "https://storage.googleapis.com/flutter_infra_release/releases/releases_linux.json" "$work/flutter.json"
  found=$(jq -r --arg archive "stable/linux/flutter_linux_${v}-stable.tar.xz" \
    '[.releases[] | select(.archive == $archive) | .sha256] | unique | if length == 1 then .[0] else "" end' \
    "$work/flutter.json") || die "cannot read releases_linux.json"
  [[ "$found" =~ ^[0-9a-fA-F]{64}$ ]] || die "no single sha256 for Flutter ${v} in releases_linux.json"
  hashes[FLUTTER_SHA256]=$(printf '%s' "$found" | tr '[:upper:]' '[:lower:]')
fi

if any ANDROID_CMDLINE_TOOLS_SHA256; then
  v=$(pin ANDROID_CMDLINE_TOOLS_VERSION)
  name="commandlinetools-linux-${v}_latest.zip"
  fetch "https://dl.google.com/android/repository/repository2-3.xml" "$work/repository.xml"
  published=$(tr -d '\r\n' < "$work/repository.xml" \
    | grep -oE "<checksum type=\"sha1\">[0-9a-fA-F]{40}</checksum>[[:space:]]*<url>${name}</url>" \
    | grep -oE '[0-9a-fA-F]{40}' | tr '[:upper:]' '[:lower:]' | sort -u || true)
  [[ "$published" =~ ^[0-9a-f]{40}$ ]] || die "no single SHA-1 for ${name} in repository2-3.xml"
  fetch "https://dl.google.com/android/repository/${name}" "$work/cmdline-tools.zip"
  [ "$(sha1sum "$work/cmdline-tools.zip" | cut -d ' ' -f 1)" = "$published" ] \
    || die "the Android command-line tools download does not match its published SHA-1"
  hashes[ANDROID_CMDLINE_TOOLS_SHA256]=$(sha256sum "$work/cmdline-tools.zip" | cut -d ' ' -f 1)
  rm -f "$work/cmdline-tools.zip"
fi

# Every hash is in hand: rewrite the hash pins of a copy, then the file itself in one go.
cp "$file" "$work/pins"
for key in $(printf '%s\n' "${!hashes[@]}" | sort); do
  if ! has "$key"; then
    continue
  fi
  value=${hashes[$key]}
  sed -i -E \
    -e "s/^([[:space:]]*${key}=)[^[:space:]]*/\\1${value}/" \
    -e "s/^([[:space:]]*${key}:[[:space:]]*)\"[^\"]*\"/\\1\"${value}\"/" \
    -e "s/^([[:space:]]*${key}:[[:space:]]*)[^\"[:space:]][^[:space:]]*/\\1${value}/" \
    "$work/pins"
  echo "${key}=${value}"
done
cat "$work/pins" > "$file"
