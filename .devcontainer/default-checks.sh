#!/usr/bin/env bash
# The template's default checks, run by .devcontainer/check.sh after the dependency install: the
# linters and tests of every language whose manifest is at the top of the repository, then one
# osv-scanner scan per manifest of the dependencies the install resolved. Every check runs even when
# an earlier one fails; each failure prints `==> FAILED: <command>`, and the exit code is 1 when any
# check failed and 0 when none did.
#
# This file is template-owned: `copier update` rewrites it. The project's own checks go in
# .devcontainer/check.sh, and accepted vulnerability risks in osv-scanner.toml.
set -uo pipefail
cd "$(dirname "$0")/.."

failed=0
check() {
  echo "==> $*"
  if ! "$@"; then
    echo "==> FAILED: $*"
    failed=1
    return 1
  fi
}

if [ -f pyproject.toml ]; then
  check uv run ruff check
  check uv run ruff format --check --extend-exclude '*.md'
  echo "==> uv run pytest"
  rc=0
  uv run pytest || rc=$?
  # Exit code 5 means pytest collected no tests: a project without tests passes.
  if [ "$rc" -ne 0 ] && [ "$rc" -ne 5 ]; then
    echo "==> FAILED: uv run pytest"
    failed=1
  fi
fi

if [ -f package.json ]; then
  if jq -e '.scripts | objects | has("check")' package.json > /dev/null 2>&1; then
    check npm run check
  else
    check npm run lint --if-present
    check npm test --if-present
  fi
fi

if [ -f pom.xml ]; then
  check mvn -B verify
fi

if [ -f pubspec.yaml ]; then
  check flutter analyze
  check dart format --output=none --set-exit-if-changed .
  if [ -d test ]; then
    check flutter test
  fi
fi

# --- Dependency scans ------------------------------------------------------------------------------
# osv-scanner looks each exact package version of a lockfile up in the OSV.dev database: it sends the
# package names and versions (never the code) to the OSV.dev service. Only its exit code decides:
#   0    packages found, no known vulnerability: passes;
#   1    known vulnerabilities found: fails;
#   127  general error (missing or broken lockfile, database unreachable, bad config): fails;
#   128  no packages found: passes only when the manifest declares no dependency, else fails;
#   any other code fails.
# Accepted risks are listed in osv-scanner.toml at the top of the repository.

# Reads pyproject.toml or pom.xml (the path in argv[1]) and prints `none` when it declares no
# dependency. Anything it cannot judge, an unparsable file included, counts as declaring.
manifest_parser=$(cat <<'PY'
import sys
import tomllib
import xml.etree.ElementTree as ET


def pyproject_declares(doc):
    project = doc.get("project", {})
    if project.get("dependencies", []) != []:
        return True
    dynamic = project.get("dynamic", [])
    if "dependencies" in dynamic or "optional-dependencies" in dynamic:
        return True
    if any(extra != [] for extra in project.get("optional-dependencies", {}).values()):
        return True
    if any(group != [] for group in doc.get("dependency-groups", {}).values()):
        return True
    return doc.get("tool", {}).get("uv", {}).get("dev-dependencies", []) != []


def pom_declares(root):
    # A parent POM can pass dependencies on; a <dependency> anywhere counts, comments never do.
    return any(isinstance(el.tag, str) and el.tag.rsplit("}", 1)[-1] in ("dependency", "parent")
               for el in root.iter())


path = sys.argv[1]
try:
    if path == "pom.xml":
        declares = pom_declares(ET.parse(path).getroot())
    else:
        with open(path, "rb") as f:
            declares = pyproject_declares(tomllib.load(f))
except Exception as error:
    print(f"{path}: {error}; counted as declaring dependencies", file=sys.stderr)
    declares = True
if not declares:
    print("none")
PY
)

# Succeeds only when the manifest ($1) clearly declares no dependency.
declares_none() {
  case "$1" in
    package.json)
      jq -e 'type == "object" and all(.dependencies, .devDependencies, .optionalDependencies,
             .peerDependencies; . == null or . == {})' package.json > /dev/null 2>&1 ;;
    pyproject.toml | pom.xml)
      # Through the Python that uv manages in the image (not every image has a system python3).
      [ "$(uv run --no-project --no-config python -I -c "$manifest_parser" "$1")" = none ] ;;
    *)
      return 1 ;;
  esac
}

# One scan of the lockfile ($2) that the manifest ($1) resolves to.
scan() {
  local manifest=$1 lockfile=$2 rc=0
  local command=(osv-scanner scan source --config osv-scanner.toml -L "$lockfile")
  echo "==> ${command[*]}"
  "${command[@]}" || rc=$?
  if [ "$rc" -eq 0 ]; then
    return 0
  fi
  if [ "$rc" -eq 128 ] && declares_none "$manifest"; then
    echo "==> $manifest: no dependencies declared, nothing to scan"
    return 0
  fi
  echo "==> FAILED: ${command[*]}"
  failed=1
}

if [ -f pyproject.toml ]; then
  scan pyproject.toml uv.lock
fi

if [ -f package.json ]; then
  scan package.json package-lock.json
fi

if [ -f pom.xml ]; then
  # Maven has no lockfile: the CycloneDX plugin writes the resolved dependencies, test scope
  # included, to target/bom.json. An old list is removed first, so it is never scanned.
  rm -f target/bom.json
  if check mvn -B -q org.cyclonedx:cyclonedx-maven-plugin:2.9.3:makeAggregateBom -DincludeTestScope=true; then
    scan pom.xml target/bom.json
  fi
fi

if [ -f pubspec.yaml ]; then
  scan pubspec.yaml pubspec.lock
fi

exit "$failed"
