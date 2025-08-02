#!/bin/bash
echo "Starting RAG Backend..."
echo "Python version:"
python --version
echo "Current directory:"
pwd
echo "Files in directory:"
ls -la
echo "Environment:"
echo "APP_ENV=$APP_ENV"
echo "GROQ_API_KEY is set: $([ -n "$GROQ_API_KEY" ] && echo "Yes" || echo "No")"
echo "Starting FastAPI..."
exec python -u -m uvicorn main:app --host 0.0.0.0 --port 8080 --log-level info