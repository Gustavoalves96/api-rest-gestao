from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import EventoPagamento


class EventoPagamentoRepository:
    """Registro dos webhooks recebidos (idempotência via external_event_id)."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def existe(self, external_event_id: str) -> bool:
        resultado = await self.session.execute(
            select(EventoPagamento.id).where(EventoPagamento.external_event_id == external_event_id)
        )
        return resultado.first() is not None

    async def obter_por_external_event_id(self, external_event_id: str) -> EventoPagamento | None:
        resultado = await self.session.execute(
            select(EventoPagamento).where(EventoPagamento.external_event_id == external_event_id)
        )
        return resultado.scalar_one_or_none()

    async def registrar(self, evento: EventoPagamento) -> EventoPagamento:
        self.session.add(evento)
        await self.session.flush()
        return evento
