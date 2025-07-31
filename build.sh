#!/usr/bin/env bash
# Render build script - ensures clean Python environment

set -o errexit  # Exit on error

echo "🔧 Installing Python dependencies..."
pip install --no-cache-dir --upgrade pip
pip install --no-cache-dir -r requirements.txt

echo "✅ Build completed successfully!"