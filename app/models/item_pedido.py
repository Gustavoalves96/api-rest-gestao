from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.pedido import Pedido
    from app.models.produto import Produto


class ItemPedido(Base):
    __tablename__ = "itens_pedido"

    id: Mapped[int] = mapped_column(primary_key=True)
    pedido_id: Mapped[int] = mapped_column(
        ForeignKey("pedidos.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    produto_id: Mapped[int] = mapped_column(
        ForeignKey("produtos.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    quantidade: Mapped[int] = mapped_column(Integer, nullable=False)
    # Preço unitário em centavos, registrado no momento da compra (não muda
    # se o produto reajustar depois).
    preco_unitario: Mapped[int] = mapped_column(Integer, nullable=False)

    pedido: Mapped["Pedido"] = relationship(back_populates="itens")
    produto: Mapped["Produto"] = relationship()

    @property
    def subtotal(self) -> int:
        return self.preco_unitario * self.quantidade
