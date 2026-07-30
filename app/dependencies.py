"""Fábricas de injeção de dependências para repositories e services."""

from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from app.auth.dependencies import SessionDep
from app.config import get_settings
from app.repositories.evento_pagamento import EventoPagamentoRepository
from app.repositories.pagamento import PagamentoRepository
from app.repositories.pedido import PedidoRepository
from app.repositories.produto import ProdutoRepository
from app.repositories.usuario import UsuarioRepository
from app.services.gateways.base import PaymentGateway
from app.services.gateways.fake import FakeGateway
from app.services.payment_service import PaymentService
from app.services.pedido import PedidoService
from app.services.produto import ProdutoService
from app.services.usuario import UsuarioService
from app.services.webhook_service import WebhookService


def get_usuario_service(session: SessionDep) -> UsuarioService:
    return UsuarioService(UsuarioRepository(session))


def get_produto_service(session: SessionDep) -> ProdutoService:
    return ProdutoService(ProdutoRepository(session))


def get_pedido_service(session: SessionDep) -> PedidoService:
    return PedidoService(PedidoRepository(session), ProdutoRepository(session))


@lru_cache
def get_payment_gateway() -> PaymentGateway:
    """Resolve o gateway pela config. Instância única (o fake guarda estado).

    É injetado via `Depends` para que os testes possam substituí-lo por um fake
    próprio via `dependency_overrides`.
    """
    settings = get_settings()
    if settings.payment_gateway == "fake":
        return FakeGateway(
            webhook_secret=settings.webhook_secret,
            expira_minutos=settings.cobranca_expira_minutos,
        )
    raise RuntimeError(f"Gateway de pagamento não suportado: {settings.payment_gateway!r}")


GatewayDep = Annotated[PaymentGateway, Depends(get_payment_gateway)]


def _build_payment_service(session: SessionDep, gateway: PaymentGateway) -> PaymentService:
    return PaymentService(
        session=session,
        pagamento_repository=PagamentoRepository(session),
        pedido_repository=PedidoRepository(session),
        produto_repository=ProdutoRepository(session),
        gateway=gateway,
    )


def get_payment_service(session: SessionDep, gateway: GatewayDep) -> PaymentService:
    return _build_payment_service(session, gateway)


def get_webhook_service(session: SessionDep, gateway: GatewayDep) -> WebhookService:
    return WebhookService(
        session=session,
        evento_repository=EventoPagamentoRepository(session),
        payment_service=_build_payment_service(session, gateway),
        gateway=gateway,
    )
