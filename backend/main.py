"""
Minimal test FastAPI app for Railway deployment
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="KWIC Concordancer API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    import sys
    from pathlib import Path
    
    port = os.environ.get("PORT", "unknown")
    cwd = str(Path.cwd())
    files = list(Path(".").iterdir())
    
    return {
        "message": "KWIC Concordancer API", 
        "status": "running",
        "port": port,
        "environment": "railway",
        "python_version": sys.version,
        "working_directory": cwd,
        "files_in_directory": [str(f) for f in files[:10]]  # First 10 files
    }

@app.get("/api")
async def api_status():
    return {"message": "API working", "status": "ok"}

@app.get("/corpora")
async def list_corpora():
    return {"corpora": ["test-corpus"], "message": "Minimal test version"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)