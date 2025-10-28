## AI Powered Nutrition Tracker  
[![CI/CD](https://github.com/Pratyush-2/ai-powered-nutrition-tracker/actions/workflows/ci.yml/badge.svg)](https://github.com/Pratyush-2/ai-powered-nutrition-tracker/actions/workflows/ci.yml)
<!-- Optionally add Codecov if configured
[![codecov](https://codecov.io/gh/Pratyush-2/ai-powered-nutrition-tracker/branch/main/graph/badge.svg?token=YOUR_TOKEN)](https://codecov.io/gh/Pratyush-2/ai-powered-nutrition-tracker)
-->

An end-to-end, AI-assisted nutrition tracker:
- FastAPI backend (Python) with SQLite by default
- Embedded AI/RAG helpers for food lookup and suggestions
- Flutter client app in `nutrition_app/` for Android, iOS, web, desktop

---

## Prerequisites
- Python 3.11+
- pip
- Git
- Optional: Docker and Docker Compose
- Optional (for mobile app): Flutter SDK 3.22+ and platform toolchains (Android Studio/Xcode)

---

## Folder structure
```
.
├─ app/                      # FastAPI application
│  ├─ ai/                    # AI endpoints and helpers (LLM, embeddings, retriever)
│  ├─ ai_pipeline/           # Image recognition, RAG, nutrition engine, ML models
│  ├─ indexes/               # Vector index files (FAISS/metadata)
│  ├─ models/                # Serialized models (e.g., joblib)
│  ├─ services/              # Service layer (e.g., food search)
│  ├─ main.py                # FastAPI app entry
│  ├─ config.py              # App settings and DB URL
│  ├─ database.py            # SQLAlchemy engine/session
│  ├─ crud.py, schemas.py    # Data access and pydantic schemas
│  └─ utils.py               # Utilities
├─ alembic/                  # DB migrations
├─ data/                     # Example datasets and local DBs (ignored in prod)
├─ docs/                     # Additional documentation
├─ models/                   # Extra model artifacts
├─ nutrition_app/            # Flutter client application
├─ scripts/                  # Build/index/test scripts
├─ tests/                    # Pytest tests
├─ docker-compose.yml        # Optional runtime with Docker
├─ Dockerfile                # Backend Dockerfile
├─ requirements.txt          # Python dependencies
└─ .env.example              # Sample environment variables
```

---

## Quick start (backend)
1) Create and activate a virtual env
```powershell
python -m venv venv
./venv/Scripts/Activate.ps1
```

2) Install dependencies
```bash
pip install -r requirements.txt
```

3) Configure environment
```bash
cp .env.example .env
# edit .env if needed; defaults use SQLite in app/nutrition_app.db
```

4) Run the API
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

5) Open docs
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## Environment variables
The backend reads configuration via `.env` and `app/config.py`.
- `DATABASE_URL` (optional) — defaults to SQLite at `app/nutrition_app.db`

Example `.env` (see `.env.example`):
```
DATABASE_URL=sqlite:///app/nutrition_app.db
```

---

## Using Docker
Build and run the backend with Docker:
```bash
docker build -t ai-nutrition-backend .
docker run -p 8000:8000 --env-file .env ai-nutrition-backend
```

With docker-compose:
```bash
docker compose up --build
```

---

## Flutter app (optional client)
Inside `nutrition_app/`:
```bash
flutter pub get
flutter run   # or: flutter build apk / ios / web
```

The mobile app talks to the FastAPI backend. If running on a device/emulator, ensure the app points to your machine’s IP and port 8000.

---

## How it works (architecture)
- **FastAPI + SQLAlchemy**: REST endpoints for foods, logs, goals, and AI helpers. DB tables are created on startup (`app/main.py`).
- **AI pipeline (`app/ai_pipeline/`)**:
  - Image/Barcode recognition to identify food items.
  - RAG module using vector indexes from `app/indexes/` to enrich context.
  - Nutrition engine and optional ML models for predictions and suggestions.
- **AI endpoints (`app/ai/ai_routes.py`)**: Exposes AI features via HTTP.
- **Services (`app/services/food_search.py`)**: Search food by name and return nutrition details.

Typical flow:
1) User logs food (quantity, date) via API or Flutter app.
2) Backend stores entries, computes daily totals, and returns guidance.
3) AI helpers provide recognition, retrieval, and explanation features.

---

## Common API endpoints
- `POST /foods/` — create a food
- `GET /foods/` — list foods
- `POST /logs/` — create a daily log
- `GET /logs/?user_id=...&log_date=YYYY-MM-DD` — get logs
- `PUT /logs/{log_id}` — update a log
- `DELETE /logs/{log_id}` — delete a log
- `GET /totals/{user_id}/{log_date}` — daily totals
- `POST /goals/` — create a user goal
- `GET /goals/` — list all goals
- `GET /goals/{user_id}` — goals for user
- `PUT /goals/{goal_id}` — update a goal
- `GET /search-food/{food_name}` — search nutrition by food name
- AI routes — see `/docs` for `app/ai/ai_routes.py`

---

## Development
Run tests:
```bash
pytest -q
```

Format/lint (example):
```bash
ruff check .
black .
```

---

## Screenshots / Demo
Place images or GIFs under `screenshots/` and they will render here.

Example:
```markdown
![Home](screenshots/home.png)
![Log Food](screenshots/log_food.png)
```

---

## Security & secrets
- Never commit secrets. Files like cloud keys must stay out of VCS.
- Sensitive files are ignored via `.gitignore`. Rotate any credentials if exposed.

---

## Troubleshooting
- If the API starts but endpoints 404, ensure you’re hitting `http://localhost:8000` and that routers are included in `app/main.py`.
- If Flutter can’t reach the API on device/emulator, use your machine IP instead of `localhost`.

---

## License
MIT (or your chosen license)

---

## Contributing
Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on setting up your environment, coding standards, and submitting PRs.

