from functools import lru_cache
from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    """Configuração da aplicação, carregada de variáveis de ambiente / .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/gestao"

    jwt_secret: str = "troque-por-um-segredo-forte-e-aleatorio"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # Origens permitidas para o frontend (CORS). Aceita lista separada por vírgula
    # no ambiente (ex.: CORS_ORIGINS=https://app.vercel.app,https://outro.com).
    cors_origins: Annotated[list[str], NoDecode] = ["http://localhost:3000"]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_cors(cls, valor: object) -> object:
        if isinstance(valor, str):
            return [origem.strip() for origem in valor.split(",") if origem.strip()]
        return valor

    # Gateway de pagamento: "fake" (em memória) ou "http" (REST genérico via httpx).
    # A app nunca conhece o gateway concreto diretamente, só a interface PaymentGateway.
    payment_gateway: str = "fake"
    # URL base do gateway HTTP genérico (usada quando payment_gateway == "http").
    gateway_base_url: str = "http://localhost:9000"
    # Chave de API do gateway — apenas via ambiente, nunca versionada nem logada.
    gateway_api_key: str = ""
    # Segredo compartilhado usado para validar a assinatura dos webhooks.
    webhook_secret: str = "troque-por-um-segredo-de-webhook"
    # Minutos de validade de uma cobrança Pix.
    cobranca_expira_minutos: int = 30


@lru_cache
def get_settings() -> Settings:
    """Retorna as settings em cache (uma única leitura por processo)."""
    return Settings()
