from decimal import Decimal

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
    preco_unitario: Decimal
    subtotal: Decimal


class PedidoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    usuario_id: int
    status: StatusPedido
    total: Decimal
    itens: list[ItemPedidoRead]
