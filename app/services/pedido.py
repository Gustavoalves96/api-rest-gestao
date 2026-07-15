from collections.abc import Sequence
from decimal import Decimal

from app.exceptions import (
    EstoqueInsuficienteError,
    RecursoNaoEncontradoError,
    RegraDeNegocioError,
)
from app.models import ItemPedido, Pedido, StatusPedido
from app.repositories.pedido import PedidoRepository
from app.repositories.produto import ProdutoRepository
from app.schemas.pedido import PedidoCreate


class PedidoService:
    def __init__(
        self,
        pedido_repository: PedidoRepository,
        produto_repository: ProdutoRepository,
    ) -> None:
        # Os dois repositórios compartilham a mesma sessão, então a criação do
        # pedido e a baixa de estoque acontecem na mesma transação (atômica).
        self.pedidos = pedido_repository
        self.produtos = produto_repository

    async def criar(self, usuario_id: int, dados: PedidoCreate) -> Pedido:
        pedido = Pedido(usuario_id=usuario_id, status=StatusPedido.PENDENTE)
        total = Decimal("0.00")

        for item in dados.itens:
            produto = await self.produtos.obter_por_id(item.produto_id)
            if produto is None or not produto.ativo:
                raise RecursoNaoEncontradoError(
                    f"Produto {item.produto_id} não encontrado ou inativo."
                )
            if produto.quantidade_estoque < item.quantidade:
                raise EstoqueInsuficienteError(
                    f"Estoque insuficiente para o produto {produto.sku}: "
                    f"disponível {produto.quantidade_estoque}, solicitado {item.quantidade}."
                )

            produto.quantidade_estoque -= item.quantidade
            pedido.itens.append(
                ItemPedido(
                    produto_id=produto.id,
                    quantidade=item.quantidade,
                    preco_unitario=produto.preco,
                )
            )
            total += produto.preco * item.quantidade

        pedido.total = total
        return await self.pedidos.criar(pedido)

    async def obter(self, pedido_id: int, usuario_id: int) -> Pedido:
        pedido = await self.pedidos.obter_por_id(pedido_id)
        if pedido is None or pedido.usuario_id != usuario_id:
            raise RecursoNaoEncontradoError("Pedido não encontrado.")
        return pedido

    async def listar(self, usuario_id: int, skip: int = 0, limit: int = 100) -> Sequence[Pedido]:
        return await self.pedidos.listar_por_usuario(usuario_id, skip=skip, limit=limit)

    async def cancelar(self, pedido_id: int, usuario_id: int) -> Pedido:
        pedido = await self.obter(pedido_id, usuario_id)
        if pedido.status == StatusPedido.CANCELADO:
            raise RegraDeNegocioError("Pedido já está cancelado.")

        # Devolve ao estoque tudo o que havia sido baixado.
        for item in pedido.itens:
            produto = await self.produtos.obter_por_id(item.produto_id)
            if produto is not None:
                produto.quantidade_estoque += item.quantidade

        pedido.status = StatusPedido.CANCELADO
        return await self.pedidos.salvar(pedido)
