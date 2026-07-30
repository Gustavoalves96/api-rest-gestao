from httpx import AsyncClient


async def _criar_produto(
    client: AsyncClient, headers: dict[str, str], sku: str, estoque: int, preco: int
) -> int:
    resposta = await client.post(
        "/produtos",
        json={"sku": sku, "nome": f"Produto {sku}", "preco": preco, "quantidade_estoque": estoque},
        headers=headers,
    )
    return resposta.json()["id"]


async def test_criar_pedido_nao_mexe_no_estoque(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    # A baixa de estoque só acontece na confirmação do pagamento.
    produto_id = await _criar_produto(client, auth_headers, "P-1", estoque=10, preco=5000)

    resposta = await client.post(
        "/pedidos",
        json={"itens": [{"produto_id": produto_id, "quantidade": 3}]},
        headers=auth_headers,
    )
    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["status"] == "pendente"
    assert corpo["total"] == 15000  # 3 x 5000 centavos
    assert corpo["itens"][0]["subtotal"] == 15000

    produto = await client.get(f"/produtos/{produto_id}")
    assert produto.json()["quantidade_estoque"] == 10  # inalterado


async def test_pedido_rejeita_quantidade_acima_do_estoque(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    # A criação recusa pedido acima do estoque disponível (verificação de
    # disponibilidade, sem reservar).
    produto_id = await _criar_produto(client, auth_headers, "P-2", estoque=2, preco=1000)
    resposta = await client.post(
        "/pedidos",
        json={"itens": [{"produto_id": produto_id, "quantidade": 5}]},
        headers=auth_headers,
    )
    assert resposta.status_code == 409

    # O estoque não foi alterado.
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


async def test_cancelar_pedido_pendente_nao_devolve_estoque(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    # Pedido nunca pago não baixou estoque; cancelar não deve devolver nada.
    produto_id = await _criar_produto(client, auth_headers, "P-3", estoque=10, preco=2000)
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
    produto_id = await _criar_produto(client, auth_headers, "P-4", estoque=5, preco=2000)
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
