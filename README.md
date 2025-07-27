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

## Quick Start

### Prerequisites

- Python 3.8+
- `uv` package manager (recommended) or `pip`

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd kwic-concordancer
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

### Running the Application

1. Start the server:
```bash
uv run uvicorn concordance_api:app --reload
```

2. Open your browser to `http://localhost:8000`

3. Select a corpus, view the file content, then search for patterns using the KWIC interface

## API Endpoints

- `GET /` - Main application interface
- `GET /corpora` - List available corpora
- `GET /view/{corpus}` - View full content of a corpus file
- `GET /search-in-file/{corpus}` - Search within a specific corpus with KWIC results

## Development

### Running Tests

```bash
uv run pytest test_concordance.py -v
```

### Project Structure

```
├── concordance_api.py      # FastAPI backend
├── static/
│   ├── index.html         # Main interface
│   └── app.js            # Frontend logic
├── samples/              # Corpus files
├── test_concordance.py   # Test suite
└── pyproject.toml       # Dependencies
```

## Technologies

- **Backend**: FastAPI, Python 3.8+
- **Frontend**: Vanilla JavaScript, Tailwind CSS
- **Testing**: pytest, httpx
- **Development**: uv package manager

## License

MIT License