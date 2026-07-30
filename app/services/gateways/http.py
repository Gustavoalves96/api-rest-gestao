"""Gateway HTTP genérico.

Implementação concreta de `PaymentGateway` sobre uma API REST convencional,
falada por `httpx`. É deliberadamente genérica (não amarrada a nenhum provedor)
para servir de esqueleto: basta apontar `GATEWAY_BASE_URL` e plugar a chave.

Convenção de payloads esperada do provedor:

    POST   {base}/charges              -> cria a cobrança
    GET    {base}/charges/{id}         -> consulta a cobrança
    POST   {base}/charges/{id}/refund  -> estorna

    resposta de cobrança:
      { "id", "status", "amount", "pix": { "qr_code", "copia_e_cola", "expires_at" } }

A tradução do JSON do provedor para os nossos tipos acontece aqui dentro.
"""

import json
from collections.abc import Mapping
from datetime import datetime
from typing import Any

import httpx

from app.exceptions import AssinaturaWebhookInvalidaError, GatewayError
from app.services.gateways.base import (
    ChargeRequest,
    ChargeResult,
    RefundResult,
    StatusCobranca,
    WebhookEvent,
)

# Mapeia o status textual do provedor para o nosso status neutro.
_STATUS: dict[str, StatusCobranca] = {
    "PENDING": StatusCobranca.PENDENTE,
    "PENDENTE": StatusCobranca.PENDENTE,
    "CONFIRMED": StatusCobranca.CONFIRMADO,
    "RECEIVED": StatusCobranca.CONFIRMADO,
    "CONFIRMADO": StatusCobranca.CONFIRMADO,
    "EXPIRED": StatusCobranca.EXPIRADO,
    "EXPIRADO": StatusCobranca.EXPIRADO,
    "FAILED": StatusCobranca.FALHOU,
    "FALHOU": StatusCobranca.FALHOU,
    "REFUNDED": StatusCobranca.ESTORNADO,
    "ESTORNADO": StatusCobranca.ESTORNADO,
}


def _mapear_status(bruto: str) -> StatusCobranca:
    status = _STATUS.get(bruto.upper())
    if status is None:
        raise GatewayError(f"Status de cobrança desconhecido: {bruto!r}.")
    return status


def _parse_data(valor: Any) -> datetime | None:
    if not isinstance(valor, str) or valor == "":
        return None
    try:
        return datetime.fromisoformat(valor)
    except ValueError:
        return None


class HttpGateway:
    def __init__(self, base_url: str, api_key: str, webhook_token: str) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._webhook_token = webhook_token

    def _client(self) -> httpx.AsyncClient:
        # A chave vai só no header Authorization — nunca é logada.
        return httpx.AsyncClient(
            base_url=self._base_url,
            headers={"Authorization": f"Bearer {self._api_key}"},
            timeout=httpx.Timeout(10.0),
        )

    async def create_charge(self, req: ChargeRequest) -> ChargeResult:
        payload = {
            "external_reference": str(req.pedido_id),
            "amount": req.valor,
            "description": req.descricao,
            "billing_type": "PIX",
        }
        async with self._client() as client:
            resposta = await client.post("/charges", json=payload)
        return self._para_charge_result(resposta)

    async def get_charge(self, external_id: str) -> ChargeResult:
        async with self._client() as client:
            resposta = await client.get(f"/charges/{external_id}")
        return self._para_charge_result(resposta)

    async def refund(self, external_id: str) -> RefundResult:
        async with self._client() as client:
            resposta = await client.post(f"/charges/{external_id}/refund")
        dados = self._corpo(resposta)
        return RefundResult(
            external_id=str(dados["id"]),
            status=_mapear_status(str(dados["status"])),
        )

    def parse_webhook(self, raw_body: bytes, headers: Mapping[str, str]) -> WebhookEvent:
        # Assinatura validada ANTES de qualquer parsing de negócio.
        token = headers.get("x-webhook-token", "")
        if token != self._webhook_token:
            raise AssinaturaWebhookInvalidaError("Assinatura do webhook inválida.")
        corpo = json.loads(raw_body)
        return WebhookEvent(
            external_event_id=str(corpo["event_id"]),
            external_id=str(corpo["charge_id"]),
            tipo=str(corpo["tipo"]),
            raw=corpo,
        )

    # ---- tradução ----

    def _corpo(self, resposta: httpx.Response) -> dict[str, Any]:
        if resposta.is_error:
            # Não vaza a chave nem o corpo bruto do provedor na mensagem.
            raise GatewayError(f"Gateway respondeu {resposta.status_code}.")
        dados: Any = resposta.json()
        if not isinstance(dados, dict):
            raise GatewayError("Resposta do gateway em formato inesperado.")
        return dados

    def _para_charge_result(self, resposta: httpx.Response) -> ChargeResult:
        dados = self._corpo(resposta)
        pix = dados.get("pix") or {}
        return ChargeResult(
            external_id=str(dados["id"]),
            status=_mapear_status(str(dados["status"])),
            valor=int(dados["amount"]),
            qr_code=pix.get("qr_code"),
            copia_e_cola=pix.get("copia_e_cola"),
            expira_em=_parse_data(pix.get("expires_at")),
        )
