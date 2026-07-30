from httpx import AsyncClient

from app.services.gateways.fake import FakeGateway
from tests.helpers import corpo_webhook, criar_cobranca, criar_pedido, criar_produto, header_webhook


async def _preparar_cobranca(
    client: AsyncClient, headers: dict[str, str], estoque: int, quantidade: int, preco: int = 1000
) -> tuple[int, str]:
    produto_id = await criar_produto(client, headers, "WH", estoque=estoque, preco=preco)
    pedido_id = await criar_pedido(client, headers, produto_id, quantidade)
    cobranca = await criar_cobranca(client, headers, pedido_id)
    return produto_id, cobranca["external_id"]


async def test_webhook_assinatura_invalida(
    client: AsyncClient, auth_headers: dict[str, str], gateway: FakeGateway
) -> None:
    produto_id, charge_id = await _preparar_cobranca(client, auth_headers, estoque=10, quantidade=3)
    gateway.marcar_pago(charge_id)

    resposta = await client.post(
        "/webhooks/pagamentos",
        content=corpo_webhook("evt-1", charge_id),
        headers=header_webhook(valido=False),
    )
    assert resposta.status_code == 401

    # Nada foi processado: estoque intacto.
    produto = await client.get(f"/produtos/{produto_id}")
    assert produto.json()["quantidade_estoque"] == 10


async def test_webhook_confirma_e_baixa_estoque(
    client: AsyncClient, auth_headers: dict[str, str], gateway: FakeGateway
) -> None:
    produto_id, charge_id = await _preparar_cobranca(client, auth_headers, estoque=10, quantidade=3)
    gateway.marcar_pago(charge_id)

    resposta = await client.post(
        "/webhooks/pagamentos",
        content=corpo_webhook("evt-1", charge_id),
        headers=header_webhook(),
    )
    assert resposta.status_code == 200

    produto = await client.get(f"/produtos/{produto_id}")
    assert produto.json()["quantidade_estoque"] == 7  # baixou 3


async def test_webhook_duplicado_processa_uma_vez(
    client: AsyncClient, auth_headers: dict[str, str], gateway: FakeGateway
) -> None:
    produto_id, charge_id = await _preparar_cobranca(client, auth_headers, estoque=10, quantidade=3)
    gateway.marcar_pago(charge_id)

    corpo = corpo_webhook("evt-dup", charge_id)
    r1 = await client.post("/webhooks/pagamentos", content=corpo, headers=header_webhook())
    r2 = await client.post("/webhooks/pagamentos", content=corpo, headers=header_webhook())
    assert r1.status_code == 200 and r2.status_code == 200

    produto = await client.get(f"/produtos/{produto_id}")
    assert produto.json()["quantidade_estoque"] == 7  # baixou só uma vez


async def test_webhook_estoque_insuficiente_reverte_tudo(
    client: AsyncClient, auth_headers: dict[str, str], gateway: FakeGateway
) -> None:
    # Pedido de 5 unidades com estoque 2: a confirmação deve reverter por completo.
    produto_id, charge_id = await _preparar_cobranca(client, auth_headers, estoque=2, quantidade=5)
    pedido_id = (await client.get("/pedidos", headers=auth_headers)).json()[0]["id"]
    gateway.marcar_pago(charge_id)

    resposta = await client.post(
        "/webhooks/pagamentos",
        content=corpo_webhook("evt-1", charge_id),
        headers=header_webhook(),
    )
    assert resposta.status_code == 200  # webhook responde 200 mesmo com falha de processamento

    produto = await client.get(f"/produtos/{produto_id}")
    assert produto.json()["quantidade_estoque"] == 2  # inalterado

    pedido = await client.get(f"/pedidos/{pedido_id}", headers=auth_headers)
    assert pedido.json()["status"] == "pendente"  # não foi marcado como pago


async def test_estorno_devolve_estoque(
    client: AsyncClient, auth_headers: dict[str, str], gateway: FakeGateway
) -> None:
    produto_id, charge_id = await _preparar_cobranca(client, auth_headers, estoque=10, quantidade=4)
    pedido_id = (await client.get("/pedidos", headers=auth_headers)).json()[0]["id"]
    gateway.marcar_pago(charge_id)
    await client.post(
        "/webhooks/pagamentos", content=corpo_webhook("evt-1", charge_id), headers=header_webhook()
    )

    # Confirmado: estoque baixou para 6.
    produto = await client.get(f"/produtos/{produto_id}")
    assert produto.json()["quantidade_estoque"] == 6

    # Cancelar um pedido pago estorna e devolve o estoque.
    cancelar = await client.post(f"/pedidos/{pedido_id}/cancelar", headers=auth_headers)
    assert cancelar.status_code == 200
    assert cancelar.json()["status"] == "cancelado"

    produto = await client.get(f"/produtos/{produto_id}")
    assert produto.json()["quantidade_estoque"] == 10  # devolvido
