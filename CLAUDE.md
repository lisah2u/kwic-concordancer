# Claude Memory

This file helps Claude understand your project and preferences.

## Project Overview

**Concordancer v1.2** - A classroom-friendly, linguist-powered concordancer with streamlined workflow for corpus analysis and file viewing.

### Features
- **📄 File Viewing**: Complete file display with line numbers and metadata  
- **🔍 KWIC Search**: Traditional concordance format with proper text justification
- **🎯 Streamlined UX**: Simple workflow (Select → View → Search → Clear)
- **📊 Statistics**: Real-time file metrics (lines, words, characters)
- **📱 Responsive**: Works on desktop and mobile devices
- **🧠 Smart UI**: Progressive disclosure based on user actions

## Development Environment

Use `uv` for dependency management and virtual environment:
- Virtual environment: `.venv` (created with `uv venv`)
- Activate: `source .venv/bin/activate` or use `uv run` prefix
- Dependencies: Managed in `pyproject.toml` (no separate requirements.txt)

## Development Commands

- Install dependencies: `uv sync`
- Run concordance server: `uv run python start_server.py`
- Run tests: `uv run pytest test_concordance.py -v`
- Test API directly: `uv run python concordance_api.py`

## Access URLs
- 🎯 **Main App**: http://localhost:8000/
- 📚 **API Docs**: http://localhost:8000/docs  
- 🔧 **API Status**: http://localhost:8000/api 

## Project Structure

### Core Application
- `concordance_api.py` - FastAPI backend with search and file viewing endpoints
- `static/index.html` - Frontend with streamlined workflow interface
- `static/app.js` - JavaScript functionality for UI and API calls
- `start_server.py` - Server startup script with helpful information

### Configuration & Dependencies
- `pyproject.toml` - Project configuration and dependencies (using uv)
- `uv.lock` - Locked dependency versions

### Data & Testing
- `samples/` - Corpus files (.txt format) for linguistic analysis
- `test_concordance.py` - Comprehensive test suite (22 tests covering all endpoints)

### Documentation
- `CLAUDE.md` - Project documentation and development guide
- `concordance-prd.md` - Product requirements and feature specifications
- `README.md` - Basic project information

### API Endpoints
- `GET /` - Frontend interface (serves static HTML)
- `GET /corpora` - List available corpus files
- `GET /view/{corpus}` - File content with metadata
- `GET /search-in-file/{corpus}` - KWIC search within specific file
- `GET /docs` - Interactive API documentation

## Key Features Implemented

- **v1.2**: Complete file viewing and KWIC search capabilities
- **Clean UX**: Streamlined workflow (Select → View → Search → Clear)
- **KWIC Format**: Traditional three-column concordance display
- **Responsive Design**: Works on desktop and mobile devices
- **Test Coverage**: 22 comprehensive tests covering all functionality
- **Modern Stack**: FastAPI + Vanilla JS + Tailwind CSS

## Development Notes

- Project uses `uv` for fast dependency management
- All dependencies specified in `pyproject.toml`
- Frontend uses vanilla JavaScript (no complex frameworks)
- Comprehensive test suite covers all API endpoints
- Clean codebase with legacy Gradio implementation removed