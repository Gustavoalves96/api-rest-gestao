from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.exceptions import registrar_exception_handlers
from app.routers import auth, pedidos, produtos, webhooks

settings = get_settings()

app = FastAPI(
    title="API de Gestão de Estoque, Pedidos e Pagamentos",
    description="API REST para gestão de estoque, pedidos e pagamentos Pix.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

registrar_exception_handlers(app)

app.include_router(auth.router)
app.include_router(produtos.router)
app.include_router(pedidos.router)
app.include_router(webhooks.router)

# Rotas de simulação só existem no modo fake (nunca com um gateway real).
if settings.payment_gateway == "fake":
    from app.routers import dev

    app.include_router(dev.router)


@app.get("/health", tags=["infra"])
async def health() -> dict[str, str]:
    return {"status": "ok"}
