"""Auxiliares compartilhados pelos testes de pagamento e webhook."""

import json

from httpx import AsyncClient

from tests.conftest import WEBHOOK_SECRET


async def criar_produto(
    client: AsyncClient, headers: dict[str, str], sku: str, estoque: int, preco: int
) -> int:
    resposta = await client.post(
        "/produtos",
        json={"sku": sku, "nome": f"Produto {sku}", "preco": preco, "quantidade_estoque": estoque},
        headers=headers,
    )
    return resposta.json()["id"]


async def criar_pedido(
    client: AsyncClient, headers: dict[str, str], produto_id: int, quantidade: int
) -> int:
    resposta = await client.post(
        "/pedidos",
        json={"itens": [{"produto_id": produto_id, "quantidade": quantidade}]},
        headers=headers,
    )
    return resposta.json()["id"]


async def criar_cobranca(client: AsyncClient, headers: dict[str, str], pedido_id: int) -> dict:
    resposta = await client.post(f"/pedidos/{pedido_id}/pagamento", headers=headers)
    return resposta.json()


def corpo_webhook(event_id: str, charge_id: str, tipo: str = "PAYMENT_CONFIRMED") -> bytes:
    return json.dumps({"event_id": event_id, "charge_id": charge_id, "tipo": tipo}).encode()


def header_webhook(valido: bool = True) -> dict[str, str]:
    return {"x-webhook-token": WEBHOOK_SECRET if valido else "token-errado"}
