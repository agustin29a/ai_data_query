# Este archivo hace que el directorio routes sea un paquete Python
from .health import health_router
from .rag_api import rag_router

__all__ = ["health_router", "rag_router"]