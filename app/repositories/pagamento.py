from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Pagamento


class PagamentoRepository:
    """Acesso a dados de pagamentos."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def obter_por_id(self, pagamento_id: int) -> Pagamento | None:
        return await self.session.get(Pagamento, pagamento_id)

    async def obter_por_pedido(self, pedido_id: int) -> Pagamento | None:
        resultado = await self.session.execute(
            select(Pagamento).where(Pagamento.pedido_id == pedido_id)
        )
        return resultado.scalar_one_or_none()

    async def obter_por_external_id(self, external_id: str) -> Pagamento | None:
        resultado = await self.session.execute(
            select(Pagamento).where(Pagamento.external_id == external_id)
        )
        return resultado.scalar_one_or_none()

    async def adicionar(self, pagamento: Pagamento) -> Pagamento:
        self.session.add(pagamento)
        await self.session.flush()
        return pagamento
