"""
Minimal FastAPI app to test if basic deployment works
"""
from fastapi import FastAPI
import os

app = FastAPI(title="RAG Test")

@app.get("/")
def root():
    return {"status": "alive", "message": "Basic app working"}

@app.get("/test")
def test():
    return {
        "env": os.environ.get("APP_ENV", "unknown"),
        "python": "working",
        "fastapi": "working"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)