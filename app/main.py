from fastapi import FastAPI

from app.exceptions import registrar_exception_handlers
from app.routers import auth, pedidos, produtos

app = FastAPI(
    title="API de Gestão de Estoque e Pedidos",
    description="API REST para gestão de estoque e pedidos (domínio ERP).",
    version="0.1.0",
)

registrar_exception_handlers(app)

app.include_router(auth.router)
app.include_router(produtos.router)
app.include_router(pedidos.router)


@app.get("/health", tags=["infra"])
async def health() -> dict[str, str]:
    return {"status": "ok"}
