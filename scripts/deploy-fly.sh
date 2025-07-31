#!/bin/bash
# Fly.io deployment script for RAG Application

set -e

echo "🚀 Deploying RAG Application Backend to Fly.io"

# Check if flyctl is installed
if ! command -v flyctl &> /dev/null; then
    echo "❌ flyctl CLI not found. Please install it first:"
    echo "curl -L https://fly.io/install.sh | sh"
    exit 1
fi

# Check if user is authenticated
if ! flyctl auth whoami &> /dev/null; then
    echo "❌ Not authenticated with Fly.io. Please run:"
    echo "flyctl auth login"
    exit 1
fi

# Navigate to project root
cd "$(dirname "$0")/.."

echo "📋 Checking fly.toml configuration..."
if [ ! -f "fly.toml" ]; then
    echo "❌ fly.toml not found"
    exit 1
fi

echo "🐳 Building and deploying application..."

# Deploy to Fly.io
flyctl deploy --verbose

echo "✅ Deployment completed!"
echo "🌐 Your app should be available at:"
flyctl status --app rag-app-backend

echo ""
echo "📊 To view logs:"
echo "flyctl logs --app rag-app-backend"
echo ""
echo "🔧 To set environment variables:"
echo "flyctl secrets set SUPABASE_URL=your_url SUPABASE_SERVICE_KEY=your_key --app rag-app-backend"