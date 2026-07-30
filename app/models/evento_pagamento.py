from datetime import datetime

from sqlalchemy import JSON, DateTime, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base

# Em produção (PostgreSQL) usamos JSONB; nos testes (SQLite), JSON comum.
JsonType = JSON().with_variant(JSONB(), "postgresql")


class EventoPagamento(Base):
    """Registro cru de cada webhook recebido do gateway.

    Gravado ANTES de qualquer processamento — é a única forma de depurar
    produção. A unicidade de `external_event_id` garante idempotência.
    """

    __tablename__ = "eventos_pagamento"

    id: Mapped[int] = mapped_column(primary_key=True)
    external_event_id: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    external_id: Mapped[str | None] = mapped_column(String(255), index=True, nullable=True)
    tipo: Mapped[str] = mapped_column(String(100), nullable=False)
    payload: Mapped[dict] = mapped_column(JsonType, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    processado_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
