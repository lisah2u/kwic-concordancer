"""
Concordance API - A classroom-friendly, linguist-powered concordancer
Backend implementation with FastAPI
"""

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, FileResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
import spacy
from pathlib import Path
import re
from functools import lru_cache
import time
from datetime import datetime
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

app = FastAPI(title="Concordance API", description="A classroom-friendly concordancer")

# Rate limiting setup (in-memory storage for simplicity)
limiter = Limiter(key_func=get_remote_address, storage_uri="memory://")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add compression middleware for better bandwidth usage
app.add_middleware(GZipMiddleware, minimum_size=1000)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now
    allow_credentials=False,  # Set to False when using wildcard
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

# spaCy model (placeholder for now)
nlp = None

# Corpus storage with caching and metadata
corpora: Dict[str, List[str]] = {}
corpus_metadata: Dict[str, Dict] = {}

# Pre-compiled regex for better tokenization performance
TOKENIZE_REGEX = re.compile(r'\w+|[^\w\s]')

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
    page: int
    page_size: int
    total_pages: int


class FileContent(BaseModel):
    """File content response"""
    filename: str
    content: str
    line_count: int
    word_count: int
    char_count: int


def load_corpus(corpus_name: str) -> List[str]:
    """Load corpus from samples directory with intelligent caching"""
    # Basic security: prevent path traversal
    if ".." in corpus_name or "/" in corpus_name or "\\" in corpus_name:
        raise HTTPException(status_code=400, detail="Invalid corpus name")
    
    corpus_path = Path("samples") / f"{corpus_name}.txt"
    
    if not corpus_path.exists():
        raise HTTPException(status_code=404, detail=f"Corpus '{corpus_name}' not found")
    
    # Check if corpus is cached and file hasn't changed
    file_stat = corpus_path.stat()
    file_mtime = file_stat.st_mtime
    file_size = file_stat.st_size
    
    if corpus_name in corpora and corpus_name in corpus_metadata:
        cached_metadata = corpus_metadata[corpus_name]
        if (cached_metadata.get('mtime') == file_mtime and 
            cached_metadata.get('size') == file_size):
            # File unchanged, return cached version
            cached_metadata['access_count'] = cached_metadata.get('access_count', 0) + 1
            cached_metadata['last_accessed'] = datetime.now().isoformat()
            return corpora[corpus_name]
    
    # Load file (not cached or file changed)
    try:
        start_time = time.time()
        with open(corpus_path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
        
        load_time = time.time() - start_time
        
        # Cache the corpus and metadata
        corpora[corpus_name] = lines
        corpus_metadata[corpus_name] = {
            'mtime': file_mtime,
            'size': file_size,
            'line_count': len(lines),
            'load_time': load_time,
            'loaded_at': datetime.now().isoformat(),
            'access_count': 1,
            'last_accessed': datetime.now().isoformat()
        }
        
        return lines
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading corpus: {str(e)}")


def tokenize_line(line: str) -> List[str]:
    """Optimized tokenization using pre-compiled regex"""
    # Use pre-compiled regex for better performance
    tokens = TOKENIZE_REGEX.findall(line)
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

@app.get("/app.js")
async def serve_js():
    """Serve JavaScript file at root level"""
    return FileResponse('static/app.js', media_type='application/javascript')

@app.get("/tailwind.css")
async def serve_css():
    """Serve Tailwind CSS file at root level"""
    return FileResponse('static/tailwind.css', media_type='text/css')

@app.get("/favicon.ico")
async def favicon():
    """Serve favicon to prevent 404 errors"""
    from fastapi.responses import Response
    return Response(status_code=204)  # No content, but not a 404

@app.get("/api")
async def api_status():
    """API status endpoint"""
    return {"message": "Concordance API v1.0", "status": "running", "cors": "enabled"}


@app.get("/cache/status")
async def cache_status():
    """Cache status and performance metrics"""
    cache_info = {}
    total_memory_mb = 0
    
    for corpus_name, lines in corpora.items():
        metadata = corpus_metadata.get(corpus_name, {})
        # Rough memory estimation (chars * 1 byte + overhead)
        memory_estimate = sum(len(line) for line in lines) / (1024 * 1024)  # MB
        total_memory_mb += memory_estimate
        
        cache_info[corpus_name] = {
            "line_count": len(lines),
            "memory_mb": round(memory_estimate, 2),
            "access_count": metadata.get('access_count', 0),
            "loaded_at": metadata.get('loaded_at'),
            "last_accessed": metadata.get('last_accessed'),
            "load_time_ms": round(metadata.get('load_time', 0) * 1000, 2)
        }
    
    return {
        "cached_corpora": len(corpora),
        "total_memory_mb": round(total_memory_mb, 2),
        "cache_details": cache_info
    }


@app.post("/cache/clear")
async def clear_cache(corpus: Optional[str] = None):
    """Clear cache for specific corpus or all corpora"""
    if corpus:
        if corpus in corpora:
            del corpora[corpus]
            if corpus in corpus_metadata:
                del corpus_metadata[corpus]
            return {"message": f"Cache cleared for corpus '{corpus}'"}
        else:
            raise HTTPException(status_code=404, detail=f"Corpus '{corpus}' not found in cache")
    else:
        corpora.clear()
        corpus_metadata.clear()
        return {"message": "All cache cleared"}


@app.get("/corpora")
@limiter.limit("30/minute")
async def list_corpora(request: Request):
    """List available corpora"""
    samples_dir = Path("samples")
    if not samples_dir.exists():
        return {"corpora": []}
    
    txt_files = [f.stem for f in samples_dir.glob("*.txt")]
    return {"corpora": txt_files}


@app.get("/search", response_model=SearchResponse)
@limiter.limit("60/minute")
async def search(
    request: Request,
    corpus: str = Query(..., description="Corpus name to search"),
    query: str = Query(..., description="Search query"),
    context_size: int = Query(5, description="Context size (words before/after match)"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(100, ge=1, le=1000, description="Results per page (max 1000)")
):
    """
    Search endpoint - returns paginated KWIC hits as JSON
    Output format: { left: [...], match: [...], right: [...] }
    """
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    # Load corpus (uses intelligent caching)
    lines = load_corpus(corpus)
    
    results = []
    
    # Search through each line
    for line_num, line in enumerate(lines):
        tokens = tokenize_line(line)
        kwic_result = search_kwic(tokens, query, context_size)
        
        if kwic_result:
            kwic_result.line_number = line_num + 1  # 1-indexed for display
            results.append(kwic_result)
    
    # Calculate pagination
    total_hits = len(results)
    total_pages = (total_hits + page_size - 1) // page_size if total_hits > 0 else 0
    
    # Validate page number
    if page > total_pages and total_pages > 0:
        raise HTTPException(status_code=400, detail=f"Page {page} does not exist. Total pages: {total_pages}")
    
    # Apply pagination
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_results = results[start_idx:end_idx]
    
    return SearchResponse(
        query=query,
        corpus=corpus,
        results=paginated_results,
        total_hits=total_hits,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@app.get("/view/{corpus}", response_model=FileContent)
@limiter.limit("20/minute")
async def view_file(request: Request, corpus: str):
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
@limiter.limit("60/minute")
async def search_in_file(
    request: Request,
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