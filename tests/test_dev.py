from httpx import AsyncClient

from tests.helpers import criar_cobranca, criar_pedido, criar_produto


async def test_simular_confirma_e_baixa_estoque(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    produto_id = await criar_produto(client, auth_headers, "DEV-1", estoque=10, preco=5000)
    pedido_id = await criar_pedido(client, auth_headers, produto_id, 3)
    await criar_cobranca(client, auth_headers, pedido_id)

    resposta = await client.post(
        f"/dev/pagamentos/{pedido_id}/simular",
        json={"resultado": "confirmar"},
        headers=auth_headers,
    )
    assert resposta.status_code == 200
    assert resposta.json()["status"] == "confirmado"

    produto = await client.get(f"/produtos/{produto_id}")
    assert produto.json()["quantidade_estoque"] == 7


async def test_simular_expiracao_cancela_pedido(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    produto_id = await criar_produto(client, auth_headers, "DEV-2", estoque=10, preco=5000)
    pedido_id = await criar_pedido(client, auth_headers, produto_id, 2)
    await criar_cobranca(client, auth_headers, pedido_id)

    resposta = await client.post(
        f"/dev/pagamentos/{pedido_id}/simular",
        json={"resultado": "expirar"},
        headers=auth_headers,
    )
    assert resposta.status_code == 200
    assert resposta.json()["status"] == "expirado"

    pedido = await client.get(f"/pedidos/{pedido_id}", headers=auth_headers)
    assert pedido.json()["status"] == "cancelado"


async def test_simular_exige_autenticacao(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    produto_id = await criar_produto(client, auth_headers, "DEV-3", estoque=5, preco=1000)
    pedido_id = await criar_pedido(client, auth_headers, produto_id, 1)
    await criar_cobranca(client, auth_headers, pedido_id)

    resposta = await client.post(f"/dev/pagamentos/{pedido_id}/simular", json={})
    assert resposta.status_code == 401
