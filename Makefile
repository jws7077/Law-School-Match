.PHONY: setup-frontend setup-backend up down

setup-frontend:
cd frontend && npm install

setup-backend:
cd backend && python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt

up:
docker compose up --build

down:
docker compose down -v
