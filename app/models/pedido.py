import enum
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.item_pedido import ItemPedido


class StatusPedido(enum.StrEnum):
    PENDENTE = "pendente"
    PAGO = "pago"
    CANCELADO = "cancelado"


class Pedido(Base, TimestampMixin):
    __tablename__ = "pedidos"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    status: Mapped[StatusPedido] = mapped_column(
        Enum(StatusPedido, name="status_pedido"),
        default=StatusPedido.PENDENTE,
        nullable=False,
    )
    total: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"), nullable=False)

    itens: Mapped[list["ItemPedido"]] = relationship(
        back_populates="pedido",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
