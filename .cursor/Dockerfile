# Dockerfile for HyprRice Background Agents
# Based on Cursor documentation: https://cursor.com/environment-json-dockerfile.md

FROM ubuntu:22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

# Install system dependencies and development tools
RUN apt-get update && apt-get install -y \
    # Essential build tools
    build-essential \
    git \
    curl \
    wget \
    ca-certificates \
    gnupg \
    lsb-release \
    software-properties-common \
    # Shell and terminal tools
    zsh \
    bash \
    fish \
    tmux \
    vim \
    nano \
    htop \
    tree \
    jq \
    yq \
    # Development tools
    python3 \
    python3-pip \
    python3-venv \
    nodejs \
    npm \
    # File system tools
    rsync \
    zip \
    unzip \
    tar \
    # Network tools
    net-tools \
    iputils-ping \
    dnsutils \
    # Text processing
    grep \
    sed \
    awk \
    # GUI tools (for desktop environment development)
    x11-utils \
    xvfb \
    # Hyprland specific tools
    meson \
    ninja-build \
    cmake \
    pkg-config \
    libgl1-mesa-dev \
    libglu1-mesa-dev \
    libxcb-randr0-dev \
    libxcb-util0-dev \
    libxcb-icccm4-dev \
    libxcb-keysyms1-dev \
    libxcb-image0-dev \
    libxcb-shm0-dev \
    libxcb-xfixes0-dev \
    libxcb-xkb-dev \
    libxkbcommon-dev \
    libxkbcommon-x11-dev \
    libxcb-cursor-dev \
    libxcb-xinerama0-dev \
    libxcb-ewmh-dev \
    libxcb-util-dev \
    libxcb-composite0-dev \
    libxcb-damage0-dev \
    libxcb-render-util0-dev \
    # Font tools
    fontconfig \
    # Image tools
    imagemagick \
    # Clean up
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create ubuntu user and set up home directory
RUN useradd -m -s /bin/bash ubuntu && \
    usermod -aG sudo ubuntu && \
    echo 'ubuntu ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

# Set user and working directory as per Cursor guidelines
USER ubuntu
WORKDIR /home/ubuntu

# Set up shell environment
RUN echo 'export PATH=$HOME/.local/bin:$PATH' >> /home/ubuntu/.bashrc && \
    echo 'export PATH=$HOME/.local/bin:$PATH' >> /home/ubuntu/.zshrc

# Install additional tools for HyprRice development
RUN pip3 install --user \
    pyyaml \
    jinja2 \
    requests \
    colorama

# Install additional Node.js tools
RUN npm install -g \
    typescript \
    eslint \
    prettier

# Create common directories
RUN mkdir -p /home/ubuntu/.local/bin \
    && mkdir -p /home/ubuntu/.config \
    && mkdir -p /home/ubuntu/.cache

# Set up git configuration template
RUN git config --global init.defaultBranch main && \
    git config --global pull.rebase false

# Keep container running
CMD ["/bin/bash"]
