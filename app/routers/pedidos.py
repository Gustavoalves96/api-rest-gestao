from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.auth.dependencies import CurrentUser
from app.dependencies import get_pedido_service
from app.schemas.pedido import PedidoCreate, PedidoRead
from app.services.pedido import PedidoService

router = APIRouter(prefix="/pedidos", tags=["pedidos"])

ServiceDep = Annotated[PedidoService, Depends(get_pedido_service)]


@router.get("", response_model=list[PedidoRead])
async def listar_pedidos(
    service: ServiceDep,
    usuario: CurrentUser,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
) -> list[PedidoRead]:
    pedidos = await service.listar(usuario.id, skip=skip, limit=limit)
    return [PedidoRead.model_validate(p) for p in pedidos]


@router.get("/{pedido_id}", response_model=PedidoRead)
async def obter_pedido(
    pedido_id: int,
    service: ServiceDep,
    usuario: CurrentUser,
) -> PedidoRead:
    pedido = await service.obter(pedido_id, usuario.id)
    return PedidoRead.model_validate(pedido)


@router.post("", response_model=PedidoRead, status_code=status.HTTP_201_CREATED)
async def criar_pedido(
    dados: PedidoCreate,
    service: ServiceDep,
    usuario: CurrentUser,
) -> PedidoRead:
    pedido = await service.criar(usuario.id, dados)
    return PedidoRead.model_validate(pedido)


@router.post("/{pedido_id}/cancelar", response_model=PedidoRead)
async def cancelar_pedido(
    pedido_id: int,
    service: ServiceDep,
    usuario: CurrentUser,
) -> PedidoRead:
    pedido = await service.cancelar(pedido_id, usuario.id)
    return PedidoRead.model_validate(pedido)
