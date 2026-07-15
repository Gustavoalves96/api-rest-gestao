.PHONY: help install run test lint format check migrate revision up down

help:  ## Lista os comandos disponíveis
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

install:  ## Instala as dependências
	uv sync

run:  ## Sobe o servidor de desenvolvimento
	uv run uvicorn app.main:app --reload

test:  ## Roda a suíte de testes
	uv run pytest

lint:  ## Verifica o estilo com ruff
	uv run ruff check .

format:  ## Formata o código com ruff
	uv run ruff format .

check: lint test  ## Roda lint e testes (usado no CI)

migrate:  ## Aplica as migrations pendentes
	uv run alembic upgrade head

revision:  ## Gera uma migration (uso: make revision m="descrição")
	uv run alembic revision --autogenerate -m "$(m)"

up:  ## Sobe a stack completa (Postgres + API) via Docker
	docker compose up --build

down:  ## Derruba a stack e remove os volumes
	docker compose down -v
