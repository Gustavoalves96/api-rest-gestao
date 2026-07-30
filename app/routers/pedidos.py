from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.auth.dependencies import CurrentUser
from app.dependencies import get_payment_service, get_pedido_service
from app.schemas.pagamento import PagamentoRead
from app.schemas.pedido import PedidoCreate, PedidoRead
from app.services.payment_service import PaymentService
from app.services.pedido import PedidoService

router = APIRouter(prefix="/pedidos", tags=["pedidos"])

PedidoServiceDep = Annotated[PedidoService, Depends(get_pedido_service)]
PaymentServiceDep = Annotated[PaymentService, Depends(get_payment_service)]


@router.get("", response_model=list[PedidoRead])
async def listar_pedidos(
    service: PedidoServiceDep,
    usuario: CurrentUser,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
) -> list[PedidoRead]:
    pedidos = await service.listar(usuario.id, skip=skip, limit=limit)
    return [PedidoRead.model_validate(p) for p in pedidos]


@router.get("/{pedido_id}", response_model=PedidoRead)
async def obter_pedido(
    pedido_id: int,
    service: PedidoServiceDep,
    usuario: CurrentUser,
) -> PedidoRead:
    pedido = await service.obter(pedido_id, usuario.id)
    return PedidoRead.model_validate(pedido)


@router.post("", response_model=PedidoRead, status_code=status.HTTP_201_CREATED)
async def criar_pedido(
    dados: PedidoCreate,
    service: PedidoServiceDep,
    usuario: CurrentUser,
) -> PedidoRead:
    pedido = await service.criar(usuario.id, dados)
    return PedidoRead.model_validate(pedido)


@router.post(
    "/{pedido_id}/pagamento",
    response_model=PagamentoRead,
    status_code=status.HTTP_201_CREATED,
)
async def criar_cobranca(
    pedido_id: int,
    service: PaymentServiceDep,
    usuario: CurrentUser,
) -> PagamentoRead:
    pagamento = await service.criar_cobranca(pedido_id, usuario.id)
    return PagamentoRead.model_validate(pagamento)


@router.get("/{pedido_id}/pagamento", response_model=PagamentoRead)
async def obter_cobranca(
    pedido_id: int,
    service: PaymentServiceDep,
    usuario: CurrentUser,
) -> PagamentoRead:
    pagamento = await service.obter_cobranca(pedido_id, usuario.id)
    return PagamentoRead.model_validate(pagamento)


@router.post("/{pedido_id}/cancelar", response_model=PedidoRead)
async def cancelar_pedido(
    pedido_id: int,
    service: PaymentServiceDep,
    usuario: CurrentUser,
) -> PedidoRead:
    pedido = await service.cancelar_pedido(pedido_id, usuario.id)
    return PedidoRead.model_validate(pedido)
