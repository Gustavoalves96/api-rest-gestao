"""Rotas chamadas PELO gateway de pagamento (não pelo cliente).

A URL é pública e conhecida por qualquer um na internet; a proteção vem da
validação de assinatura feita dentro do WebhookService.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, status

from app.dependencies import get_webhook_service
from app.services.webhook_service import WebhookService

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

WebhookServiceDep = Annotated[WebhookService, Depends(get_webhook_service)]


@router.post("/pagamentos", status_code=status.HTTP_200_OK)
async def receber_pagamento(request: Request, service: WebhookServiceDep) -> Response:
    # Precisamos do corpo cru (bytes) para validar assinatura e registrar o payload.
    raw_body = await request.body()
    await service.receber(raw_body, request.headers)
    # Responde 200 rápido: o gateway tem timeout curto e reenvia em caso de erro.
    return Response(status_code=status.HTTP_200_OK)
