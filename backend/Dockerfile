# Use Python slim image for smaller size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies first (for caching)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    libmagic1 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements files
COPY requirements-minimal.txt requirements.txt ./

# Install core dependencies first
RUN pip install --no-cache-dir -r requirements-minimal.txt

# Then install heavy ML dependencies with timeout
RUN pip install --no-cache-dir --timeout=300 \
    chromadb==0.4.22 \
    sentence-transformers==2.2.2 \
    pypdf==4.0.1 \
    python-docx==1.1.0 \
    tiktoken==0.5.2 \
    nltk==3.8.1

# Install LLM clients last (optional)
RUN pip install --no-cache-dir \
    openai==1.12.0 \
    langchain==0.1.6 \
    langchain-community==0.0.19 \
    together==0.2.10 || echo "Optional LLM clients failed, continuing..."

# Download NLTK data
RUN python -m nltk.downloader punkt averaged_perceptron_tagger -d /usr/share/nltk_data

# Copy application code
COPY . .

# Create directory for ChromaDB
RUN mkdir -p /app/chroma_data

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV CHROMA_DATA_PATH=/app/chroma_data

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]