"""Primitivas de segurança: hashing de senha e emissão/validação de JWT."""

from datetime import UTC, datetime, timedelta

import bcrypt
import jwt

from app.config import get_settings

settings = get_settings()


def gerar_hash_senha(senha: str) -> str:
    """Gera o hash bcrypt de uma senha em texto puro."""
    return bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()


def verificar_senha(senha: str, senha_hash: str) -> bool:
    """Compara a senha em texto puro com o hash armazenado."""
    return bcrypt.checkpw(senha.encode(), senha_hash.encode())


def criar_access_token(subject: str) -> str:
    """Emite um JWT de acesso para o `subject` informado (ex.: id do usuário)."""
    expira_em = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": subject, "exp": expira_em}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decodificar_access_token(token: str) -> dict:
    """Decodifica e valida um JWT. Repassa exceções de `jwt` para o chamador."""
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
