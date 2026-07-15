from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Produto


class ProdutoRepository:
    """Acesso a dados de produtos."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def obter_por_id(self, produto_id: int) -> Produto | None:
        return await self.session.get(Produto, produto_id)

    async def obter_por_sku(self, sku: str) -> Produto | None:
        resultado = await self.session.execute(select(Produto).where(Produto.sku == sku))
        return resultado.scalar_one_or_none()

    async def listar(self, skip: int = 0, limit: int = 100) -> Sequence[Produto]:
        resultado = await self.session.execute(
            select(Produto).order_by(Produto.id).offset(skip).limit(limit)
        )
        return resultado.scalars().all()

    async def criar(self, produto: Produto) -> Produto:
        self.session.add(produto)
        await self.session.commit()
        await self.session.refresh(produto)
        return produto

    async def salvar(self, produto: Produto) -> Produto:
        """Persiste alterações em um produto já rastreado pela sessão."""
        await self.session.commit()
        await self.session.refresh(produto)
        return produto

    async def remover(self, produto: Produto) -> None:
        await self.session.delete(produto)
        await self.session.commit()
