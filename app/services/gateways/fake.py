"""Gateway em memória.

Serve tanto para os testes quanto como implementação padrão enquanto não há
credenciais de um gateway real. Simula cobranças Pix e valida a assinatura do
webhook por um token compartilhado (header `x-webhook-token`).
"""

import json
import secrets
from collections.abc import Mapping
from datetime import UTC, datetime, timedelta

from app.exceptions import AssinaturaWebhookInvalidaError
from app.services.gateways.base import (
    ChargeRequest,
    ChargeResult,
    RefundResult,
    StatusCobranca,
    WebhookEvent,
)


class FakeGateway:
    def __init__(self, webhook_secret: str, expira_minutos: int = 30) -> None:
        self._webhook_secret = webhook_secret
        self._expira_minutos = expira_minutos
        self._cobrancas: dict[str, ChargeResult] = {}

    async def create_charge(self, req: ChargeRequest) -> ChargeResult:
        external_id = f"fake_{secrets.token_hex(8)}"
        resultado = ChargeResult(
            external_id=external_id,
            status=StatusCobranca.PENDENTE,
            valor=req.valor,
            qr_code=f"fake-qrcode-{external_id}",
            copia_e_cola=f"00020126fake{external_id}5204000053039865802BR",
            expira_em=datetime.now(UTC) + timedelta(minutes=self._expira_minutos),
        )
        self._cobrancas[external_id] = resultado
        return resultado

    async def get_charge(self, external_id: str) -> ChargeResult:
        return self._cobrancas[external_id]

    async def refund(self, external_id: str) -> RefundResult:
        self._transicionar(external_id, StatusCobranca.ESTORNADO)
        return RefundResult(external_id=external_id, status=StatusCobranca.ESTORNADO)

    def parse_webhook(self, raw_body: bytes, headers: Mapping[str, str]) -> WebhookEvent:
        # Assinatura validada ANTES de qualquer parsing de negócio.
        token = headers.get("x-webhook-token", "")
        if not secrets.compare_digest(token, self._webhook_secret):
            raise AssinaturaWebhookInvalidaError("Assinatura do webhook inválida.")

        corpo = json.loads(raw_body)
        return WebhookEvent(
            external_event_id=str(corpo["event_id"]),
            external_id=str(corpo["charge_id"]),
            tipo=str(corpo["tipo"]),
            raw=corpo,
        )

    # ---- Auxiliares de teste: simulam mudanças do lado do gateway ----

    def marcar_pago(self, external_id: str) -> None:
        self._transicionar(external_id, StatusCobranca.CONFIRMADO)

    def marcar_expirado(self, external_id: str) -> None:
        self._transicionar(external_id, StatusCobranca.EXPIRADO)

    def marcar_falhou(self, external_id: str) -> None:
        self._transicionar(external_id, StatusCobranca.FALHOU)

    def _transicionar(self, external_id: str, status: StatusCobranca) -> None:
        atual = self._cobrancas[external_id]
        self._cobrancas[external_id] = ChargeResult(
            external_id=atual.external_id,
            status=status,
            valor=atual.valor,
            qr_code=atual.qr_code,
            copia_e_cola=atual.copia_e_cola,
            expira_em=atual.expira_em,
        )
