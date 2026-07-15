from httpx import AsyncClient


async def _criar_produto(
    client: AsyncClient, headers: dict[str, str], sku: str, estoque: int, preco: str
) -> int:
    resposta = await client.post(
        "/produtos",
        json={
            "sku": sku,
            "nome": f"Produto {sku}",
            "preco": preco,
            "quantidade_estoque": estoque,
        },
        headers=headers,
    )
    return resposta.json()["id"]


async def test_criar_pedido_da_baixa_no_estoque(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    produto_id = await _criar_produto(client, auth_headers, "P-1", estoque=10, preco="50.00")

    resposta = await client.post(
        "/pedidos",
        json={"itens": [{"produto_id": produto_id, "quantidade": 3}]},
        headers=auth_headers,
    )
    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["status"] == "pendente"
    assert corpo["total"] == "150.00"
    assert corpo["itens"][0]["subtotal"] == "150.00"

    produto = await client.get(f"/produtos/{produto_id}")
    assert produto.json()["quantidade_estoque"] == 7


async def test_estoque_insuficiente(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    produto_id = await _criar_produto(client, auth_headers, "P-2", estoque=2, preco="10.00")

    resposta = await client.post(
        "/pedidos",
        json={"itens": [{"produto_id": produto_id, "quantidade": 5}]},
        headers=auth_headers,
    )
    assert resposta.status_code == 409

    # O estoque não pode ter sido alterado quando o pedido falha.
    produto = await client.get(f"/produtos/{produto_id}")
    assert produto.json()["quantidade_estoque"] == 2


async def test_pedido_com_produto_inexistente(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    resposta = await client.post(
        "/pedidos",
        json={"itens": [{"produto_id": 999, "quantidade": 1}]},
        headers=auth_headers,
    )
    assert resposta.status_code == 404


async def test_cancelar_pedido_devolve_estoque(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    produto_id = await _criar_produto(client, auth_headers, "P-3", estoque=10, preco="20.00")
    pedido = await client.post(
        "/pedidos",
        json={"itens": [{"produto_id": produto_id, "quantidade": 4}]},
        headers=auth_headers,
    )
    pedido_id = pedido.json()["id"]

    cancelar = await client.post(f"/pedidos/{pedido_id}/cancelar", headers=auth_headers)
    assert cancelar.status_code == 200
    assert cancelar.json()["status"] == "cancelado"

    produto = await client.get(f"/produtos/{produto_id}")
    assert produto.json()["quantidade_estoque"] == 10


async def test_cancelar_pedido_ja_cancelado(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    produto_id = await _criar_produto(client, auth_headers, "P-4", estoque=5, preco="20.00")
    pedido = await client.post(
        "/pedidos",
        json={"itens": [{"produto_id": produto_id, "quantidade": 1}]},
        headers=auth_headers,
    )
    pedido_id = pedido.json()["id"]

    await client.post(f"/pedidos/{pedido_id}/cancelar", headers=auth_headers)
    segunda = await client.post(f"/pedidos/{pedido_id}/cancelar", headers=auth_headers)
    assert segunda.status_code == 422


async def test_pedido_exige_autenticacao(client: AsyncClient) -> None:
    resposta = await client.post("/pedidos", json={"itens": [{"produto_id": 1, "quantidade": 1}]})
    assert resposta.status_code == 401
