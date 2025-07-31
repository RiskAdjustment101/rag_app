#!/bin/bash

# Railway deployment script - alternative approach
# Run this if Railway dashboard deployment fails

echo "🚂 Deploying to Railway via CLI..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "Installing Railway CLI..."
    curl -fsSL https://railway.app/install.sh | sh
fi

# Login and deploy
echo "Please run the following commands manually:"
echo ""
echo "1. railway login"
echo "2. railway link (select your existing project)"
echo "3. railway up"
echo ""
echo "Or create a new project:"
echo "railway init"
echo "railway up"