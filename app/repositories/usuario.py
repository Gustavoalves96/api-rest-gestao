from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Usuario


class UsuarioRepository:
    """Acesso a dados de usuários. Todas as queries de usuário ficam aqui."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def obter_por_id(self, usuario_id: int) -> Usuario | None:
        return await self.session.get(Usuario, usuario_id)

    async def obter_por_email(self, email: str) -> Usuario | None:
        resultado = await self.session.execute(select(Usuario).where(Usuario.email == email))
        return resultado.scalar_one_or_none()

    async def criar(self, usuario: Usuario) -> Usuario:
        self.session.add(usuario)
        await self.session.commit()
        await self.session.refresh(usuario)
        return usuario
