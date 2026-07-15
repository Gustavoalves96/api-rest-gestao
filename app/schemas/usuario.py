from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UsuarioCreate(BaseModel):
    email: EmailStr
    nome: str = Field(min_length=1, max_length=255)
    senha: str = Field(min_length=8, max_length=128)


class UsuarioRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    nome: str
    ativo: bool
