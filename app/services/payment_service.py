"""Orquestra cobrança, confirmação, estorno e o processamento de webhooks.

Regras críticas (ver "Pagamentos" no CLAUDE.md):
- O estoque só é abatido na CONFIRMAÇÃO do pagamento, na mesma transação.
- A máquina de estados é explícita; transição inválida é erro de domínio.
- O status real vem sempre do gateway (`get_charge`), nunca do corpo do webhook.
"""

from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import (
    EstoqueInsuficienteError,
    RecursoNaoEncontradoError,
    RegraDeNegocioError,
    TransicaoDeStatusInvalidaError,
)
from app.models import Pagamento, Pedido, StatusPagamento, StatusPedido
from app.repositories.pagamento import PagamentoRepository
from app.repositories.pedido import PedidoRepository
from app.repositories.produto import ProdutoRepository
from app.services.gateways.base import ChargeRequest, PaymentGateway, StatusCobranca, WebhookEvent

# Transições permitidas. CONFIRMADO nunca volta para PENDENTE; ESTORNADO é terminal.
_TRANSICOES: dict[StatusPagamento, set[StatusPagamento]] = {
    StatusPagamento.PENDENTE: {
        StatusPagamento.CONFIRMADO,
        StatusPagamento.FALHOU,
        StatusPagamento.EXPIRADO,
    },
    StatusPagamento.CONFIRMADO: {StatusPagamento.ESTORNADO},
    StatusPagamento.FALHOU: set(),
    StatusPagamento.EXPIRADO: set(),
    StatusPagamento.ESTORNADO: set(),
}

_MAP_STATUS: dict[StatusCobranca, StatusPagamento] = {
    StatusCobranca.PENDENTE: StatusPagamento.PENDENTE,
    StatusCobranca.CONFIRMADO: StatusPagamento.CONFIRMADO,
    StatusCobranca.FALHOU: StatusPagamento.FALHOU,
    StatusCobranca.EXPIRADO: StatusPagamento.EXPIRADO,
    StatusCobranca.ESTORNADO: StatusPagamento.ESTORNADO,
}


class PaymentService:
    def __init__(
        self,
        session: AsyncSession,
        pagamento_repository: PagamentoRepository,
        pedido_repository: PedidoRepository,
        produto_repository: ProdutoRepository,
        gateway: PaymentGateway,
    ) -> None:
        self.session = session
        self.pagamentos = pagamento_repository
        self.pedidos = pedido_repository
        self.produtos = produto_repository
        self.gateway = gateway

    async def criar_cobranca(self, pedido_id: int, usuario_id: int) -> Pagamento:
        pedido = await self.pedidos.obter_por_id(pedido_id)
        if pedido is None or pedido.usuario_id != usuario_id:
            raise RecursoNaoEncontradoError("Pedido não encontrado.")
        if pedido.status != StatusPedido.PENDENTE:
            raise RegraDeNegocioError("O pedido não está pendente de pagamento.")

        existente = await self.pagamentos.obter_por_pedido(pedido_id)
        if existente is not None:
            if existente.status == StatusPagamento.CONFIRMADO:
                raise RegraDeNegocioError("Pedido já pago.")
            # Reaproveita a cobrança vigente em vez de gerar outra.
            return existente

        cobranca = await self.gateway.create_charge(
            ChargeRequest(pedido_id=pedido_id, valor=pedido.total, descricao=f"Pedido #{pedido_id}")
        )
        pagamento = Pagamento(
            pedido_id=pedido_id,
            external_id=cobranca.external_id,
            status=StatusPagamento.PENDENTE,
            valor=cobranca.valor,
            metodo="pix",
            qr_code=cobranca.qr_code,
            copia_e_cola=cobranca.copia_e_cola,
            expira_em=cobranca.expira_em,
        )
        await self.pagamentos.adicionar(pagamento)
        await self.session.commit()
        await self.session.refresh(pagamento)
        return pagamento

    async def obter_cobranca(self, pedido_id: int, usuario_id: int) -> Pagamento:
        pedido = await self.pedidos.obter_por_id(pedido_id)
        if pedido is None or pedido.usuario_id != usuario_id:
            raise RecursoNaoEncontradoError("Cobrança não encontrada.")
        pagamento = await self.pagamentos.obter_por_pedido(pedido_id)
        if pagamento is None:
            raise RecursoNaoEncontradoError("Cobrança não encontrada.")
        return pagamento

    async def processar_evento(self, evento: WebhookEvent) -> None:
        """Aplica um evento de webhook já validado e registrado.

        Reconsulta o gateway para obter o status real — nunca confia no corpo
        do webhook para valores.
        """
        cobranca = await self.gateway.get_charge(evento.external_id)
        novo_status = _MAP_STATUS[cobranca.status]
        await self._aplicar_status(evento.external_id, novo_status, cobranca.valor)

    async def cancelar_pedido(self, pedido_id: int, usuario_id: int) -> Pedido:
        pedido = await self.pedidos.obter_para_atualizacao(pedido_id)
        if pedido is None or pedido.usuario_id != usuario_id:
            raise RecursoNaoEncontradoError("Pedido não encontrado.")
        if pedido.status == StatusPedido.CANCELADO:
            raise RegraDeNegocioError("Pedido já está cancelado.")

        pagamento = await self.pagamentos.obter_por_pedido(pedido_id)
        try:
            if pedido.status == StatusPedido.PAGO:
                # Estorno: devolve o dinheiro no gateway e o estoque, juntos.
                if pagamento is not None:
                    await self.gateway.refund(pagamento.external_id)
                    self._transicionar(pagamento, StatusPagamento.ESTORNADO)
                await self._devolver_estoque(pedido)
            elif pagamento is not None and pagamento.status == StatusPagamento.PENDENTE:
                # Pedido não pago: só expira a cobrança, sem mexer no estoque.
                self._transicionar(pagamento, StatusPagamento.EXPIRADO)

            pedido.status = StatusPedido.CANCELADO
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise

        await self.session.refresh(pedido)
        return pedido

    # ---- internos ----

    async def _aplicar_status(
        self, external_id: str, novo_status: StatusPagamento, valor_confirmado: int
    ) -> None:
        pagamento = await self.pagamentos.obter_por_external_id(external_id)
        if pagamento is None:
            return  # cobrança desconhecida: nada a processar
        if pagamento.status == novo_status:
            return  # idempotente: evento já refletido

        # Trava a linha do pedido: dois webhooks simultâneos não dão baixa dupla.
        pedido = await self.pedidos.obter_para_atualizacao(pagamento.pedido_id)
        if pedido is None:
            raise RecursoNaoEncontradoError("Pedido da cobrança não encontrado.")

        try:
            if novo_status == StatusPagamento.CONFIRMADO:
                await self._confirmar(pedido, pagamento, valor_confirmado)
            elif novo_status == StatusPagamento.ESTORNADO:
                self._transicionar(pagamento, StatusPagamento.ESTORNADO)
                await self._devolver_estoque(pedido)
                pedido.status = StatusPedido.CANCELADO
            elif novo_status == StatusPagamento.EXPIRADO:
                self._transicionar(pagamento, StatusPagamento.EXPIRADO)
                pedido.status = StatusPedido.CANCELADO
            elif novo_status == StatusPagamento.FALHOU:
                self._transicionar(pagamento, StatusPagamento.FALHOU)
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise

    async def _confirmar(self, pedido: Pedido, pagamento: Pagamento, valor_confirmado: int) -> None:
        self._transicionar(pagamento, StatusPagamento.CONFIRMADO)
        # Baixa de estoque na MESMA transação da confirmação.
        for item in pedido.itens:
            produto = await self.produtos.obter_por_id(item.produto_id)
            if produto is None or produto.quantidade_estoque < item.quantidade:
                disponivel = 0 if produto is None else produto.quantidade_estoque
                raise EstoqueInsuficienteError(
                    f"Estoque insuficiente para o produto {item.produto_id}: "
                    f"disponível {disponivel}, necessário {item.quantidade}."
                )
            produto.quantidade_estoque -= item.quantidade

        pagamento.valor = valor_confirmado
        pagamento.confirmado_em = datetime.now(UTC)
        pedido.status = StatusPedido.PAGO

    async def _devolver_estoque(self, pedido: Pedido) -> None:
        for item in pedido.itens:
            produto = await self.produtos.obter_por_id(item.produto_id)
            if produto is not None:
                produto.quantidade_estoque += item.quantidade

    def _transicionar(self, pagamento: Pagamento, novo_status: StatusPagamento) -> None:
        if novo_status not in _TRANSICOES[pagamento.status]:
            raise TransicaoDeStatusInvalidaError(
                f"Transição inválida: {pagamento.status} → {novo_status}."
            )
        pagamento.status = novo_status
