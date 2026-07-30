# Imagem oficial do uv com Python 3.12
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# Instala as dependências primeiro (melhor cache de camadas) sem o código-fonte.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

# Copia o restante do projeto.
COPY . .
RUN uv sync --frozen --no-dev

EXPOSE 8000

# Aplica as migrations (idempotente) e sobe a API. Usa $PORT quando o host
# define (ex.: Render); cai para 8000 localmente.
CMD ["sh", "-c", "uv run alembic upgrade head && uv run uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
