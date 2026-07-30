from pydantic import BaseModel, ConfigDict, Field


class ProdutoCreate(BaseModel):
    sku: str = Field(min_length=1, max_length=64)
    nome: str = Field(min_length=1, max_length=255)
    descricao: str | None = Field(default=None, max_length=1000)
    # Preço em centavos (int). Ex.: R$ 199,90 -> 19990.
    preco: int = Field(gt=0)
    quantidade_estoque: int = Field(default=0, ge=0)


class ProdutoUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=1, max_length=255)
    descricao: str | None = Field(default=None, max_length=1000)
    preco: int | None = Field(default=None, gt=0)
    quantidade_estoque: int | None = Field(default=None, ge=0)
    ativo: bool | None = None


class ProdutoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sku: str
    nome: str
    descricao: str | None
    preco: int
    quantidade_estoque: int
    ativo: bool
