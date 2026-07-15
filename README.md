# API REST — Gestão de Estoque e Pedidos

API REST de exemplo (domínio ERP) para gestão de **estoque** e **pedidos**, com
autenticação JWT, camadas bem separadas (`router → service → repository → model`)
e testes automatizados.

## Stack

Python 3.12+ · FastAPI · Pydantic v2 · SQLAlchemy 2.0 (async) · Alembic ·
PostgreSQL · pytest · ruff · uv.

## Como rodar

```bash
uv sync                                   # instala dependências
cp .env.example .env                      # configure o banco e o segredo JWT
uv run alembic upgrade head               # aplica as migrations
uv run uvicorn app.main:app --reload      # sobe a API em http://localhost:8000
```

Documentação interativa em `http://localhost:8000/docs`.

## Testes e qualidade

```bash
uv run ruff check .    # lint
uv run pytest          # testes
```

Os testes usam um banco SQLite isolado, criado e destruído a cada execução — não
tocam no banco de desenvolvimento.

## Arquitetura

O fluxo de uma requisição segue as camadas:

- **router** — só HTTP: valida entrada, define status e resposta.
- **service** — regra de negócio (ex.: baixa de estoque ao criar pedido).
- **repository** — acesso a dados; todas as queries ficam isoladas aqui.
- **model** — mapeamento SQLAlchemy das tabelas.

Erros de domínio são levantados nos services e convertidos em respostas HTTP por
handlers registrados em `app/main.py`.
