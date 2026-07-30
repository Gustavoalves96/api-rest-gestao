from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Pedido


class PedidoRepository:
    """Acesso a dados de pedidos."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def obter_por_id(self, pedido_id: int) -> Pedido | None:
        return await self.session.get(Pedido, pedido_id)

    async def obter_para_atualizacao(self, pedido_id: int) -> Pedido | None:
        """Lê o pedido com trava de linha (`SELECT ... FOR UPDATE`).

        Usado ao confirmar pagamento: impede que dois webhooks do mesmo pedido
        deem baixa de estoque em paralelo. No SQLite dos testes o lock é no-op,
        mas a query permanece correta.
        """
        resultado = await self.session.execute(
            select(Pedido).where(Pedido.id == pedido_id).with_for_update()
        )
        return resultado.scalar_one_or_none()

    async def listar_por_usuario(
        self, usuario_id: int, skip: int = 0, limit: int = 100
    ) -> Sequence[Pedido]:
        resultado = await self.session.execute(
            select(Pedido)
            .where(Pedido.usuario_id == usuario_id)
            .order_by(Pedido.id.desc())
            .offset(skip)
            .limit(limit)
        )
        return resultado.scalars().all()

    async def criar(self, pedido: Pedido) -> Pedido:
        self.session.add(pedido)
        await self.session.commit()
        await self.session.refresh(pedido)
        return pedido

    async def salvar(self, pedido: Pedido) -> Pedido:
        await self.session.commit()
        await self.session.refresh(pedido)
        return pedido
