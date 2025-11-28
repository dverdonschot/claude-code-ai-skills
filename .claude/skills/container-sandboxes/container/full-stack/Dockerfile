# Full-Stack Development Sandbox Container
# Combines Python 3.12 + Node.js 22 + Database tools
FROM container-sandbox:base

USER root

# Install Python 3.12
RUN apt-get update && apt-get install -y \
    software-properties-common \
    && add-apt-repository -y ppa:deadsnakes/ppa \
    && apt-get update && apt-get install -y \
    python3.12 \
    python3.12-dev \
    python3.12-venv \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 22
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Install database clients
RUN apt-get update && apt-get install -y \
    sqlite3 \
    postgresql-client \
    redis-tools \
    && rm -rf /var/lib/apt/lists/*

# Set Python 3.12 as default
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.12 1 && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1

# Install pip for Python 3.12
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.12

# Install Yarn and pnpm
RUN npm install -g yarn pnpm

# Install uv as root (will be accessible to all users)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Add uv to PATH
ENV PATH="/root/.local/bin:${PATH}"

# Install common Python packages using uv (as root for system-wide access)
RUN uv pip install --system \
    flask fastapi uvicorn \
    sqlalchemy alembic \
    requests python-dotenv \
    pytest black

# Switch to non-root user
USER user

# Create project directories
RUN mkdir -p /home/user/{backend,frontend,database,scripts}

# Add uv to user PATH as well
ENV PATH="/root/.local/bin:${PATH}"

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV NODE_ENV=development

WORKDIR /home/user

CMD ["sleep", "infinity"]
