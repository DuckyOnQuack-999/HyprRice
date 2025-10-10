# Base image with Ubuntu for general VM development
FROM ubuntu:22.04

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Update package lists and install essential development tools
RUN apt-get update && apt-get install -y \
    # Basic system utilities
    curl \
    wget \
    git \
    unzip \
    zip \
    tar \
    gzip \
    ca-certificates \
    software-properties-common \
    apt-transport-https \
    gnupg \
    lsb-release \
    # Development essentials
    build-essential \
    cmake \
    make \
    gcc \
    g++ \
    clang \
    # Text editors and tools
    vim \
    nano \
    emacs \
    # Version control and collaboration
    git-lfs \
    # Networking tools
    net-tools \
    iputils-ping \
    telnet \
    # Process and system monitoring
    htop \
    tree \
    jq \
    # Python development
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    # Additional utilities
    sudo \
    less \
    man \
    # Clean up package cache
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js (using NodeSource repository for latest LTS)
RUN curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install additional development tools via pip
RUN pip3 install --no-cache-dir \
    pip \
    setuptools \
    wheel \
    virtualenv

# Create a non-root user for security
RUN groupadd -g 1000 developer && \
    useradd -m -s /bin/bash -u 1000 -g developer developer && \
    usermod -aG sudo developer && \
    echo "developer ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Set the working directory to the user's home
WORKDIR /home/developer

# Set environment variables
ENV HOME=/home/developer
ENV USER=developer
ENV SHELL=/bin/bash

# Switch to the non-root user
USER developer

# Set up shell environment
RUN echo 'export PS1="\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ "' >> ~/.bashrc && \
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc

# Install useful development tools for the user
RUN npm install -g --unsafe-perm \
    typescript \
    ts-node \
    nodemon \
    eslint \
    prettier \
    @types/node \
    yarn \
    pnpm

# Create common development directories
RUN mkdir -p ~/projects ~/bin ~/.local/bin

# Set up git configuration template
RUN git config --global init.defaultBranch main && \
    git config --global core.autocrlf input

# Add a simple health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD echo "VM is running" || exit 1

# Expose common development ports (can be overridden)
EXPOSE 3000 3001 5000 8000 8080 9000

# Set default command with proper shell initialization
CMD ["/bin/bash", "--login"]
