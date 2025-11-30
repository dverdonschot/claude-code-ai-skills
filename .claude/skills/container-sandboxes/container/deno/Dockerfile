# Deno Development Sandbox Container
# Extends base with Deno runtime
FROM container-sandbox:base

USER root

# Install Deno
RUN curl -fsSL https://deno.land/install.sh | sh

# Add Deno to PATH for all users
ENV DENO_INSTALL="/root/.deno"
ENV PATH="${DENO_INSTALL}/bin:${PATH}"

# Make deno accessible to non-root user by copying to /usr/local/bin
RUN cp /root/.deno/bin/deno /usr/local/bin/deno && \
    chmod +x /usr/local/bin/deno

# Switch to non-root user
USER user

# Create Deno project structure
RUN mkdir -p /home/user/.cache/deno

# Set Deno environment variables
ENV DENO_DIR="/home/user/.cache/deno"

WORKDIR /home/user

CMD ["sleep", "infinity"]
