# Claude Memory

This file helps Claude understand your project and preferences.

## Plan and Review

### Before starting work
- Always use plan mode
- After the plan has completed, write it to .claude/tasks/TASK_NAME.md
- The plan should be a detailed implementation plan and reasoning for the task. Break tasks down.
- If the tasks require external knowledge or a certain package, research to get the latest knowledge.
- Don't overplan, think MVP. 
- Once the plan has been written, ask me to review it. Don't move forward until I approve it.

### While implementing
- Update the plan as you work.
- Fter you complete tasks, update and append detailed descriptions of changes made.

## Project Overview

This is a modern concordancer (KWIC - Keywords-in-Context) tool built with FastAPI and vanilla JavaScript. The application provides a streamlined workflow for corpus linguistics analysis with traditional three-column KWIC format display.

## Development Environment

Use `uv` for dependency management and virtual environment:
- Virtual environment: `.venv` (created with `uv venv`)
- Activate: `source .venv/bin/activate` or use `uv run` prefix
- Install dependencies: `uv pip install -r requirements.txt`

## Development Commands

**Python Backend:**
- Install dependencies: `uv pip install -r requirements.txt`
- Start server: `uv run uvicorn concordance_api:app --reload` or `npm run dev`
- Test: `uv run pytest test_concordance.py -v` or `npm run test-api`

**Frontend Assets:**
- Install frontend dependencies: `npm install`
- Build CSS: `npm run build-css` (builds Tailwind CSS from src/input.css)
- Watch CSS (during development): `npm run watch-css` (rebuilds on changes)
- Access application: `http://localhost:8000`

**Note:** Frontend uses Tailwind CSS v3 (local installation, production-ready)

## Deployment Commands

**Production Deployment:**
- Build production assets: `npm run build` (minified CSS)
- Deploy to Netlify: `npm run deploy-netlify` (requires Netlify CLI)
- Deploy to Railway: `git push origin main` (automatic backend deployment)

**Architecture:** Frontend (Netlify) + Backend (Railway)
- Frontend serves static files with CDN
- Backend provides FastAPI endpoints
- Environment-aware API URLs (localhost vs production)

## Project Structure

- `concordance_api.py` - FastAPI backend with search and file viewing endpoints
- `static/` - Frontend files
  - `index.html` - Main application interface with streamlined UX
  - `app.js` - JavaScript logic for KWIC search and display
- `samples/` - Corpus text files (Brown Corpus samples)
- `test_concordance.py` - Comprehensive test suite (22 tests)
- `pyproject.toml` - Modern dependency management
- `concordance-prd.md` - Product requirements document

## Notes
