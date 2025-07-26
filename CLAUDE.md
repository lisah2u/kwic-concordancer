# Claude Memory

This file helps Claude understand your project and preferences.

## Plan and Review

### Before starting work
- Always use plan mode
- After the plan has completed, write it to .claude/tasks/TASK_NAME.md
- The plan should be a detailed implementation plan and reasoning for the task. Break tasks down.
- If the tasks require external knowledge or a certain package, research to get the latest knowlesge.
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

- Install dependencies: `uv pip install -r requirements.txt`
- Start server: `uv run uvicorn concordance_api:app --reload`
- Test: `uv run pytest test_concordance.py -v`
- Lint: (none configured yet)
- Access application: `http://localhost:8000`

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

Add any important project-specific information, coding conventions, or preferences here.