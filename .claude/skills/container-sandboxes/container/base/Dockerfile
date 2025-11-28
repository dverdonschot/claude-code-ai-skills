# Base Ubuntu Sandbox Container
# Minimal environment with essential utilities
FROM ubuntu:22.04

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Set timezone
ENV TZ=UTC

# Install essential system packages
RUN apt-get update && apt-get install -y \
    # Core utilities
    curl wget git vim nano unzip zip \
    # Build tools
    build-essential \
    # Network tools
    net-tools iputils-ping netcat \
    # SSL certificates
    ca-certificates \
    # Process management
    procps \
    # File utilities
    file tree \
    # Text processing
    jq \
    # Other essentials
    sudo locales \
    && rm -rf /var/lib/apt/lists/*

# Set up locale
RUN locale-gen en_US.UTF-8
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US:en
ENV LC_ALL=en_US.UTF-8

# Create non-root user 'user' with UID 1000
RUN useradd -m -u 1000 -s /bin/bash user && \
    echo "user ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Set working directory
WORKDIR /home/user

# Create common directories
RUN mkdir -p /home/user/{projects,data,output} && \
    chown -R user:user /home/user

# Switch to non-root user
USER user

# Set default shell
ENV SHELL=/bin/bash

# Keep container alive
CMD ["sleep", "infinity"]
