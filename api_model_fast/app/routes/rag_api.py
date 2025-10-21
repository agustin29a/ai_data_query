from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any
import pandas as pd
import time

from app.services.enhanced_bedrock_service import EnhancedBedrockService
from app.services.database_service import db_service
from app.services.chart_service import chart_service
from app.services.security_validator import SQLSecurityValidator, get_security_validator
from app.services.conversation_service import save_conversation
from app.utils.exceptions import (
    DatabaseError,
    BedrockError,
    RAGError,
    SecurityValidationError,
)
from app.utils.logging_config import log_rag_success, log_rag_error

# Crear el router de FastAPI
rag_router = APIRouter(prefix="/rag", tags=["RAG"])

# Instancia singleton del servicio para evitar múltiples inicializaciones
_rag_service = None


def get_rag_service() -> EnhancedBedrockService:
    """Obtiene la instancia singleton del servicio RAG"""
    global _rag_service
    if _rag_service is None:
        _rag_service = EnhancedBedrockService(db_service)
    return _rag_service


# Modelos Pydantic para validación de datos
class NLToSQLRequest(BaseModel):
    pregunta: str = Field(
        ..., min_length=1, max_length=500, description="Pregunta en lenguaje natural"
    )
    id: str | None = None


@rag_router.post("/nl-to-sql", response_model=Dict[str, Any])
async def rag_natural_language_to_sql(
    request: NLToSQLRequest,
    rag_service: EnhancedBedrockService = Depends(get_rag_service),
    security_validator: SQLSecurityValidator = Depends(get_security_validator),
):
    """
    Endpoint mejorado con RAG para NL-to-SQL con soporte completo de gráficos
    """
    start_time = time.time()
    pregunta = request.pregunta.strip()
    conversation_id = request.id

    try:
        # Usar servicio mejorado con RAG
        resultado = rag_service.nl_to_sql_with_rag(pregunta)

        # Validar seguridad de la consulta SQL
        if not security_validator.validate_sql_query(resultado["sql_query"]):
            raise SecurityValidationError("Consulta SQL no segura")

        # Sanitizar consulta SQL
        safe_sql_query = security_validator.sanitize_sql_query(resultado["sql_query"])

        # Ejecutar SQL
        resultados_db = db_service.execute_query(safe_sql_query)

        # Preparar datos para gráfico si es necesario
        chart_data = None
        if resultado.get("needs_chart") and resultados_db.get("data"):
            try:
                # Crear DataFrame con los resultados
                df = pd.DataFrame(
                    resultados_db["data"], columns=resultados_db.get("columns", [])
                )

                # Generar gráfico
                if not df.empty and resultado.get("chart_fields"):
                    chart_base64 = chart_service.generate_chart(
                        df,
                        resultado.get("chart_fields", {}),
                    )

                    chart_data = {
                        "needs_chart": True,
                        "chart_type": resultado.get("chart_type", "bar"),
                        "chart_image": f"data:image/png;base64,{chart_base64}",
                        "chart_code": resultado.get("chart_code", ""),
                        "chart_generated": True,
                    }
                else:
                    chart_data = {
                        "needs_chart": True,
                        "chart_type": resultado.get("chart_type", "bar"),
                        "chart_generated": False,
                        "reason": "No hay datos suficientes o código de gráfico faltante",
                    }
            except Exception as chart_error:
                chart_data = {
                    "needs_chart": True,
                    "chart_type": resultado.get("chart_type", "bar"),
                    "chart_generated": False,
                    "error": str(chart_error),
                }

        # Construir respuesta completa
        response_time = time.time() - start_time
        response = {
            "pregunta": pregunta,
            "sql_generado": safe_sql_query,
            "confidence_score": resultado.get("confidence_score", 0.0),
            "tables_used": resultado.get("tables_used", []),
            "title": resultado.get("title", ""),
            "resultados": resultados_db,
            "rag_enhanced": True,
            "visualization": {
                "needs_chart": resultado.get("needs_chart", False),
                "chart_type": resultado.get("chart_type", "none"),
                "detection_confidence": resultado.get("confidence_score", 0.0),
            },
            "status": "success",
            "response_time": round(response_time, 3),
        }

        # Agregar datos del gráfico si existe
        if chart_data:
            response["chart"] = chart_data
        else:
            response["chart"] = {"needs_chart": False, "chart_generated": False}

        # Log exitoso
        log_rag_success(
            pregunta=pregunta,
            sql_query=safe_sql_query,
            confidence=resultado.get("confidence_score", 0.0),
            time_taken=response_time,
        )

        response = await save_conversation(conversation_id, response)

        return response

    except BedrockError as e:
        response_time = time.time() - start_time
        log_rag_error(pregunta, f"BedrockError: {str(e)}", response_time)
        raise HTTPException(
            status_code=500,
            detail={
                "error": f"Error en el servicio de IA: {str(e)}",
                "status": "error",
                "error_type": "bedrock_error",
            },
        )
    except DatabaseError as e:
        response_time = time.time() - start_time
        log_rag_error(pregunta, f"DatabaseError: {str(e)}", response_time)
        raise HTTPException(
            status_code=500,
            detail={
                "error": f"Error en la base de datos: {str(e)}",
                "status": "error",
                "error_type": "database_error",
            },
        )
    except RAGError as e:
        response_time = time.time() - start_time
        log_rag_error(pregunta, f"RAGError: {str(e)}", response_time)
        raise HTTPException(
            status_code=500,
            detail={
                "error": f"Error en el sistema RAG: {str(e)}",
                "status": "error",
                "error_type": "rag_error",
            },
        )
    except Exception as e:
        response_time = time.time() - start_time
        log_rag_error(pregunta, f"Exception: {str(e)}", response_time)
        raise HTTPException(
            status_code=500,
            detail={
                "error": f"Error interno del servidor: {str(e)}",
                "status": "error",
                "error_type": "internal_error",
            },
        )

    except SecurityValidationError as e:
        response_time = time.time() - start_time
        log_rag_error(pregunta, f"SecurityValidationError: {str(e)}", response_time)
        raise HTTPException(
            status_code=400,
            detail={
                "error": f"Error de validación de seguridad: {str(e)}",
                "status": "error",
                "error_type": "security_validation_error",
                "dangerous_pattern": e.dangerous_pattern,
            },
        )


def get_security_validator() -> SQLSecurityValidator:
    """Dependencia para el validador de seguridad SQL"""
    return SQLSecurityValidator()
