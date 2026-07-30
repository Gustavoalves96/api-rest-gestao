from httpx import AsyncClient


async def _criar_produto(client: AsyncClient, headers: dict[str, str], **overrides):
    payload = {
        "sku": "SKU-001",
        "nome": "Teclado Mecânico",
        "descricao": "ABNT2",
        "preco": 19990,  # centavos = R$ 199,90
        "quantidade_estoque": 10,
    }
    payload.update(overrides)
    return await client.post("/produtos", json=payload, headers=headers)


async def test_criar_produto_exige_auth(client: AsyncClient) -> None:
    resposta = await _criar_produto(client, headers={})
    assert resposta.status_code == 401


async def test_criar_e_obter_produto(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    resposta = await _criar_produto(client, auth_headers)
    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["preco"] == 19990
    produto_id = corpo["id"]

    obter = await client.get(f"/produtos/{produto_id}")
    assert obter.status_code == 200
    assert obter.json()["sku"] == "SKU-001"


async def test_sku_duplicado(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    await _criar_produto(client, auth_headers)
    resposta = await _criar_produto(client, auth_headers)
    assert resposta.status_code == 409


async def test_preco_invalido(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    resposta = await _criar_produto(client, auth_headers, preco=0)
    assert resposta.status_code == 422


async def test_obter_inexistente(client: AsyncClient) -> None:
    resposta = await client.get("/produtos/999")
    assert resposta.status_code == 404


async def test_atualizar_produto(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    criado = await _criar_produto(client, auth_headers)
    produto_id = criado.json()["id"]

    resposta = await client.patch(
        f"/produtos/{produto_id}",
        json={"preco": 14990, "quantidade_estoque": 5},
        headers=auth_headers,
    )
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["preco"] == 14990
    assert corpo["quantidade_estoque"] == 5


async def test_remover_produto(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    criado = await _criar_produto(client, auth_headers)
    produto_id = criado.json()["id"]

    remover = await client.delete(f"/produtos/{produto_id}", headers=auth_headers)
    assert remover.status_code == 204

    obter = await client.get(f"/produtos/{produto_id}")
    assert obter.status_code == 404
