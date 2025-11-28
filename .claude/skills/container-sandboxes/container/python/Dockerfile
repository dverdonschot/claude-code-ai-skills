# Python Development Sandbox Container
# Extends base with Python 3.12 and common data science tools
FROM container-sandbox:base

USER root

# Install Python 3.12 from deadsnakes PPA
RUN apt-get update && apt-get install -y \
    software-properties-common \
    && add-apt-repository -y ppa:deadsnakes/ppa \
    && apt-get update && apt-get install -y \
    python3.12 \
    python3.12-dev \
    python3.12-venv \
    python3-pip \
    python3-setuptools \
    && rm -rf /var/lib/apt/lists/*

# Set Python 3.12 as default
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.12 1 && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1

# Install pip for Python 3.12
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.12

# Install uv as root (will be accessible to all users)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Add uv to PATH
ENV PATH="/root/.local/bin:${PATH}"

# Install common Python packages using uv (as root for system-wide access)
RUN uv pip install --system \
    # Web frameworks
    flask fastapi uvicorn \
    # Data science
    numpy pandas matplotlib seaborn \
    # Utilities
    requests python-dotenv click rich \
    # Testing
    pytest pytest-cov \
    # Code quality
    black flake8 mypy

# Switch to non-root user
USER user

# Create Python project structure
RUN mkdir -p /home/user/.cache/pip

# Add uv to user PATH as well
ENV PATH="/root/.local/bin:${PATH}"

# Set Python environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /home/user

CMD ["sleep", "infinity"]
