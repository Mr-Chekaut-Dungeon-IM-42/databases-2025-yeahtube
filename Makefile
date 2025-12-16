generate-migration:
	docker compose exec backend uv run alembic -c app/alembic.ini revision --autogenerate -m "$(message)"

migrate-upgrade-head:
	docker compose exec backend uv run alembic -c app/alembic.ini upgrade head

migrate-downgrade-one:
	docker compose exec backend uv run alembic -c app/alembic.ini downgrade -1

populate:
	docker compose exec backend uv run python app/populate.py

test:
	docker compose exec -w /app/app backend uv run pytest -v