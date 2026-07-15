from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProdutoCreate(BaseModel):
    sku: str = Field(min_length=1, max_length=64)
    nome: str = Field(min_length=1, max_length=255)
    descricao: str | None = Field(default=None, max_length=1000)
    preco: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    quantidade_estoque: int = Field(default=0, ge=0)


class ProdutoUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=1, max_length=255)
    descricao: str | None = Field(default=None, max_length=1000)
    preco: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=2)
    quantidade_estoque: int | None = Field(default=None, ge=0)
    ativo: bool | None = None


class ProdutoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sku: str
    nome: str
    descricao: str | None
    preco: Decimal
    quantidade_estoque: int
    ativo: bool
