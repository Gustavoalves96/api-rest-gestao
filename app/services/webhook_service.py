"""Recebe webhooks do gateway com segurança e idempotência.

Ordem obrigatória (ver CLAUDE.md → Webhooks):
1. valida a assinatura (feito no gateway.parse_webhook) — 401 se inválida;
2. idempotência: evento repetido é no-op (constraint UNIQUE como 2ª defesa);
3. grava o payload cru ANTES de processar;
4. processa consultando o gateway para o status/valor reais.
"""

from collections.abc import Mapping
from datetime import UTC, datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import DomainError
from app.models import EventoPagamento
from app.repositories.evento_pagamento import EventoPagamentoRepository
from app.services.gateways.base import PaymentGateway
from app.services.payment_service import PaymentService


class WebhookService:
    def __init__(
        self,
        session: AsyncSession,
        evento_repository: EventoPagamentoRepository,
        payment_service: PaymentService,
        gateway: PaymentGateway,
    ) -> None:
        self.session = session
        self.eventos = evento_repository
        self.payments = payment_service
        self.gateway = gateway

    async def receber(self, raw_body: bytes, headers: Mapping[str, str]) -> None:
        # (1) Assinatura inválida levanta AssinaturaWebhookInvalidaError -> 401.
        evento = self.gateway.parse_webhook(raw_body, headers)

        # (2) Idempotência: evento já visto é no-op.
        if await self.eventos.existe(evento.external_event_id):
            return

        # (3) Persiste o payload cru antes de processar.
        try:
            await self.eventos.registrar(
                EventoPagamento(
                    external_event_id=evento.external_event_id,
                    external_id=evento.external_id,
                    tipo=evento.tipo,
                    payload=evento.raw,
                )
            )
            await self.session.commit()
        except IntegrityError:
            # Corrida entre dois eventos iguais: a constraint UNIQUE resolve.
            await self.session.rollback()
            return

        # (4) Processa. Erros de domínio (ex.: estoque insuficiente) revertem o
        # processamento, mas o evento permanece gravado para auditoria.
        try:
            await self.payments.processar_evento(evento)
        except DomainError:
            return

        await self._marcar_processado(evento.external_event_id)

    async def _marcar_processado(self, external_event_id: str) -> None:
        evento = await self.eventos.obter_por_external_event_id(external_event_id)
        if evento is not None:
            evento.processado_em = datetime.now(UTC)
            await self.session.commit()
