#!/usr/bin/env bash
# The project's checks: install the dependencies, run the template's default checks
# (.devcontainer/default-checks.sh: every language's linters and tests, then the dependency scans),
# then the project's own checks below the marker line. The "Run Checks" task runs this file in the
# dev container; CI runs it through .devcontainer/ci.sh in a fresh container from the project's
# image. Every check runs even when an earlier one fails; the exit code is 1 when any check failed
# and 0 when none did. A failing dependency install stops it at once.
#
# This file is project-owned: `copier update` never overwrites it. default-checks.sh is
# template-owned and follows template updates; to run a different default set, edit or drop its call.
set -uo pipefail
cd "$(dirname "$0")/.."

TDP_CI=1 bash .devcontainer/update.sh || exit $?

failed=0
check() {
  echo "==> $*"
  if ! "$@"; then
    echo "==> FAILED: $*"
    failed=1
  fi
}

bash .devcontainer/default-checks.sh || failed=1

# Add each check as `check <command>`, between the marker line and the final `exit` line: a check
# added after the `exit` line never runs.
# The project's own checks go below this line.

exit "$failed"
