"""Abstração do gateway de pagamento.

Tipos e interface são **nossos** — o JSON do gateway concreto é traduzido para
estes tipos dentro de cada implementação. Nenhum módulo fora deste pacote
conhece um gateway específico.
"""

import enum
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol, runtime_checkable


class StatusCobranca(enum.StrEnum):
    """Status neutro de uma cobrança, independente do gateway."""

    PENDENTE = "pendente"
    CONFIRMADO = "confirmado"
    FALHOU = "falhou"
    EXPIRADO = "expirado"
    ESTORNADO = "estornado"


@dataclass(frozen=True)
class ChargeRequest:
    pedido_id: int
    valor: int  # centavos
    descricao: str


@dataclass(frozen=True)
class ChargeResult:
    external_id: str
    status: StatusCobranca
    valor: int  # centavos
    qr_code: str | None = None
    copia_e_cola: str | None = None
    expira_em: datetime | None = None


@dataclass(frozen=True)
class RefundResult:
    external_id: str
    status: StatusCobranca


@dataclass(frozen=True)
class WebhookEvent:
    external_event_id: str
    external_id: str
    tipo: str
    raw: dict


@runtime_checkable
class PaymentGateway(Protocol):
    async def create_charge(self, req: ChargeRequest) -> ChargeResult: ...

    async def get_charge(self, external_id: str) -> ChargeResult: ...

    async def refund(self, external_id: str) -> RefundResult: ...

    def parse_webhook(self, raw_body: bytes, headers: Mapping[str, str]) -> WebhookEvent:
        """Valida a assinatura e traduz o corpo cru em um WebhookEvent.

        Deve levantar `AssinaturaWebhookInvalidaError` se a assinatura for
        inválida, antes de qualquer parsing de negócio.
        """
        ...
