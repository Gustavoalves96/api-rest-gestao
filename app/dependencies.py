"""Fábricas de injeção de dependências para repositories e services."""

from app.auth.dependencies import SessionDep
from app.repositories.pedido import PedidoRepository
from app.repositories.produto import ProdutoRepository
from app.repositories.usuario import UsuarioRepository
from app.services.pedido import PedidoService
from app.services.produto import ProdutoService
from app.services.usuario import UsuarioService


def get_usuario_service(session: SessionDep) -> UsuarioService:
    return UsuarioService(UsuarioRepository(session))


def get_produto_service(session: SessionDep) -> ProdutoService:
    return ProdutoService(ProdutoRepository(session))


def get_pedido_service(session: SessionDep) -> PedidoService:
    return PedidoService(PedidoRepository(session), ProdutoRepository(session))
