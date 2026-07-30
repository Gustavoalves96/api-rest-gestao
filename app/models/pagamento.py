import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.pedido import Pedido


class StatusPagamento(enum.StrEnum):
    PENDENTE = "pendente"
    CONFIRMADO = "confirmado"
    FALHOU = "falhou"
    EXPIRADO = "expirado"
    ESTORNADO = "estornado"


class Pagamento(Base, TimestampMixin):
    __tablename__ = "pagamentos"

    id: Mapped[int] = mapped_column(primary_key=True)
    # 1:1 com o pedido: um pedido tem no máximo uma cobrança ativa.
    pedido_id: Mapped[int] = mapped_column(
        ForeignKey("pedidos.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    # ID da cobrança no gateway. Indexado e único (evita cobranças duplicadas).
    external_id: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    status: Mapped[StatusPagamento] = mapped_column(
        Enum(StatusPagamento, name="status_pagamento"),
        default=StatusPagamento.PENDENTE,
        nullable=False,
    )
    # Valor cobrado, em centavos.
    valor: Mapped[int] = mapped_column(Integer, nullable=False)
    metodo: Mapped[str] = mapped_column(String(20), default="pix", nullable=False)

    qr_code: Mapped[str | None] = mapped_column(String(4096), nullable=True)
    copia_e_cola: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    expira_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    confirmado_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    pedido: Mapped["Pedido"] = relationship()
