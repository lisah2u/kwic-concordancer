"""
Concordance API - A classroom-friendly, linguist-powered concordancer
Backend implementation with FastAPI
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, FileResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
import spacy
from pathlib import Path
import re

app = FastAPI(title="Concordance API", description="A classroom-friendly concordancer")

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# spaCy model (placeholder for now)
nlp = None

# Corpus storage
corpora: Dict[str, List[str]] = {}

# Mount static files
static_path = Path("static")
if static_path.exists():
    app.mount("/static", StaticFiles(directory="static", html=True), name="static")


class KWICResult(BaseModel):
    """KWIC (Keyword in Context) result structure"""
    left: List[str]
    match: List[str]
    right: List[str]
    line_number: int


class SearchResponse(BaseModel):
    """Search response containing KWIC results"""
    query: str
    corpus: str
    results: List[KWICResult]
    total_hits: int


class FileContent(BaseModel):
    """File content response"""
    filename: str
    content: str
    line_count: int
    word_count: int
    char_count: int


def load_corpus(corpus_name: str) -> List[str]:
    """Load corpus from samples directory"""
    corpus_path = Path("samples") / f"{corpus_name}.txt"
    
    if not corpus_path.exists():
        raise HTTPException(status_code=404, detail=f"Corpus '{corpus_name}' not found")
    
    try:
        with open(corpus_path, 'r', encoding='utf-8') as f:
            # Tokenize per line as specified in PRD
            lines = [line.strip() for line in f.readlines() if line.strip()]
            return lines
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading corpus: {str(e)}")


def tokenize_line(line: str) -> List[str]:
    """Basic tokenization - split on whitespace and punctuation"""
    # Simple tokenization for v1 - can be enhanced with spaCy later
    tokens = re.findall(r'\w+|[^\w\s]', line)
    return tokens


def search_kwic(tokens: List[str], query: str, context_size: int = 5) -> Optional[KWICResult]:
    """Search for exact match and return KWIC structure"""
    query_lower = query.lower()
    
    for i, token in enumerate(tokens):
        if token.lower() == query_lower:
            # Calculate context boundaries
            left_start = max(0, i - context_size)
            right_end = min(len(tokens), i + 1 + context_size)
            
            return KWICResult(
                left=tokens[left_start:i],
                match=[token],  # Exact match as found
                right=tokens[i + 1:right_end],
                line_number=0  # Will be set by caller
            )
    
    return None


@app.get("/")
async def root():
    """Root endpoint - serve frontend"""
    return FileResponse('static/index.html')

@app.get("/app")
async def frontend():
    """Frontend endpoint"""
    return FileResponse('static/index.html')

@app.get("/api")
async def api_status():
    """API status endpoint"""
    return {"message": "Concordance API v1.0", "status": "running"}


@app.get("/corpora")
async def list_corpora():
    """List available corpora"""
    samples_dir = Path("samples")
    if not samples_dir.exists():
        return {"corpora": []}
    
    txt_files = [f.stem for f in samples_dir.glob("*.txt")]
    return {"corpora": txt_files}


@app.get("/search", response_model=SearchResponse)
async def search(
    corpus: str = Query(..., description="Corpus name to search"),
    query: str = Query(..., description="Search query"),
    context_size: int = Query(5, description="Context size (words before/after match)")
):
    """
    Search endpoint - returns KWIC hits as JSON
    Output format: { left: [...], match: [...], right: [...] }
    """
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    # Load corpus if not already loaded
    if corpus not in corpora:
        corpora[corpus] = load_corpus(corpus)
    
    results = []
    
    # Search through each line
    for line_num, line in enumerate(corpora[corpus]):
        tokens = tokenize_line(line)
        kwic_result = search_kwic(tokens, query, context_size)
        
        if kwic_result:
            kwic_result.line_number = line_num + 1  # 1-indexed for display
            results.append(kwic_result)
    
    return SearchResponse(
        query=query,
        corpus=corpus,
        results=results,
        total_hits=len(results)
    )


@app.get("/view/{corpus}", response_model=FileContent)
async def view_file(corpus: str):
    """
    File viewing endpoint - returns full file content with metadata
    """
    corpus_path = Path("samples") / f"{corpus}.txt"
    
    if not corpus_path.exists():
        raise HTTPException(status_code=404, detail=f"Corpus '{corpus}' not found")
    
    try:
        with open(corpus_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Calculate metadata
        lines = content.split('\n')
        line_count = len(lines)
        word_count = len(content.split())
        char_count = len(content)
        
        return FileContent(
            filename=f"{corpus}.txt",
            content=content,
            line_count=line_count,
            word_count=word_count,
            char_count=char_count
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")


@app.get("/search-in-file/{corpus}")
async def search_in_file(
    corpus: str,
    query: str = Query(..., description="Search query"),
    case_sensitive: bool = Query(False, description="Case sensitive search")
):
    """
    Search within a specific file - returns line numbers and content
    """
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    corpus_path = Path("samples") / f"{corpus}.txt"
    
    if not corpus_path.exists():
        raise HTTPException(status_code=404, detail=f"Corpus '{corpus}' not found")
    
    try:
        with open(corpus_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        results = []
        search_query = query if case_sensitive else query.lower()
        
        for line_num, line in enumerate(lines, 1):
            search_line = line if case_sensitive else line.lower()
            if search_query in search_line:
                results.append({
                    "line_number": line_num,
                    "content": line.strip(),
                    "matches": line.count(query) if case_sensitive else line.lower().count(search_query)
                })
        
        return {
            "query": query,
            "corpus": corpus,
            "case_sensitive": case_sensitive,
            "results": results,
            "total_lines_matched": len(results),
            "total_matches": sum(r["matches"] for r in results)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching file: {str(e)}")


# Placeholder for spaCy integration (v1.5+)
def initialize_spacy():
    """Initialize spaCy model - placeholder for future enhancement"""
    global nlp
    try:
        # nlp = spacy.load("en_core_web_sm")
        pass
    except IOError:
        print("spaCy model not found. Install with: python -m spacy download en_core_web_sm")


if __name__ == "__main__":
    import uvicorn
    initialize_spacy()
    uvicorn.run(app, host="0.0.0.0", port=8000)