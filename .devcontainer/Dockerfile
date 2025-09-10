FROM ubuntu:24.04

ARG ARG_NODE_VERSION
ARG ARG_UV_VERSION

WORKDIR /workspaces

# Install some utilities and full Python3
RUN apt-get update && \
    apt-get install -y --no-install-recommends wget sudo git vim curl gpg gnupg apt-transport-https ca-certificates lsb-release unzip dos2unix python3-full && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install uv (specific version)
RUN curl -LsSf https://astral.sh/uv/${ARG_UV_VERSION}/install.sh | sh && \
    mv /root/.cargo/bin/uv /usr/local/bin/uv && \
    mv /root/.cargo/bin/uvx /usr/local/bin/uvx

# Install Nodejs
RUN curl -fsSL https://deb.nodesource.com/setup_${ARG_NODE_VERSION}.x | sudo -E bash - && \
    apt-get install -y nodejs

# Install Github client
RUN mkdir -p -m 755 /etc/apt/keyrings && \
    wget -qO /etc/apt/keyrings/githubcli-archive-keyring.gpg https://cli.github.com/packages/githubcli-archive-keyring.gpg && \
    chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" > /etc/apt/sources.list.d/github-cli.list && \
    apt-get update && apt-get install -y --no-install-recommends gh && \
    apt-get clean && rm -rf /var/lib/apt/lists/*    

COPY app/* .

# Create Python environment with uv and install required Python dependencies
RUN uv venv venv && \
    uv pip install --python venv -r requirements.txt

# Set up environment to use the uv virtual environment
ENV PATH="/workspaces/venv/bin:$PATH"
ENV VIRTUAL_ENV="/workspaces/venv"

# Prepare scripts
RUN dos2unix init.sh && \
    chmod a+x init.sh

CMD ["/bin/bash"]
