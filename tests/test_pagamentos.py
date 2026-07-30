from httpx import AsyncClient

from tests.helpers import criar_cobranca, criar_pedido, criar_produto


async def test_criar_cobranca_pix(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    produto_id = await criar_produto(client, auth_headers, "PAG-1", estoque=10, preco=5000)
    pedido_id = await criar_pedido(client, auth_headers, produto_id, 2)

    resposta = await client.post(f"/pedidos/{pedido_id}/pagamento", headers=auth_headers)
    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["status"] == "pendente"
    assert corpo["valor"] == 10000  # 2 x 5000 centavos
    assert corpo["metodo"] == "pix"
    assert corpo["qr_code"] and corpo["copia_e_cola"]


async def test_cobranca_reaproveitada(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    # Pedir a cobrança duas vezes não gera duas cobranças no gateway.
    produto_id = await criar_produto(client, auth_headers, "PAG-2", estoque=10, preco=1000)
    pedido_id = await criar_pedido(client, auth_headers, produto_id, 1)

    primeira = await criar_cobranca(client, auth_headers, pedido_id)
    segunda = await criar_cobranca(client, auth_headers, pedido_id)
    assert primeira["external_id"] == segunda["external_id"]


async def test_criar_cobranca_exige_auth(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    produto_id = await criar_produto(client, auth_headers, "PAG-3", estoque=10, preco=1000)
    pedido_id = await criar_pedido(client, auth_headers, produto_id, 1)

    resposta = await client.post(f"/pedidos/{pedido_id}/pagamento")
    assert resposta.status_code == 401


async def test_obter_cobranca(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    produto_id = await criar_produto(client, auth_headers, "PAG-4", estoque=10, preco=2500)
    pedido_id = await criar_pedido(client, auth_headers, produto_id, 3)
    await criar_cobranca(client, auth_headers, pedido_id)

    resposta = await client.get(f"/pedidos/{pedido_id}/pagamento", headers=auth_headers)
    assert resposta.status_code == 200
    assert resposta.json()["valor"] == 7500
