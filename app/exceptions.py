"""Exceções de domínio e seus handlers HTTP.

As camadas de service/repository levantam essas exceções; nunca `HTTPException`.
A conversão para resposta HTTP acontece nos handlers registrados em `main.py`.
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse


class DomainError(Exception):
    """Base para erros de regra de negócio."""

    status_code: int = status.HTTP_400_BAD_REQUEST

    def __init__(self, mensagem: str) -> None:
        super().__init__(mensagem)
        self.mensagem = mensagem


class RecursoNaoEncontradoError(DomainError):
    """Recurso solicitado não existe."""

    status_code = status.HTTP_404_NOT_FOUND


class RecursoDuplicadoError(DomainError):
    """Violação de unicidade (ex.: e-mail ou SKU já cadastrado)."""

    status_code = status.HTTP_409_CONFLICT


class EstoqueInsuficienteError(DomainError):
    """Quantidade solicitada excede o estoque disponível."""

    status_code = status.HTTP_409_CONFLICT


class RegraDeNegocioError(DomainError):
    """Operação inválida dado o estado atual do recurso."""

    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT


class CredenciaisInvalidasError(DomainError):
    """Falha de autenticação (credenciais ou token inválidos)."""

    status_code = status.HTTP_401_UNAUTHORIZED


def registrar_exception_handlers(app: FastAPI) -> None:
    """Registra o handler que traduz `DomainError` em resposta JSON."""

    @app.exception_handler(DomainError)
    async def _handle_domain_error(_: Request, exc: DomainError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.mensagem},
        )
