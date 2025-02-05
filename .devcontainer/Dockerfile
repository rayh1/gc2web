FROM ubuntu:24.04

ARG ARG_NODE_VERSION

WORKDIR /workspaces

# Install some utilities and full Python3
RUN apt-get update && \
    apt-get install -y --no-install-recommends wget sudo git vim curl gpg gnupg apt-transport-https ca-certificates lsb-release unzip dos2unix python3-full && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

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

# Create Python venv and install required Python dependencies
RUN /usr/bin/python3 -m venv venv && \
    /workspaces/venv/bin/pip install -r requirements.txt

# Prepare scripts
RUN dos2unix init.sh && \
    chmod a+x init.sh

CMD ["/bin/bash"]
