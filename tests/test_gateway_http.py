import httpx
import pytest
import respx

from app.exceptions import AssinaturaWebhookInvalidaError, GatewayError
from app.services.gateways.base import ChargeRequest, StatusCobranca
from app.services.gateways.http import HttpGateway

BASE = "http://gateway.test"


def gateway() -> HttpGateway:
    return HttpGateway(base_url=BASE, api_key="chave-secreta", webhook_token="tok-webhook")


@respx.mock
async def test_create_charge_traduz_resposta_e_envia_chave() -> None:
    rota = respx.post(f"{BASE}/charges").mock(
        return_value=httpx.Response(
            200,
            json={
                "id": "ch_1",
                "status": "PENDING",
                "amount": 10000,
                "pix": {
                    "qr_code": "qr",
                    "copia_e_cola": "000201",
                    "expires_at": "2026-01-01T00:00:00+00:00",
                },
            },
        )
    )
    resultado = await gateway().create_charge(
        ChargeRequest(pedido_id=1, valor=10000, descricao="Pedido #1")
    )

    assert resultado.external_id == "ch_1"
    assert resultado.status == StatusCobranca.PENDENTE
    assert resultado.valor == 10000
    assert resultado.copia_e_cola == "000201"
    assert resultado.expira_em is not None
    # A chave vai no header Authorization (e nunca é logada).
    assert rota.calls.last.request.headers["authorization"] == "Bearer chave-secreta"


@respx.mock
async def test_get_charge_mapeia_confirmado() -> None:
    respx.get(f"{BASE}/charges/ch_1").mock(
        return_value=httpx.Response(200, json={"id": "ch_1", "status": "CONFIRMED", "amount": 500})
    )
    resultado = await gateway().get_charge("ch_1")
    assert resultado.status == StatusCobranca.CONFIRMADO


@respx.mock
async def test_refund_mapeia_estornado() -> None:
    respx.post(f"{BASE}/charges/ch_1/refund").mock(
        return_value=httpx.Response(200, json={"id": "ch_1", "status": "REFUNDED"})
    )
    resultado = await gateway().refund("ch_1")
    assert resultado.status == StatusCobranca.ESTORNADO


@respx.mock
async def test_erro_http_vira_gateway_error() -> None:
    respx.get(f"{BASE}/charges/ch_x").mock(return_value=httpx.Response(500))
    with pytest.raises(GatewayError):
        await gateway().get_charge("ch_x")


@respx.mock
async def test_status_desconhecido_vira_gateway_error() -> None:
    respx.get(f"{BASE}/charges/ch_1").mock(
        return_value=httpx.Response(200, json={"id": "ch_1", "status": "SEI_LA", "amount": 1})
    )
    with pytest.raises(GatewayError):
        await gateway().get_charge("ch_1")


def test_parse_webhook_valida_assinatura() -> None:
    corpo = b'{"event_id":"e1","charge_id":"ch_1","tipo":"PAYMENT_CONFIRMED"}'
    evento = gateway().parse_webhook(corpo, {"x-webhook-token": "tok-webhook"})
    assert evento.external_id == "ch_1"
    assert evento.external_event_id == "e1"


def test_parse_webhook_assinatura_invalida() -> None:
    corpo = b'{"event_id":"e1","charge_id":"ch_1","tipo":"x"}'
    with pytest.raises(AssinaturaWebhookInvalidaError):
        gateway().parse_webhook(corpo, {"x-webhook-token": "errado"})
