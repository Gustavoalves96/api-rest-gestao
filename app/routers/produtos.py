from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.auth.dependencies import CurrentUser
from app.dependencies import get_produto_service
from app.schemas.produto import ProdutoCreate, ProdutoRead, ProdutoUpdate
from app.services.produto import ProdutoService

router = APIRouter(prefix="/produtos", tags=["produtos"])

ServiceDep = Annotated[ProdutoService, Depends(get_produto_service)]


@router.get("", response_model=list[ProdutoRead])
async def listar_produtos(
    service: ServiceDep,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
) -> list[ProdutoRead]:
    produtos = await service.listar(skip=skip, limit=limit)
    return [ProdutoRead.model_validate(p) for p in produtos]


@router.get("/{produto_id}", response_model=ProdutoRead)
async def obter_produto(produto_id: int, service: ServiceDep) -> ProdutoRead:
    produto = await service.obter(produto_id)
    return ProdutoRead.model_validate(produto)


@router.post("", response_model=ProdutoRead, status_code=status.HTTP_201_CREATED)
async def criar_produto(
    dados: ProdutoCreate,
    service: ServiceDep,
    _usuario: CurrentUser,
) -> ProdutoRead:
    produto = await service.criar(dados)
    return ProdutoRead.model_validate(produto)


@router.patch("/{produto_id}", response_model=ProdutoRead)
async def atualizar_produto(
    produto_id: int,
    dados: ProdutoUpdate,
    service: ServiceDep,
    _usuario: CurrentUser,
) -> ProdutoRead:
    produto = await service.atualizar(produto_id, dados)
    return ProdutoRead.model_validate(produto)


@router.delete("/{produto_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remover_produto(
    produto_id: int,
    service: ServiceDep,
    _usuario: CurrentUser,
) -> None:
    await service.remover(produto_id)
