from collections.abc import Sequence

from app.exceptions import RecursoDuplicadoError, RecursoNaoEncontradoError
from app.models import Produto
from app.repositories.produto import ProdutoRepository
from app.schemas.produto import ProdutoCreate, ProdutoUpdate


class ProdutoService:
    def __init__(self, repository: ProdutoRepository) -> None:
        self.repository = repository

    async def obter(self, produto_id: int) -> Produto:
        produto = await self.repository.obter_por_id(produto_id)
        if produto is None:
            raise RecursoNaoEncontradoError("Produto não encontrado.")
        return produto

    async def listar(self, skip: int = 0, limit: int = 100) -> Sequence[Produto]:
        return await self.repository.listar(skip=skip, limit=limit)

    async def criar(self, dados: ProdutoCreate) -> Produto:
        if await self.repository.obter_por_sku(dados.sku):
            raise RecursoDuplicadoError("Já existe um produto com este SKU.")
        return await self.repository.criar(Produto(**dados.model_dump()))

    async def atualizar(self, produto_id: int, dados: ProdutoUpdate) -> Produto:
        produto = await self.obter(produto_id)
        for campo, valor in dados.model_dump(exclude_unset=True).items():
            setattr(produto, campo, valor)
        return await self.repository.salvar(produto)

    async def remover(self, produto_id: int) -> None:
        produto = await self.obter(produto_id)
        await self.repository.remover(produto)
