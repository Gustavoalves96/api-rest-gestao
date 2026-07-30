from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.pagamento import StatusPagamento


class PagamentoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    pedido_id: int
    # Referência da cobrança no gateway (útil para suporte/conciliação).
    external_id: str
    status: StatusPagamento
    # Valor em centavos.
    valor: int
    metodo: str
    qr_code: str | None
    copia_e_cola: str | None
    expira_em: datetime | None
    confirmado_em: datetime | None
