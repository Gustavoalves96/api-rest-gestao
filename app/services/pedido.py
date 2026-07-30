from collections.abc import Sequence

from app.exceptions import EstoqueInsuficienteError, RecursoNaoEncontradoError
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
        self.pedidos = pedido_repository
        self.produtos = produto_repository

    async def criar(self, usuario_id: int, dados: PedidoCreate) -> Pedido:
        # A criação NÃO abate o estoque — a baixa autoritativa acontece só na
        # confirmação do pagamento (ver payment_service). Mas fazemos uma
        # verificação de disponibilidade aqui para não aceitar pedidos que já
        # nascem impossíveis. Não é reserva: dois pedidos podem passar por esta
        # checagem, e a concorrência é resolvida na confirmação.
        pedido = Pedido(usuario_id=usuario_id, status=StatusPedido.PENDENTE)
        total = 0

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
