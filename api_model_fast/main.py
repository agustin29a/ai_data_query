from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.routes.rag_api import rag_router
from app.routes.health import health_router
from app.utils.logging_config import setup_logging_from_env
from app.middleware.rate_limiter import setup_rate_limiting

# Obtiene el logger raíz configurado por setup_logging_from_env()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Configura tareas de inicio y cierre del ciclo de vida de la app"""
    # --- STARTUP ---
    from app.routes.rag_api import get_rag_service

    get_rag_service()  # Inicializa el singleton
    logger.info("✅ RAG Service inicializado en startup")

    yield  # <--- Aquí se ejecuta la aplicación mientras está viva

    # --- SHUTDOWN ---
    logger.info("🛑 Apagando aplicación...")


def create_application() -> FastAPI:
    # Configurar logging desde variables de entorno
    setup_logging_from_env()

    app = FastAPI(
        title="NL-to-SQL RAG API",
        description="API para convertir lenguaje natural a SQL usando RAG",
        version="1.0.0",
        lifespan=lifespan,  # ✅ Usa el ciclo de vida
    )

    # Configurar CORS para desactivar la validación
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Permite todos los orígenes
        allow_credentials=True,
        allow_methods=["*"],  # Permite todos los métodos
        allow_headers=["*"],  # Permite todos los headers
    )

    # Configurar rate limiting
    setup_rate_limiting(app)

    # Incluir routers
    app.include_router(rag_router)
    app.include_router(health_router)

    return app


app = create_application()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
