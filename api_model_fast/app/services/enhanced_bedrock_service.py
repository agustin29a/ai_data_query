from typing import Dict, Any
import json
from app.services.rag.rag_pipeline import RAGPipeline
from app.services.database_service import db_service
from app.services.bedrock_service import BedrockService
from app.utils.exceptions import BedrockError
from app.utils.logging_config import get_logger

# Uso especializado para RAG
rag_logger = get_logger("enhanced_bedrock_service")


class EnhancedBedrockService(BedrockService):
    def __init__(self, db_service):
        super().__init__()
        self.rag_pipeline = RAGPipeline(db_service)
        self.query_history = []
        rag_logger.info("✅ EnhancedBedrockService inicializado con soporte RAG")

    def nl_to_sql_with_rag(self, pregunta: str) -> Dict[str, Any]:
        """Convierte NL a SQL usando RAG para mejor contexto"""
        try:
            rag_logger.debug(f"Recibiendo consulta en lenguaje natural: '{pregunta}'")

            # Mejorar prompt con contexto RAG (ahora incluye detección de gráficos)
            enhanced_prompt = self.rag_pipeline.enhance_prompt_with_rag(pregunta)
            rag_logger.debug("Prompt enriquecido con RAG generado correctamente")

            # Llamar a Bedrock
            response = self.client.invoke_model(
                modelId=self.config.PROFILE_ARN,
                body=json.dumps(
                    {
                        "anthropic_version": "bedrock-2023-05-31",
                        "max_tokens": 2500,  # Aumentado por el contexto adicional
                        "temperature": 0.1,
                        "messages": [{"role": "user", "content": enhanced_prompt}],
                    }
                ),
            )

            result = json.loads(response["body"].read())
            response_text = result["content"][0]["text"].strip()
            sql_response = json.loads(response_text)

            validated_response = self._validate_and_format_response(
                sql_response, pregunta
            )

            # Guardar en historial
            self.query_history.append(
                {
                    "pregunta": pregunta,
                    "sql_query": validated_response.get("sql_query"),
                    "confidence": validated_response.get("confidence_score"),
                    "tables_used": validated_response.get("tables_used", []),
                    "needs_chart": validated_response.get("needs_chart", False),
                    "chart_type": validated_response.get("chart_type", "none"),
                }
            )

            rag_logger.info(
                f"✅ Consulta procesada correctamente con RAG: '{pregunta}'"
            )

            return validated_response

        except json.JSONDecodeError as e:
            rag_logger.exception("❌ Error parseando respuesta JSON de Bedrock")
            raise BedrockError(f"Error parseando respuesta JSON de Bedrock: {str(e)}")
        except Exception as e:
            rag_logger.exception("❌ Error general en Bedrock con RAG")
            raise BedrockError(f"Error en Bedrock con RAG: {str(e)}")

    def _validate_and_format_response(
        self, sql_response: Dict, pregunta: str
    ) -> Dict[str, Any]:
        """Valida y formatea la respuesta para asegurar compatibilidad con el sistema existente"""
        if not sql_response.get("sql_query"):
            rag_logger.error("La respuesta de Bedrock no contiene consulta SQL")
            raise BedrockError("La respuesta de Bedrock no contiene consulta SQL")

        validated_response = {
            "sql_query": sql_response["sql_query"],
            "needs_chart": sql_response.get("needs_chart", False),
            "chart_type": sql_response.get("chart_type", "none"),
            "chart_fields": sql_response.get("chart_fields", ""),
            "confidence_score": sql_response.get("confidence_score", 0.0),
            "tables_used": sql_response.get("tables_used", []),
            "title": sql_response.get("title", ""),
        }

        return validated_response

    def nl_to_sql_and_viz(self, pregunta: str) -> Dict[str, Any]:
        """Método compatible con el servicio original BedrockService que ahora usa RAG internamente"""
        try:
            rag_logger.info(
                f"🧠 Procesando consulta con RAG + Visualización: '{pregunta}'"
            )
            rag_result = self.nl_to_sql_with_rag(pregunta)

            return {
                "needs_chart": rag_result.get("needs_chart", False),
                "chart_type": rag_result.get("chart_type", "none"),
                "sql_query": rag_result.get("sql_query", ""),
                "chart_fields": rag_result.get("chart_fields", ""),
            }

        except Exception as e:
            rag_logger.warning(
                f"⚠️ Fallo en RAG, aplicando fallback al método original: {str(e)}"
            )
            return super().nl_to_sql_and_viz(pregunta)

    def nl_to_sql(self, pregunta: str) -> str:
        """Método original que solo devuelve SQL (para compatibilidad) ahora mejorado con RAG"""
        try:
            rag_logger.debug(f"Procesando consulta solo SQL con RAG: '{pregunta}'")
            result = self.nl_to_sql_with_rag(pregunta)
            return result["sql_query"]
        except Exception as e:
            rag_logger.warning(f"⚠️ Fallo en RAG, fallback al método original: {str(e)}")
            return super().nl_to_sql(pregunta)

    def get_query_analytics(self) -> Dict[str, Any]:
        """Obtiene analytics de las consultas realizadas"""
        if not self.query_history:
            return {}

        total_queries = len(self.query_history)
        avg_confidence = (
            sum(q.get("confidence", 0) for q in self.query_history) / total_queries
        )

        table_usage = {}
        chart_usage = {}

        for query in self.query_history:
            for table in query.get("tables_used", []):
                table_usage[table] = table_usage.get(table, 0) + 1

            if query.get("needs_chart"):
                chart_type = query.get("chart_type", "unknown")
                chart_usage[chart_type] = chart_usage.get(chart_type, 0) + 1

        rag_logger.debug("Generando métricas de uso de consultas RAG")

        return {
            "total_queries": total_queries,
            "average_confidence": round(avg_confidence, 3),
            "most_used_tables": sorted(
                table_usage.items(), key=lambda x: x[1], reverse=True
            )[:5],
            "chart_usage": chart_usage,
            "charts_requested": sum(chart_usage.values()),
            "charts_percentage": round(
                (sum(chart_usage.values()) / total_queries) * 100, 1
            ),
        }

    def update_rag_schema(self):
        """Actualiza el esquema en el pipeline RAG"""
        try:
            rag_logger.info("🔄 Actualizando esquema RAG...")
            self.rag_pipeline.update_schema()
            rag_logger.info("✅ Esquema RAG actualizado correctamente")
            return {
                "status": "success",
                "message": "Esquema RAG actualizado correctamente",
            }
        except Exception as e:
            rag_logger.exception("❌ Error actualizando esquema RAG")
            raise BedrockError(f"Error actualizando esquema RAG: {str(e)}")


# Instancia global del servicio mejorado
enhanced_bedrock_service = EnhancedBedrockService(db_service)
