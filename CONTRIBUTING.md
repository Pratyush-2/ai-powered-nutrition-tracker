## Contributing to AI Powered Nutrition Tracker

Thanks for your interest in contributing! This guide covers local setup, coding standards, and how to submit changes.

### Getting started
1) Fork the repository and clone your fork
2) Create a virtual environment and install dependencies
```bash
python -m venv venv
source venv/bin/activate   # Windows: .\\venv\\Scripts\\activate
pip install -r requirements.txt
```

3) Create a feature branch
```bash
git checkout -b feature/your-feature
```

4) Run tests and linters locally
```bash
pytest -q
ruff check . || true
black --check . || true
```

5) Commit using clear messages and open a Pull Request

### Project structure highlights
- Backend FastAPI: `app/`
- Tests: `tests/`
- Flutter app (optional client): `nutrition_app/`
- Docs: `docs/`

### Coding standards
- Python: match existing style; prefer type hints where helpful
- Keep functions small and focused; add concise comments for non-obvious logic
- Include/adjust tests for new behaviors

### Submitting a Pull Request
- Rebase on latest `main` before opening the PR
- Ensure CI is green (tests, lint, type checks)
- Fill in the PR template with context and testing notes

### Security
- Do not commit secrets. If you suspect a secret was committed, notify maintainers immediately so we can rotate and scrub history.

### Questions
Open a discussion or issue if you’re unsure about anything — we’re happy to help.


