"""Rotas de desenvolvimento — só existem quando o gateway é o `fake`.

Servem para simular localmente o que um gateway real faria (confirmar, expirar
ou falhar uma cobrança), já que o fake não dispara webhooks sozinho. Nunca são
registradas quando um gateway concreto está configurado.
"""

import uuid
from typing import Annotated, Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.auth.dependencies import CurrentUser
from app.dependencies import GatewayDep, get_payment_service
from app.exceptions import RegraDeNegocioError
from app.schemas.pagamento import PagamentoRead
from app.services.gateways.base import WebhookEvent
from app.services.gateways.fake import FakeGateway
from app.services.payment_service import PaymentService

router = APIRouter(prefix="/dev", tags=["dev"])

PaymentServiceDep = Annotated[PaymentService, Depends(get_payment_service)]


class SimulacaoInput(BaseModel):
    resultado: Literal["confirmar", "expirar", "falhar"] = "confirmar"


@router.post("/pagamentos/{pedido_id}/simular", response_model=PagamentoRead)
async def simular_pagamento(
    pedido_id: int,
    dados: SimulacaoInput,
    service: PaymentServiceDep,
    gateway: GatewayDep,
    usuario: CurrentUser,
) -> PagamentoRead:
    if not isinstance(gateway, FakeGateway):
        raise RegraDeNegocioError("Simulação disponível apenas com o gateway fake.")

    # Valida que a cobrança existe e pertence ao usuário.
    pagamento = await service.obter_cobranca(pedido_id, usuario.id)

    if dados.resultado == "confirmar":
        gateway.marcar_pago(pagamento.external_id)
    elif dados.resultado == "expirar":
        gateway.marcar_expirado(pagamento.external_id)
    else:
        gateway.marcar_falhou(pagamento.external_id)

    # Dispara o mesmo processamento de um webhook real (reconsulta o gateway,
    # aplica a transição de status e a baixa de estoque na confirmação).
    evento = WebhookEvent(
        external_event_id=f"dev-{uuid.uuid4()}",
        external_id=pagamento.external_id,
        tipo="DEV_SIMULACAO",
        raw={},
    )
    await service.processar_evento(evento)

    return PagamentoRead.model_validate(await service.obter_cobranca(pedido_id, usuario.id))
