from app.auth.security import criar_access_token, gerar_hash_senha, verificar_senha
from app.exceptions import CredenciaisInvalidasError, RecursoDuplicadoError
from app.models import Usuario
from app.repositories.usuario import UsuarioRepository
from app.schemas.usuario import UsuarioCreate


class UsuarioService:
    def __init__(self, repository: UsuarioRepository) -> None:
        self.repository = repository

    async def registrar(self, dados: UsuarioCreate) -> Usuario:
        if await self.repository.obter_por_email(dados.email):
            raise RecursoDuplicadoError("E-mail já cadastrado.")

        usuario = Usuario(
            email=dados.email,
            nome=dados.nome,
            senha_hash=gerar_hash_senha(dados.senha),
        )
        return await self.repository.criar(usuario)

    async def autenticar(self, email: str, senha: str) -> str:
        usuario = await self.repository.obter_por_email(email)
        if usuario is None or not verificar_senha(senha, usuario.senha_hash):
            raise CredenciaisInvalidasError("E-mail ou senha inválidos.")
        if not usuario.ativo:
            raise CredenciaisInvalidasError("Usuário inativo.")

        return criar_access_token(subject=str(usuario.id))
