# Node.js Development Sandbox Container
# Extends base with Node.js 22 LTS and common dev tools
FROM container-sandbox:base

USER root

# Install Node.js 22 LTS from NodeSource
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Install Yarn and pnpm
RUN npm install -g yarn pnpm

# Install common global packages (as root for system-wide access)
RUN npm install -g \
    # Build tools
    typescript@latest \
    ts-node@latest \
    # Bundlers
    vite@latest \
    webpack@latest \
    # Testing
    vitest@latest \
    jest@latest \
    # Code quality
    eslint@latest \
    prettier@latest \
    # Utilities
    nodemon@latest \
    tsx@latest \
    # Framework CLIs
    create-vite@latest \
    create-next-app@latest

# Switch to non-root user
USER user

# Create npm directories
RUN mkdir -p /home/user/{.npm,.cache/yarn,.cache/pnpm}

# Set Node environment variables
ENV NODE_ENV=development

WORKDIR /home/user

CMD ["sleep", "infinity"]
