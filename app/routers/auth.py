from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.dependencies import CurrentUser
from app.dependencies import get_usuario_service
from app.schemas.token import Token
from app.schemas.usuario import UsuarioCreate, UsuarioRead
from app.services.usuario import UsuarioService

router = APIRouter(prefix="/auth", tags=["auth"])

ServiceDep = Annotated[UsuarioService, Depends(get_usuario_service)]


@router.post("/register", response_model=UsuarioRead, status_code=status.HTTP_201_CREATED)
async def registrar(dados: UsuarioCreate, service: ServiceDep) -> UsuarioRead:
    usuario = await service.registrar(dados)
    return UsuarioRead.model_validate(usuario)


@router.post("/login", response_model=Token)
async def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: ServiceDep,
) -> Token:
    # O padrão OAuth2 usa o campo `username`; aqui ele carrega o e-mail.
    access_token = await service.autenticar(form.username, form.password)
    return Token(access_token=access_token)


@router.get("/me", response_model=UsuarioRead)
async def usuario_atual(usuario: CurrentUser) -> UsuarioRead:
    return UsuarioRead.model_validate(usuario)
