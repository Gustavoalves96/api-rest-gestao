from httpx import AsyncClient


async def test_registrar_usuario(client: AsyncClient) -> None:
    resposta = await client.post(
        "/auth/register",
        json={"email": "novo@example.com", "nome": "Novo", "senha": "senha-forte-123"},
    )
    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["email"] == "novo@example.com"
    assert "senha" not in corpo and "senha_hash" not in corpo


async def test_registrar_email_duplicado(client: AsyncClient) -> None:
    payload = {"email": "dup@example.com", "nome": "Dup", "senha": "senha-forte-123"}
    await client.post("/auth/register", json=payload)
    resposta = await client.post("/auth/register", json=payload)
    assert resposta.status_code == 409


async def test_login_sucesso(client: AsyncClient) -> None:
    await client.post(
        "/auth/register",
        json={"email": "log@example.com", "nome": "Log", "senha": "senha-forte-123"},
    )
    resposta = await client.post(
        "/auth/login",
        data={"username": "log@example.com", "password": "senha-forte-123"},
    )
    assert resposta.status_code == 200
    assert resposta.json()["token_type"] == "bearer"


async def test_login_senha_incorreta(client: AsyncClient) -> None:
    await client.post(
        "/auth/register",
        json={"email": "log2@example.com", "nome": "Log2", "senha": "senha-forte-123"},
    )
    resposta = await client.post(
        "/auth/login",
        data={"username": "log2@example.com", "password": "errada"},
    )
    assert resposta.status_code == 401


async def test_me_exige_autenticacao(client: AsyncClient) -> None:
    resposta = await client.get("/auth/me")
    assert resposta.status_code == 401


async def test_me_retorna_usuario(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    resposta = await client.get("/auth/me", headers=auth_headers)
    assert resposta.status_code == 200
    assert resposta.json()["email"] == "user@example.com"
