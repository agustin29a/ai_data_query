from fastapi import APIRouter
from pydantic import BaseModel

# Crear el router de FastAPI
health_router = APIRouter(tags=["Health"])

# Modelo de respuesta para documentación automática
class HealthResponse(BaseModel):
    status: str
    message: str

@health_router.get("/health", response_model=HealthResponse)
async def health_check():
    """Endpoint para verificar que la API está funcionando"""
    return {
        "status": "OK", 
        "message": "API funcionando correctamente"
    }