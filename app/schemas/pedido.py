from pydantic import BaseModel, ConfigDict, Field

from app.models.pedido import StatusPedido


class ItemPedidoCreate(BaseModel):
    produto_id: int
    quantidade: int = Field(gt=0)


class PedidoCreate(BaseModel):
    itens: list[ItemPedidoCreate] = Field(min_length=1)


class ItemPedidoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    produto_id: int
    quantidade: int
    # Valores em centavos.
    preco_unitario: int
    subtotal: int


class PedidoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    usuario_id: int
    status: StatusPedido
    # Total em centavos.
    total: int
    itens: list[ItemPedidoRead]
