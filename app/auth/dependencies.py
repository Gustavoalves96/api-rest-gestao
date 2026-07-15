from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.security import decodificar_access_token
from app.database import get_session
from app.exceptions import CredenciaisInvalidasError
from app.models import Usuario
from app.repositories.usuario import UsuarioRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

SessionDep = Annotated[AsyncSession, Depends(get_session)]


async def get_current_user(
    session: SessionDep,
    token: Annotated[str, Depends(oauth2_scheme)],
) -> Usuario:
    """Valida o JWT do header e retorna o usuário autenticado."""
    try:
        payload = decodificar_access_token(token)
        subject = payload.get("sub")
        if subject is None:
            raise CredenciaisInvalidasError("Token inválido.")
        usuario_id = int(subject)
    except (jwt.PyJWTError, ValueError) as exc:
        raise CredenciaisInvalidasError("Token inválido ou expirado.") from exc

    usuario = await UsuarioRepository(session).obter_por_id(usuario_id)
    if usuario is None or not usuario.ativo:
        raise CredenciaisInvalidasError("Usuário não encontrado ou inativo.")

    return usuario


CurrentUser = Annotated[Usuario, Depends(get_current_user)]
