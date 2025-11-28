#!/bin/bash
# Full-stack container setup script

set -e

echo "========================================="
echo "Full-Stack Sandbox Environment"
echo "========================================="

# Python version
echo "Python version:"
python --version

# Node version
echo -e "\nNode.js version:"
node --version
npm --version

# Installed tools
echo -e "\nInstalled tools:"
echo "- uv (Python package manager): $(uv --version)"
echo "- yarn (Node package manager): $(yarn --version)"
echo "- pnpm (Node package manager): $(pnpm --version)"
echo "- typescript: $(tsc --version)"
echo "- vite: $(vite --version)"

# Database clients
echo -e "\nDatabase clients:"
echo "- sqlite3: $(sqlite3 --version)"
echo "- psql (PostgreSQL)"
echo "- redis-cli"

echo -e "\n========================================="
echo "Environment ready!"
echo "Working directory: /home/user"
echo "========================================="
