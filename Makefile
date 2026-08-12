.PHONY: dev api web test lint docker demo

dev:
	docker compose up --build

api:
	cd apps/api && uvicorn docurule.main:app --reload --port 8000

web:
	cd apps/web && npm run dev

test:
	cd apps/api && pytest
	cd apps/web && npm run test -- --run

lint:
	cd apps/api && ruff check .
	cd apps/web && npm run lint

# Start the deterministic procurement demo in the same containerized setup
# documented in README.md. The old samples/generate_demo_bundle.py entrypoint
# no longer exists; the canonical fixture now lives in demo/three-way-match/.
demo:
	docker compose up --build
