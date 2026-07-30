from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.database import get_session
from app.dependencies import get_payment_gateway
from app.main import app
from app.models import Base
from app.services.gateways.fake import FakeGateway

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
WEBHOOK_SECRET = "segredo-de-teste"


@pytest_asyncio.fixture
async def gateway() -> FakeGateway:
    """Gateway fake isolado por teste (estado não vaza entre testes)."""
    return FakeGateway(webhook_secret=WEBHOOK_SECRET, expira_minutos=30)


@pytest_asyncio.fixture
async def client(gateway: FakeGateway) -> AsyncGenerator[AsyncClient, None]:
    """Client HTTP com banco SQLite em memória e gateway fake, por teste."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    session_maker = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async def override_get_session() -> AsyncGenerator:
        async with session_maker() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_payment_gateway] = lambda: gateway

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
    await engine.dispose()


@pytest_asyncio.fixture
async def auth_headers(client: AsyncClient) -> dict[str, str]:
    """Registra e autentica um usuário, devolvendo o header Authorization."""
    await client.post(
        "/auth/register",
        json={"email": "user@example.com", "nome": "Usuária Teste", "senha": "senha-forte-123"},
    )
    resposta = await client.post(
        "/auth/login",
        data={"username": "user@example.com", "password": "senha-forte-123"},
    )
    token = resposta.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
