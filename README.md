# KWIC Concordancer

A modern corpus linguistics tool built with FastAPI and vanilla JavaScript, designed for classroom use and linguistic analysis.

## 🌐 Live Demo

- **Frontend**: https://kwic-concordancer.netlify.app/
- **Backend API**: https://kwic-concordancer-production.up.railway.app/

## Features

- **Simple Workflow**: Select corpus → View file → Search within file
- **KWIC Format**: Traditional three-column Keyword-in-Context display with proper text alignment
- **Multiple Corpora**: Support for various text collections (currently includes Brown Corpus samples)
- **Educational Focus**: Clean, intuitive interface designed for linguistics students and researchers
- **Fast Search**: Efficient pattern matching with customizable context size and case sensitivity
- **Production Ready**: Deployed with security features and rate limiting

## Repository Structure

```
kwic-concordancer/
├── frontend/              # Netlify deployment
│   ├── index.html         # Main application interface
│   ├── app.js             # Frontend JavaScript logic
│   ├── tailwind.css       # Built CSS styles
│   ├── package.json       # Node.js dependencies for Tailwind
│   ├── netlify.toml       # Netlify configuration
│   └── src/input.css      # CSS source file
│
├── backend/               # Railway deployment
│   ├── main.py            # FastAPI application
│   ├── samples/           # Corpus text files
│   ├── requirements.txt   # Python dependencies
│   ├── pyproject.toml     # Python project configuration
│   ├── Procfile           # Railway start command
│   └── runtime.txt        # Python version specification
│
└── README.md              # Project documentation
```

## Local Development

### Backend (Python)

1. Navigate to backend directory:
```bash
cd backend
```

2. Create and activate virtual environment:
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
uv pip install -r requirements.txt
```

4. Start the server:
```bash
python main.py
# OR
uv run uvicorn main:app --reload
```

5. Backend runs at `http://localhost:8000`

### Frontend (Static Files)

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install Node.js dependencies:
```bash
npm install
```

3. Build CSS (for development):
```bash
npm run build-css
```

4. For development with CSS watching:
```bash
npm run watch-css
```

5. Serve frontend files using any static server or open `index.html` directly

## API Endpoints

**Base URL**: `https://kwic-concordancer-production.up.railway.app`

- `GET /` - API status and information
- `GET /api` - Detailed API status with samples info
- `GET /corpora` - List available text corpora
- `GET /search` - KWIC search with pagination
  - Query params: `corpus`, `query`, `context_size`, `page`, `page_size`
- `GET /view/{corpus}` - View full content of a corpus file
- `GET /search-in-file/{corpus}` - Search within specific corpus
  - Query params: `query`, `case_sensitive`
- `GET /cache/status` - Cache performance metrics
- `POST /cache/clear` - Clear corpus cache

## Deployment

### Architecture

- **Frontend**: Netlify (Static site deployment)
  - Base directory: `frontend/`
  - Build command: `npm run build-css`
  - Deploy directory: `frontend/` (current directory)

- **Backend**: Railway (Python app deployment)  
  - Base directory: `backend/`
  - Start command: `python main.py`
  - Auto-deploys from `main` branch

### Deployment Configuration

**Netlify** (`frontend/netlify.toml`):
- Builds Tailwind CSS
- Proxies API calls to Railway backend
- Includes security headers and caching

**Railway** (`backend/Procfile`, `backend/runtime.txt`):
- Python 3.13 runtime
- Automatic dependency installation
- Environment-based port configuration

## Technologies

- **Backend**: FastAPI, Python 3.13, uvicorn
- **Frontend**: Vanilla JavaScript, Tailwind CSS v3
- **Deployment**: Netlify + Railway
- **Development**: uv package manager, npm

## License

MIT License