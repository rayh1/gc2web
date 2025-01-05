FROM ubuntu:24.04

ARG ARG_JDK_VERSION
ARG ARG_JDK_VENDOR
ARG ARG_MAVEN_VERSION
ARG ARG_NODE_VERSION

WORKDIR /workspaces

# Install some utilities and full Python3
RUN apt-get update && \
    apt-get install -y --no-install-recommends wget sudo git vim curl gpg gnupg apt-transport-https lsb-release unzip dos2unix python3-full && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Nodejs
RUN curl -fsSL https://deb.nodesource.com/setup_${ARG_NODE_VERSION}.x | sudo -E bash - && \
    apt install -y nodejs

# Install Java (build and runtime)
RUN wget -qO - https://packages.adoptium.net/artifactory/api/gpg/key/public | gpg --dearmor | tee /etc/apt/trusted.gpg.d/adoptium.gpg > /dev/null && \
    echo "deb https://packages.adoptium.net/artifactory/deb $(awk -F= '/^VERSION_CODENAME/{print$2}' /etc/os-release) main" | tee /etc/apt/sources.list.d/adoptium.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends ${ARG_JDK_VENDOR}-${ARG_JDK_VERSION}-jdk && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Maven
RUN wget https://dlcdn.apache.org/maven/maven-3/${ARG_MAVEN_VERSION}/binaries/apache-maven-${ARG_MAVEN_VERSION}-bin.tar.gz && \
    tar -xvf apache-maven-${ARG_MAVEN_VERSION}-bin.tar.gz && \
    mv apache-maven-${ARG_MAVEN_VERSION} /opt/maven && \
    rm apache-maven-${ARG_MAVEN_VERSION}-bin.tar.gz && \
    ln -s /opt/maven/bin/mvn /usr/bin/mvn

ENV M2_HOME=/opt/apache-maven-${ARG_MAVEN_VERSION}

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
