# Initial Project Architecture: Law School Match

This scaffold creates a scalable foundation for a **Next.js + TypeScript + Tailwind** frontend, a **FastAPI** backend, and a **PostgreSQL** database.

## 1) Frontend folder structure

```text
frontend/
  Dockerfile
  .env.example
  package.json
  next.config.ts
  next-env.d.ts
  tsconfig.json
  postcss.config.js
  tailwind.config.ts
  src/
    app/
      globals.css
      layout.tsx
      page.tsx
    lib/
      api.ts
```

## 2) Backend folder structure

```text
backend/
  Dockerfile
  .env.example
  requirements.txt
  app/
    __init__.py
    main.py
    api/
      __init__.py
      v1/
        __init__.py
        router.py
        endpoints/
          __init__.py
          health.py
          schools.py
          match.py
    core/
      __init__.py
      config.py
    db/
      __init__.py
      session.py
    models/
      __init__.py
      base.py
    schemas/
      __init__.py
      school.py
      match.py
      profile.py
```

## 3) Database schema

Database schema is defined in `/database/schema.sql` with:

- `career_goals`
- `schools`
- `school_career_focus` (join table)
- `student_profiles`
- `match_results`

This models GPA/LSAT, geography, goals, cost sensitivity, lifestyle preferences, and generated recommendation matches.

## 4) API endpoints

Base path: `/api/v1`

- `GET /health` – basic health check
- `GET /schools` – list schools (placeholder in-memory data)
- `GET /schools/{school_id}` – fetch one school
- `POST /matches/preview` – preview recommendation score from profile inputs

## 5) Environment variable requirements

Shared (`/.env.example`):
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_DB`
- `POSTGRES_HOST`
- `POSTGRES_PORT`
- `BACKEND_HOST`
- `BACKEND_PORT`
- `NEXT_PUBLIC_API_BASE_URL`

Backend (`/backend/.env.example`):
- `DATABASE_URL`
- `BACKEND_HOST`
- `BACKEND_PORT`
- `FRONTEND_ORIGIN`

Frontend (`/frontend/.env.example`):
- `NEXT_PUBLIC_API_BASE_URL`

## 6) Docker setup

- `docker-compose.yml` starts `db`, `backend`, and `frontend`
- `/backend/Dockerfile` builds and runs FastAPI via Uvicorn
- `/frontend/Dockerfile` builds and runs Next.js in dev mode for local iteration
- `database/schema.sql` is mounted for PostgreSQL first-run initialization

## 7) Local development setup

Use `/Makefile`:
- `make setup-frontend` – install frontend dependencies
- `make setup-backend` – create Python venv and install backend dependencies
- `make up` – run the full stack with Docker Compose
- `make down` – stop stack and remove volumes

---

## File-by-file explanation

### Root files

- `/.gitignore` — prevents committing local env files and build/dependency artifacts.
- `/.env.example` — shared sample environment variables for local and dockerized development.
- `/docker-compose.yml` — orchestrates PostgreSQL, FastAPI, and Next.js services.
- `/Makefile` — standard local developer shortcuts for setup and lifecycle commands.

### Frontend files

- `/frontend/Dockerfile` — container image definition for Next.js frontend.
- `/frontend/.env.example` — frontend runtime config (API base URL).
- `/frontend/package.json` — frontend dependencies and scripts.
- `/frontend/next.config.ts` — Next.js runtime configuration.
- `/frontend/next-env.d.ts` — Next.js TypeScript type references.
- `/frontend/tsconfig.json` — TypeScript compiler configuration and path aliases.
- `/frontend/postcss.config.js` — PostCSS config wiring Tailwind and Autoprefixer.
- `/frontend/tailwind.config.ts` — Tailwind scanning/theming config.
- `/frontend/src/app/globals.css` — global styles and Tailwind directives.
- `/frontend/src/app/layout.tsx` — root HTML shell and app metadata.
- `/frontend/src/app/page.tsx` — initial landing page placeholder.
- `/frontend/src/lib/api.ts` — centralized API base URL helper for fetchers.

### Backend files

- `/backend/Dockerfile` — container image definition for FastAPI backend.
- `/backend/.env.example` — backend-specific env vars.
- `/backend/requirements.txt` — backend Python dependencies.
- `/backend/app/__init__.py` — package marker for app module.
- `/backend/app/main.py` — FastAPI app creation, CORS config, router registration.
- `/backend/app/api/__init__.py` — package marker for API module.
- `/backend/app/api/v1/__init__.py` — package marker for API v1 module.
- `/backend/app/api/v1/router.py` — versioned API route composition.
- `/backend/app/api/v1/endpoints/__init__.py` — package marker for endpoint module.
- `/backend/app/api/v1/endpoints/health.py` — health endpoint.
- `/backend/app/api/v1/endpoints/schools.py` — school listing/detail endpoints.
- `/backend/app/api/v1/endpoints/match.py` — recommendation preview endpoint.
- `/backend/app/core/__init__.py` — package marker for core module.
- `/backend/app/core/config.py` — typed environment-backed configuration.
- `/backend/app/db/__init__.py` — package marker for database module.
- `/backend/app/db/session.py` — SQLAlchemy engine initialization.
- `/backend/app/models/__init__.py` — package marker for ORM models module.
- `/backend/app/models/base.py` — SQLAlchemy declarative base for future models.
- `/backend/app/schemas/__init__.py` — package marker for schema module.
- `/backend/app/schemas/school.py` — Pydantic schema for school responses.
- `/backend/app/schemas/match.py` — Pydantic request/response schema for match preview.
- `/backend/app/schemas/profile.py` — Pydantic schema for student profile payloads.

### Database file

- `/database/schema.sql` — PostgreSQL DDL tables, constraints, and indexes for matching data.
