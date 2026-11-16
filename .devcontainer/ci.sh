#!/usr/bin/env bash
# Run the project's checks the way CI does, on any host with Docker: build the dev-container image
# from the working tree with the pins in .devcontainer/.env, start the services of
# .devcontainer/compose.extra.yaml when it declares any, run .devcontainer/check.sh in a fresh
# container from that image, and remove the image and the services again, pass or fail. The exit
# code is check.sh's. Nothing is mounted from the host and the build cache is left alone.
#
# The run id names everything this script creates (image `ci-<id>`, compose project `ci-<id>`):
# $GITHUB_RUN_ID in CI, `local-<pid>` otherwise.
set -euo pipefail
cd "$(dirname "$0")/.."

run_id="${GITHUB_RUN_ID:-}"
if [ -z "$run_id" ]; then
  run_id="local-$$"
fi
name="ci-${run_id}"
extra=.devcontainer/compose.extra.yaml

# One build argument per pin: every line of .env that is neither blank nor a comment, in file order.
build_args=()
while IFS= read -r line || [ -n "$line" ]; do
  line="${line%$'\r'}"
  line="${line#"${line%%[![:space:]]*}"}"
  line="${line%"${line##*[![:space:]]}"}"
  if [ -z "$line" ] || [ "${line:0:1}" = "#" ]; then
    continue
  fi
  build_args+=(--build-arg "$line")
done < .devcontainer/.env

services=0
cleanup() {
  local rc=$?
  trap - EXIT
  if [ "$services" = 1 ]; then
    docker compose -f "$extra" -p "$name" down -v || true
  fi
  docker image rm "$name" > /dev/null 2>&1 || true
  exit "$rc"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
trap 'exit 129' HUP

docker build -f .devcontainer/Dockerfile --label tdp-ci -t "$name" "${build_args[@]}" .

network=()
if [ -f "$extra" ] && grep -qvE '^[[:space:]]*(#|$)' "$extra"; then
  services=1
  docker compose -f "$extra" -p "$name" down -v
  docker compose -f "$extra" -p "$name" up -d --wait
  network=(--network "${name}_default")
fi

rc=0
docker run --rm --label tdp-ci "${network[@]}" "$name" bash .devcontainer/check.sh || rc=$?
exit "$rc"
