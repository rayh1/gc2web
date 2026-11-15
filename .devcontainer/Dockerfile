FROM ubuntu:26.04

# Every version pin comes from .devcontainer/.env, through compose build.args or ci.sh's --build-arg.
ARG TARGETARCH
ARG PYTHON_VERSION
ARG UV_VERSION
ARG NODE_VERSION
ARG TEA_VERSION
ARG GH_VERSION
ARG OSV_SCANNER_VERSION
ARG PLAYWRIGHT_VERSION
ARG PLAYWRIGHT_CLI_VERSION
ARG DEBIAN_FRONTEND=noninteractive

ENV TZ=Europe/Amsterdam \
    LANG=C.UTF-8 \
    DO_NOT_TRACK=1 \
    NG_CLI_ANALYTICS=false \
    UV_PYTHON_INSTALL_DIR=/opt/uv/python \
    PLAYWRIGHT_BROWSERS_PATH=/opt/playwright \
    HISTFILE=/home/devuser/.bash_history_dir/.bash_history

# Upgrade the base image packages to pick up the latest security fixes
RUN apt-get update && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

# Base tooling
RUN apt-get update && apt-get install -y --no-install-recommends git ca-certificates curl wget jq ripgrep sudo unzip zip gpg bash-completion xz-utils less procps openssh-client tzdata nano vim tree bc rclone file \
    && ln -snf "/usr/share/zoneinfo/${TZ}" /etc/localtime && echo "${TZ}" > /etc/timezone \
    && install -d -m 0755 /etc/apt/keyrings \
    && rm -rf /var/lib/apt/lists/*

# The download check: each step below checks every file it downloads against its pin from
# .devcontainer/.env (a SHA-256 hash, or a signing key's fingerprint) before using it.
COPY .devcontainer/verify-download.sh /opt/tdp/verify-download.sh

# Node (NodeSource). The AI CLIs are not installed here: DevKit installs them on container create
# (.devcontainer/devkit.sh).
ARG NODESOURCE_KEY_FINGERPRINT
RUN curl -fsSL -o /tmp/nodesource.key https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key \
    && bash /opt/tdp/verify-download.sh /tmp/nodesource.key "${NODESOURCE_KEY_FINGERPRINT}" nodesource-key \
    && gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg /tmp/nodesource.key && rm /tmp/nodesource.key \
    && echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_${NODE_VERSION}.x nodistro main" > /etc/apt/sources.list.d/nodesource.list \
    && apt-get update && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

# Playwright: the npm package in the root-owned global prefix (/usr/local, on everyone's PATH) and
# Chromium's system libraries. The browser itself is downloaded later, as devuser, into /opt/playwright.
RUN npm install -g "playwright@${PLAYWRIGHT_VERSION}" \
    && npm cache clean --force \
    && apt-get update && playwright install-deps chromium \
    && rm -rf /var/lib/apt/lists/*

# playwright-cli, the browser command line (npm @playwright/cli), in the same global prefix; its own
# Chromium (playwright-cli brings a newer Playwright) is downloaded later, as devuser, by playwright-cli.
RUN npm install -g "@playwright/cli@${PLAYWRIGHT_CLI_VERSION}" && npm cache clean --force

# uv (uv and uvx), from its release archive
ARG UV_SHA256_AMD64
ARG UV_SHA256_ARM64
RUN case "${TARGETARCH}" in \
      (amd64) uv_target=x86_64 uv_sha256="${UV_SHA256_AMD64}" ;; \
      (arm64) uv_target=aarch64 uv_sha256="${UV_SHA256_ARM64}" ;; \
    esac \
    && curl -fsSL -o /tmp/uv.tar.gz "https://releases.astral.sh/github/uv/releases/download/${UV_VERSION}/uv-${uv_target}-unknown-linux-gnu.tar.gz" \
    && bash /opt/tdp/verify-download.sh /tmp/uv.tar.gz "${uv_sha256:-}" uv \
    && tar -xzf /tmp/uv.tar.gz -C /tmp \
    && install -m 0755 "/tmp/uv-${uv_target}-unknown-linux-gnu/uv" "/tmp/uv-${uv_target}-unknown-linux-gnu/uvx" /usr/local/bin \
    && rm -rf /tmp/uv.tar.gz "/tmp/uv-${uv_target}-unknown-linux-gnu"

# The Gitea CLI (tea) and the GitHub CLI (gh)
ARG TEA_SHA256_AMD64
ARG TEA_SHA256_ARM64
ARG GH_SHA256_AMD64
ARG GH_SHA256_ARM64
RUN case "${TARGETARCH}" in \
      (amd64) tea_sha256="${TEA_SHA256_AMD64}" gh_sha256="${GH_SHA256_AMD64}" ;; \
      (arm64) tea_sha256="${TEA_SHA256_ARM64}" gh_sha256="${GH_SHA256_ARM64}" ;; \
    esac \
    && curl -fsSL -o /tmp/tea "https://dl.gitea.com/tea/${TEA_VERSION}/tea-${TEA_VERSION}-linux-${TARGETARCH}" \
    && bash /opt/tdp/verify-download.sh /tmp/tea "${tea_sha256:-}" tea \
    && install -m 0755 /tmp/tea /usr/local/bin/tea && rm /tmp/tea \
    && curl -fsSL -o /tmp/gh.tar.gz "https://github.com/cli/cli/releases/download/v${GH_VERSION}/gh_${GH_VERSION}_linux_${TARGETARCH}.tar.gz" \
    && bash /opt/tdp/verify-download.sh /tmp/gh.tar.gz "${gh_sha256:-}" gh \
    && tar -xzf /tmp/gh.tar.gz -C /tmp \
    && install -m 0755 "/tmp/gh_${GH_VERSION}_linux_${TARGETARCH}/bin/gh" /usr/local/bin/gh \
    && rm -rf /tmp/gh.tar.gz "/tmp/gh_${GH_VERSION}_linux_${TARGETARCH}"

# osv-scanner, for the dependency scans of .devcontainer/default-checks.sh
ARG OSV_SCANNER_SHA256_AMD64
ARG OSV_SCANNER_SHA256_ARM64
RUN case "${TARGETARCH}" in \
      (amd64) osv_scanner_sha256="${OSV_SCANNER_SHA256_AMD64}" ;; \
      (arm64) osv_scanner_sha256="${OSV_SCANNER_SHA256_ARM64}" ;; \
    esac \
    && curl -fsSL -o "/tmp/osv-scanner_linux_${TARGETARCH}" "https://github.com/google/osv-scanner/releases/download/v${OSV_SCANNER_VERSION}/osv-scanner_linux_${TARGETARCH}" \
    && bash /opt/tdp/verify-download.sh "/tmp/osv-scanner_linux_${TARGETARCH}" "${osv_scanner_sha256:-}" osv-scanner \
    && install -m 0755 "/tmp/osv-scanner_linux_${TARGETARCH}" /usr/local/bin/osv-scanner \
    && rm "/tmp/osv-scanner_linux_${TARGETARCH}"

# Project-owned extra apt packages (.devcontainer/extra-packages.txt, one name per line)
COPY .devcontainer/extra-packages.txt /tmp/extra-packages.txt
RUN if grep -qvE '^\s*(#|$)' /tmp/extra-packages.txt; then apt-get update && grep -vE '^\s*(#|$)' /tmp/extra-packages.txt | xargs apt-get install -y --no-install-recommends && rm -rf /var/lib/apt/lists/*; fi \
    && rm /tmp/extra-packages.txt

# Non-root user with the host's UID/GID; the stock ubuntu account is removed.
# The group is only named devuser when USER_GID is free in the base image (GID 100 is already
# `users`), so ownership below is set by number, never by the group name.
ARG USER_UID=1000
ARG USER_GID=1000
RUN userdel -r ubuntu \
    && (getent group "${USER_GID}" > /dev/null || groupadd -g "${USER_GID}" devuser) \
    && useradd -m -u "${USER_UID}" -g "${USER_GID}" -s /bin/bash devuser \
    && echo 'devuser ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/devuser && chmod 0440 /etc/sudoers.d/devuser \
    && install -d -o "${USER_UID}" -g "${USER_GID}" /opt/uv /opt/playwright \
    && install -d /opt/tdp \
    && printf '%s\n' 'export PATH="${HOME}/.local/bin:${PATH}"' > /etc/profile.d/tdp-path.sh
ENV PATH=/home/devuser/.local/bin:${PATH}:/usr/local/games:/usr/games
# DevKit's `npm install -g` runs as devuser and lands its binaries in /home/devuser/.local/bin.
ENV NPM_CONFIG_PREFIX=/home/devuser/.local

USER devuser
WORKDIR /home/devuser

# uv-managed CPython lives in the image (/opt/uv/python), not in the persisted uv data volume.
# The persisted cache directories are created here so the named volumes inherit devuser ownership.
RUN uv python install "${PYTHON_VERSION}" \
    && install -d /home/devuser/.cache/uv /home/devuser/.local/share/uv /home/devuser/.npm /home/devuser/.bash_history_dir /home/devuser/.local/bin \
    && printf '%s\n' 'export HISTFILE=/home/devuser/.bash_history_dir/.bash_history' "export PROMPT_COMMAND='history -a'" >> /home/devuser/.bashrc

# Chromium for Playwright, downloaded as devuser into PLAYWRIGHT_BROWSERS_PATH (/opt/playwright)
RUN playwright install chromium
# playwright-cli's Chromium, downloaded as devuser into the same folder, for playwright-cli's Playwright
RUN playwright-cli install-browser chromium

# Project-owned build hook, run as root at the end of the image build
USER root
COPY .devcontainer/extra.sh /tmp/extra.sh
RUN bash /tmp/extra.sh && rm /tmp/extra.sh

# Seed the workspace volume from the project (including .git). The hook scripts get the executable
# bit here, whatever the build context carried (a Windows checkout cannot store it).
COPY --chown=${USER_UID}:${USER_GID} . /workspace
RUN chmod 0755 /workspace/.devcontainer/*.sh
USER devuser
WORKDIR /workspace
