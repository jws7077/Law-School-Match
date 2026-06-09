# Law School Match

MVP scaffold for a law school recommendation platform using:
- **Frontend:** Next.js + TypeScript + Tailwind CSS
- **Backend:** FastAPI (Python)
- **Database:** PostgreSQL

See `/docs/INITIAL_PROJECT_ARCHITECTURE.md` for the full architecture, file-by-file explanations, schema, API plan, Docker setup, and local development instructions.

## Local Run

1. Start the stack with `docker compose up --build`.
2. Open the frontend at `http://localhost:3000`.
3. The FastAPI docs are available at `http://localhost:8000/docs`.

The PostgreSQL container initializes with the schema in `database/schema.sql` and seeds 20 realistic sample law schools from `database/002_seed_data.sql`.

## ABA 509 Ingestion

To import ABA 509 report exports into PostgreSQL, run the backend importer against a CSV, TSV, JSON file, or a directory of report exports:

```bash
cd backend
python -m app.ingestion.aba509 ../path/to/reports
```

The importer normalizes school names, upserts yearly statistics, tuition, and employment outcomes, and records each batch in `aba_509_import_runs`.
