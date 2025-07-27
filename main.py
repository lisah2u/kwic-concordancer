"""
Minimal test FastAPI app for Railway deployment
"""
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
    return {"message": "KWIC Concordancer API", "status": "running"}

@app.get("/api")
async def api_status():
    return {"message": "API working", "status": "ok"}

@app.get("/corpora")
async def list_corpora():
    return {"corpora": ["test-corpus"], "message": "Minimal test version"}