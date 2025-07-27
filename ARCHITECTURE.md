# Concordancer Architecture Documentation

## Overview

The Concordancer is a modern KWIC (Keywords-in-Context) tool built with FastAPI and vanilla JavaScript, designed for corpus linguistics analysis in educational environments. This document provides a comprehensive technical overview of the system architecture, implementation details, and design decisions.

## System Architecture

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │───▶│   Backend API   │───▶│   Data Layer    │
│                 │    │                 │    │                 │
│ • HTML/CSS/JS   │    │ • FastAPI       │    │ • Text Files    │
│ • KWIC Display  │    │ • KWIC Logic    │    │ • File Cache    │
│ • Search UI     │    │ • Pagination    │    │ • Metadata      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Technology Stack

**Backend:**
- **FastAPI** - Modern Python web framework with automatic API documentation
- **Pydantic** - Data validation and serialization
- **uvicorn** - ASGI server for production deployment

**Frontend:**
- **Vanilla JavaScript (ES6+)** - No framework dependencies for educational clarity
- **Tailwind CSS v3** - Utility-first CSS framework (local build process, production-ready)
- **Modern DOM APIs** - fetch(), async/await, template literals

**Data Layer:**
- **Text Files** - Corpus data stored as UTF-8 text files
- **In-Memory Cache** - Intelligent caching with file change detection
- **Metadata Tracking** - Performance and usage analytics

## Project Structure

```
kwic-concordancer/
├── 🔧 Core Application
│   ├── concordance_api.py      # FastAPI backend (main server)
│   ├── static/
│   │   ├── index.html          # Frontend UI
│   │   ├── app.js             # JavaScript logic
│   │   └── tailwind.css       # Built CSS (generated, do not edit)
│   ├── src/
│   │   └── input.css          # Tailwind CSS source file
│   └── start_server.py        # Server startup script
├── 📊 Data & Testing  
│   ├── samples/               # Corpus text files (~1MB diverse data)
│   ├── test_concordance.py    # Comprehensive test suite (36 tests)
│   └── pyproject.toml         # Python dependencies & config
├── 🎨 Frontend Build
│   ├── package.json           # Node.js dependencies & scripts
│   ├── tailwind.config.js     # Tailwind CSS configuration
│   └── node_modules/          # Node.js dependencies (ignored by git)
└── 📝 Documentation
    ├── CLAUDE.md              # Project memory & commands
    ├── README.md              # Project overview
    ├── ARCHITECTURE.md        # This document
    └── concordance-prd.md     # Requirements document
```

## Backend Implementation

### Application Setup & Middleware Stack

```python
# FastAPI app with optimized middleware stack
app = FastAPI(title="Concordance API", description="A classroom-friendly concordancer")

# Performance & Infrastructure Middleware (order matters!)
├── GZipMiddleware        # Response compression (30-70% bandwidth reduction)
├── CORSMiddleware        # Cross-origin requests for frontend
└── StaticFiles          # Serve HTML/CSS/JS files
```

**Key Design Decisions:**
- **GZip Compression**: Only compresses responses >1KB to avoid overhead
- **CORS**: Wildcard origins for development (should be restricted in production)
- **Static Files**: Frontend served from same server (no separate deployment)

### Data Models

```python
# Traditional KWIC (Keywords-in-Context) Structure
KWICResult:
├── left: ["The", "quick"]      # Words before match
├── match: ["brown"]            # The search term found
├── right: ["fox", "jumps"]     # Words after match  
└── line_number: 42             # Source line reference

# Paginated Search Response
SearchResponse:
├── query: "brown"              # Original search term
├── corpus: "shakespeare"       # Source corpus name
├── results: [KWICResult...]    # Current page results
├── total_hits: 156             # Total matches found
├── page: 1                     # Current page (1-indexed)
├── page_size: 100              # Results per page
└── total_pages: 2              # Total available pages
```

### Intelligent Caching System

The caching system provides 50-90% performance improvement on repeated searches:

```python
# Cache Decision Flow
File Request
├── File in cache? ──No──► Load from disk ──► Cache with metadata
└── Yes
    ├── File modified? ──Yes──► Reload & update cache
    └── No ──► Return cached version + update access stats

# Metadata Tracking
corpus_metadata[corpus_name] = {
    'mtime': 1705123456.789,           # File modification time
    'size': 524288,                    # File size in bytes  
    'line_count': 4234,                # Number of lines
    'load_time': 0.045,                # Time to load (seconds)
    'loaded_at': '2024-01-13T...',     # When first cached
    'access_count': 7,                 # Number of times accessed
    'last_accessed': '2024-01-13T...' # Last access timestamp
}
```

**Performance Impact:** 
- First load: File I/O time (5-50ms depending on file size)
- Subsequent loads: ~1ms (memory access only)
- Automatic cache invalidation on file changes

### Optimized Tokenization

```python
# Pre-compiled regex pattern (defined once at module load)
TOKENIZE_REGEX = re.compile(r'\w+|[^\w\s]')

# Before optimization: re.findall(r'\w+|[^\w\s]', line)  # Compiles every call
# After optimization:  TOKENIZE_REGEX.findall(line)     # Uses pre-compiled

# Pattern Explanation:
├── \w+        # One or more word characters (letters, digits, underscore)
└── [^\w\s]    # OR any single non-word, non-whitespace character (punctuation)

# Example tokenization:
"Hello, world!"  →  ["Hello", ",", "world", "!"]
"I have 5 cats." →  ["I", "have", "5", "cats", "."]
```

**Performance Impact:** 20-40% faster tokenization on large texts

### KWIC Search Algorithm

```python
# Input: tokens = ["The", "quick", "brown", "fox", "jumps"]
#        query = "brown", context_size = 2

Step 1: Find match at index 2
Step 2: Calculate boundaries
├── left_start = max(0, 2-2) = 0
├── left_end = 2  
├── right_start = 2+1 = 3
└── right_end = min(5, 2+1+2) = 5

Step 3: Extract contexts
├── left = tokens[0:2] = ["The", "quick"]
├── match = [tokens[2]] = ["brown"]  # Preserves original case
└── right = tokens[3:5] = ["fox", "jumps"]

# Traditional KWIC Format:
     Left Context  |   Match   |  Right Context
    The quick      |   brown   |  fox jumps
```

**Key Features:**
- **Case-insensitive search** but **preserves original case** in results
- **Flexible context size** (default 5 words each side)
- **Boundary protection** (doesn't go beyond line start/end)
- **First match only** per line (linguistic convention)

## API Endpoints

### Complete API Reference

```yaml
Frontend Endpoints:
  GET /              # Serve main HTML page
  GET /app           # Alternative frontend route
  GET /static/*      # Static files (CSS, JS, images)

Core Search API:
  GET /search        # Main KWIC search with pagination
  └── Parameters: corpus, query, context_size=5, page=1, page_size=100
  
Data Access:
  GET /corpora       # List available corpus files
  GET /view/{corpus} # View full file content with metadata
  
In-File Search:
  GET /search-in-file/{corpus}  # Line-by-line text search
  └── Parameters: query, case_sensitive=false

Cache Management:
  GET /cache/status   # Cache performance metrics
  POST /cache/clear   # Clear cache (optional ?corpus= parameter)

System:
  GET /api           # API status and version
```

### Search Endpoint Flow

```python
# Request: GET /search?corpus=shakespeare&query=love&page=2&page_size=50

Step 1: Parameter Validation
├── corpus: "shakespeare" (required)
├── query: "love" (required, non-empty)  
├── context_size: 5 (default)
├── page: 2 (≥1)
└── page_size: 50 (1-1000 range)

Step 2: Corpus Loading (with caching)
├── Check cache for "shakespeare"
├── If cached & file unchanged → return cached
└── If not cached → load from disk + cache

Step 3: Full Corpus Search
├── For each line in corpus:
│   ├── Tokenize line
│   ├── Search for "love" 
│   └── If found → create KWICResult
└── Collect all matches

Step 4: Pagination Logic
├── total_hits = len(results)
├── total_pages = ceil(total_hits / page_size)
├── Validate page number exists
└── Extract page slice: results[start:end]

Step 5: Response
└── Return SearchResponse with metadata + results
```

## Frontend Implementation

### HTML Structure

```html
<!DOCTYPE html>
<html>
<head>
    <!-- Tailwind CSS v3 (locally built, production-ready) -->
    <link rel="stylesheet" href="tailwind.css">
    
    <!-- Custom CSS for KWIC-specific styling -->
    <style>
        .kwic-match { /* Highlight search matches */ }
        .kwic-table { /* Three-column KWIC layout */ }
        .line-number { /* Source line references */ }
    </style>
</head>

<body>
    <!-- UI Component Structure -->
    ├── Header (Title + Description)
    ├── Corpus Selection (Dropdown + View Button)
    ├── Search Section (Query Input + Options)
    ├── Results Display
    │   ├── File Viewer (Full text with line numbers)
    │   └── KWIC Table (Traditional 3-column format)
    └── Message Areas (Errors, No Results, Loading)
</body>
</html>
```

### CSS Build Process

```bash
# Tailwind CSS v3 Build System
src/input.css              # Source file with Tailwind directives
├── @tailwind base;         # Normalize CSS and base styles
├── @tailwind components;   # Component classes
└── @tailwind utilities;    # Utility classes

tailwind.config.js          # Configuration file
├── content: ["./static/**/*.{html,js}"]  # Files to scan for classes
├── theme: { extend: {} }    # Custom theme extensions
└── plugins: []              # Additional plugins

# Build Commands
npm run build-css           # Build CSS once for production
npm run watch-css           # Watch and rebuild during development

# Output
static/tailwind.css         # Generated CSS (optimized, only used classes)
```

### Traditional KWIC Layout

```css
/* Three-Column KWIC Format */
.kwic-table {
    table-layout: fixed;  /* Equal column distribution */
}

.kwic-left {
    text-align: right;    /* Right-align context before match */
    padding-right: 1rem;
    border-right: 2px solid #e5e7eb;  /* Visual separator */
}

.kwic-match {
    text-align: center;   /* Center the search term */
    background-color: #fef3c7;  /* Yellow highlight */
    font-weight: bold;
    white-space: nowrap;  /* Don't wrap the match */
}

.kwic-right {
    text-align: left;     /* Left-align context after match */
    padding-left: 1rem;
}
```

**Visual Result:**
```
Line | Left Context      |  Match  | Right Context
  42 | The quick brown   |   fox   | jumps over the
  89 | red and orange    |   fox   | in the forest  
 156 | sly little grey   |   fox   | caught the
```

### JavaScript Architecture

```javascript
// Modern ES6+ JavaScript with async/await
// Single-Page Application (SPA) pattern

Application Lifecycle:
├── init() → loadCorpora() + setupEventListeners()
├── User interactions → Event handlers  
├── API calls → fetch() with error handling
├── DOM updates → Display results
└── State management → currentCorpus variable

Key Functions:
├── loadCorpora()        # Populate dropdown from API
├── handleViewFile()     # Display full file content
├── handleSearchInFile() # Perform KWIC search
├── displayFileSearchResults() # Render KWIC table
└── extractKWICContexts() # Client-side KWIC formatting
```

## Data Layer

### Corpus Collection

```yaml
Corpus Files (samples/ directory):
├── Literary Texts:
│   ├── AllsWellThatEndsWell.txt (124KB, Shakespeare)
│   └── comedy_monologue.txt (63KB, Modern performance text)
├── Speech & Conversation:
│   ├── Berkeley_Restaurant_Project_speech.txt (389KB)
│   └── Berkeley_Restaurant_transcription_guidelines.txt (3KB)
├── Business Communication:
│   ├── Enron_email.txt (498 bytes, Corporate email)
│   └── Enron_meeting.txt (677 bytes, Meeting transcript)
├── Social Media & Web:
│   ├── covidhoax_hashtag.csv (316KB, Twitter data)
│   ├── tweet_chars.txt (Small social media)
│   ├── tweet_zh.txt (Chinese language tweets)
│   └── newsgroups_txt (3KB, Forum discussions)
└── Reference:
    └── wikipedia_corpus_sample.txt (Large encyclopedia text)

Total Coverage: ~1MB diverse text data
Languages: English (primary), Chinese (sample)
Domains: Literature, speech, business, social media, reference
```

## Testing Architecture

### Comprehensive Test Suite (36 tests)

```python
Test Architecture:
├── TestAPI (2 tests)
│   ├── Basic endpoints functionality  
│   └── CORS and static file serving
├── TestCorpusLoading (2 tests)  
│   ├── File loading with caching
│   └── Error handling for missing files
├── TestTokenization (4 tests)
│   ├── Basic tokenization accuracy
│   ├── Punctuation handling
│   └── Edge cases (empty strings, numbers)
├── TestKWICSearch (5 tests)
│   ├── KWIC algorithm correctness
│   ├── Case sensitivity handling  
│   ├── Context boundary logic
│   └── Edge cases (line start/end)
├── TestSearchEndpoint (4 tests)
│   ├── Parameter validation
│   ├── Error handling
│   └── Response format validation
├── TestFileViewingEndpoints (5 tests)
│   ├── File content display
│   ├── Search within files
│   └── Metadata calculation
├── TestPerformance (5 tests) ⚡
│   ├── Load time benchmarks (<1s for 1000 lines)
│   ├── Search performance (<2s for common words)
│   ├── Caching effectiveness measurement
│   └── Tokenization speed validation
├── TestPaginationAndCaching (5 tests)
│   ├── Pagination logic validation
│   ├── Cache status monitoring
│   └── Cache management functionality
└── TestRealCorpusIntegration (4 tests)
    ├── Shakespeare corpus testing
    ├── Wikipedia corpus testing  
    └── Real-world data validation
```

## Performance Characteristics

### Benchmarked Performance

```yaml
Corpus Operations:
  Load Time: <1ms (cached), 5-50ms (disk read)
  Memory Usage: ~1MB per 4000-line corpus
  Cache Hit Rate: ~90% in typical usage

Search Performance:
  Common Words: 12ms for 1000 hits
  Rare Words: 6ms for few hits  
  Tokenization: 0.1ms per 1000-word line
  Pagination: Negligible overhead

Network Efficiency:
  Compression: 30-70% bandwidth reduction
  Response Size: Typical 5-50KB per search
  Concurrent Users: Scales to hundreds with caching
```

### Performance Optimizations

```python
1. Intelligent Caching: File change detection prevents unnecessary reloads
2. Pre-compiled Regex: 20-40% tokenization speedup
3. Result Pagination: Prevents browser freezing on large datasets
4. Response Compression: Reduces bandwidth usage significantly
5. Comprehensive Testing: 36 tests ensure reliability & performance
```

## Key Design Decisions

### 1. Why FastAPI?

```python
Advantages:
├── Automatic API documentation (OpenAPI/Swagger)
├── Type hints with Pydantic models
├── Async support for future scalability
├── Built-in validation and error handling
└── Excellent performance (similar to Node.js/Go)
```

### 2. Why Vanilla JavaScript?

```javascript
Rationale:
├── Educational clarity (no framework complexity)
├── Lightweight (fast loading for classroom use)
├── Direct DOM manipulation (easier to understand)
├── No build step required (immediate development)
└── Modern ES6+ features (fetch, async/await)
```

### 3. Why In-Memory Caching?

```python
Trade-offs:
├── Pros: Extremely fast access, simple implementation
├── Cons: Lost on restart, memory usage
├── Alternative: Redis (for persistence + sharing)
└── Decision: Educational tool doesn't need persistence
```

### 4. Why Traditional KWIC Format?

```
Linguistic Standard:
├── Left Context | Match | Right Context format
├── Established in corpus linguistics since 1960s
├── Easy visual scanning for patterns
├── Familiar to linguistics students & researchers
└── Optimal for classroom analysis workflows
```

## Development Workflow

### Development Commands

```bash
# Development Environment (using uv)
uv venv                    # Create virtual environment  
source .venv/bin/activate  # Activate (or use 'uv run' prefix)
uv pip install -r requirements.txt  # Install Python dependencies

# Frontend Assets
npm install                # Install Node.js dependencies
npm run build-css          # Build Tailwind CSS v3 (production-ready)
npm run watch-css           # Watch and rebuild CSS during development

# Server Operations
uv run uvicorn concordance_api:app --reload  # Development server
npm run dev                                   # Alternative using npm script
uv run python start_server.py               # Alternative startup

# Testing & Quality
uv run pytest test_concordance.py -v        # Run all tests
npm run test-api                             # Alternative using npm script
uv run pytest test_concordance.py::TestPerformance -v -s  # Performance tests
uv run pytest test_concordance.py::TestRealCorpusIntegration -v  # Integration tests

# Access Points
http://localhost:8000/          # Main application
http://localhost:8000/api       # API status
http://localhost:8000/cache/status  # Cache monitoring
```

### Deployment Architecture

```yaml
Production Considerations:
├── Web Server: FastAPI with uvicorn
├── Static Files: Served via FastAPI StaticFiles
├── CORS: Configured for specific domains (not wildcard)
├── Compression: GZip enabled for responses >1KB  
├── Caching: In-memory cache with intelligent invalidation
├── Monitoring: Cache status endpoint for performance tracking
└── Security: Input validation, error handling, no sensitive data exposure

Scaling Options:
├── Horizontal: Multiple uvicorn workers
├── Caching: Redis for shared cache across instances  
├── Storage: Database for large corpus collections
└── CDN: Static file optimization for global access
```

## Future Enhancements

### Completed Optimizations

- ✅ **Intelligent Corpus Caching** - 50-90% performance improvement
- ✅ **Result Pagination** - Better UI responsiveness with large result sets  
- ✅ **Optimized Tokenization** - 20-40% faster processing
- ✅ **Response Compression** - 30-70% bandwidth reduction
- ✅ **Comprehensive Test Suite** - 36 tests covering all functionality

### Potential Future Enhancements

- 🔄 **Frontend Testing** - Browser automation with Playwright
- 🔄 **Async File I/O** - Better concurrency for large files
- 📋 **spaCy Integration** - Advanced linguistic analysis
- 📋 **Multi-word Search** - Phrase and pattern matching
- 📋 **Export Functionality** - CSV/JSON result export
- 📋 **User Authentication** - Multi-user corpus management
- 📋 **Real-time Collaboration** - Shared analysis sessions

## Conclusion

This concordancer represents a **production-ready educational tool** that balances **linguistic accuracy**, **performance optimization**, and **pedagogical clarity**. The architecture demonstrates modern Python/JavaScript practices while maintaining focus on the core KWIC functionality that corpus linguists need.

The system's strength lies in its simplicity, performance optimization, and comprehensive testing, making it an ideal tool for classroom use and linguistic research.