.PHONY: setup dev ui demo check lint typecheck test integration build docker seed benchmark

setup:
	uv sync --frozen --extra dev
	cd frontend && npm ci

dev:
	uv run uvicorn agent_bucket.app:create_app --factory --host 127.0.0.1 --workers 1

ui:
	cd frontend && npm run dev

demo:
	AB_SOURCE=demo AB_EMBEDDING_PROVIDER=hash uv run uvicorn agent_bucket.app:create_app --factory --host 127.0.0.1 --workers 1

lint:
	uv run ruff check backend tests scripts benchmarks
	uv run ruff format --check backend tests scripts benchmarks
	cd frontend && npm run lint

typecheck:
	uv run mypy
	cd frontend && npm run typecheck

test:
	uv run pytest -m 'not integration and not models'
	cd frontend && npm test

check: lint typecheck test build

integration:
	AB_TEST_S3_ENDPOINT=http://127.0.0.1:9000 uv run pytest -m integration

seed:
	uv run python scripts/seed_minio.py

build:
	cd frontend && npm run build

docker:
	docker compose up --build -d

benchmark:
	uv run python benchmarks/run.py
