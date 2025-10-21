
"""
Módulo centralizado de excepciones personalizadas para la aplicación
"""

class BaseAppException(Exception):
    """Clase base para todas las excepciones personalizadas"""
    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

# -------------------------------------------------------------------
# EXCEPCIONES EXISTENTES (que ya tenías)
# -------------------------------------------------------------------

class ChartError(BaseAppException):
    """Excepción para errores en generación de gráficos"""
    def __init__(self, message: str, chart_type: str = None, chart_code: str = None):
        details = {
            "error_type": "chart_generation",
            "chart_type": chart_type,
            "chart_code": chart_code
        }
        super().__init__(message, details)

class DatabaseError(BaseAppException):
    """Excepción para errores de base de datos"""
    def __init__(self, message: str, sql_query: str = None, db_operation: str = None):
        details = {
            "error_type": "database_operation",
            "sql_query": sql_query,
            "db_operation": db_operation
        }
        super().__init__(message, details)

class BedrockError(BaseAppException):
    """Excepción para errores del servicio AWS Bedrock"""
    def __init__(self, message: str, model_id: str = None, prompt: str = None):
        details = {
            "error_type": "bedrock_service",
            "model_id": model_id,
            "prompt_preview": prompt[:100] + "..." if prompt and len(prompt) > 100 else prompt
        }
        super().__init__(message, details)

# -------------------------------------------------------------------
# EXCEPCIONES RAG
# -------------------------------------------------------------------

class RAGError(BaseAppException):
    """Excepción base para errores en el pipeline RAG"""
    def __init__(self, message: str, component: str = None, operation: str = None):
        details = {
            "error_type": "rag_pipeline",
            "component": component,
            "operation": operation
        }
        super().__init__(message, details)

class SchemaExtractionError(RAGError):
    """Error al extraer el esquema de la base de datos"""
    def __init__(self, message: str, table_name: str = None, query_used: str = None):
        details = {
            "error_type": "schema_extraction",
            "table_name": table_name,
            "query_preview": query_used[:200] + "..." if query_used and len(query_used) > 200 else query_used
        }
        super().__init__(message, details)

class VectorStoreError(RAGError):
    """Error en operaciones del vector store"""
    def __init__(self, message: str, operation: str = None, chunk_count: int = None):
        details = {
            "error_type": "vector_store",
            "operation": operation,
            "chunk_count": chunk_count
        }
        super().__init__(message, details)

class EmbeddingError(RAGError):
    """Error en generación o búsqueda de embeddings"""
    def __init__(self, message: str, embedding_type: str = None, query: str = None):
        details = {
            "error_type": "embedding_operation",
            "embedding_type": embedding_type,
            "query_preview": query[:100] + "..." if query and len(query) > 100 else query
        }
        super().__init__(message, details)

class ContextRetrievalError(RAGError):
    """Error al recuperar contexto relevante"""
    def __init__(self, message: str, user_query: str = None, top_k: int = None):
        details = {
            "error_type": "context_retrieval",
            "user_query": user_query,
            "top_k_attempted": top_k
        }
        super().__init__(message, details)

# -------------------------------------------------------------------
# EXCEPCIONES DE VALIDACIÓN Y SEGURIDAD
# -------------------------------------------------------------------

class ValidationError(BaseAppException):
    """Excepción para errores de validación de datos"""
    def __init__(self, message: str, field: str = None, value: any = None, validation_rule: str = None):
        details = {
            "error_type": "validation",
            "field": field,
            "invalid_value": str(value),
            "validation_rule": validation_rule
        }
        super().__init__(message, details)

class SecurityError(BaseAppException):
    """Excepción para violaciones de seguridad"""
    def __init__(self, message: str, security_rule: str = None, attempted_action: str = None):
        details = {
            "error_type": "security",
            "security_rule": security_rule,
            "attempted_action": attempted_action
        }
        super().__init__(message, details)

class RateLimitError(BaseAppException):
    """Excepción para límites de tasa excedidos"""
    def __init__(self, message: str, limit: str = None, endpoint: str = None):
        details = {
            "error_type": "rate_limit",
            "limit": limit,
            "endpoint": endpoint
        }
        super().__init__(message, details)

# -------------------------------------------------------------------
# EXCEPCIONES DE DATOS Y PROCESAMIENTO
# -------------------------------------------------------------------

class DataProcessingError(BaseAppException):
    """Excepción para errores en procesamiento de datos"""
    def __init__(self, message: str, dataframe_shape: tuple = None, operation: str = None):
        details = {
            "error_type": "data_processing",
            "dataframe_shape": dataframe_shape,
            "operation": operation
        }
        super().__init__(message, details)

class ConfigurationError(BaseAppException):
    """Excepción para errores de configuración"""
    def __init__(self, message: str, config_key: str = None, config_file: str = None):
        details = {
            "error_type": "configuration",
            "config_key": config_key,
            "config_file": config_file
        }
        super().__init__(message, details)

# -------------------------------------------------------------------
# UTILIDADES PARA MANEJO DE EXCEPCIONES
# -------------------------------------------------------------------

def exception_to_dict(exception: BaseAppException) -> dict:
    """
    Convierte una excepción personalizada a diccionario para respuestas API
    """
    if isinstance(exception, BaseAppException):
        return {
            "error": exception.message,
            "error_type": exception.details.get("error_type", "unknown"),
            "details": exception.details,
            "status": "error"
        }
    else:
        return {
            "error": str(exception),
            "error_type": "unexpected_error",
            "details": {},
            "status": "error"
        }

def get_http_status_code(exception: Exception) -> int:
    """
    Determina el código HTTP apropiado para cada tipo de excepción
    """
    if isinstance(exception, (ValidationError, SecurityError)):
        return 400  # Bad Request
    elif isinstance(exception, RateLimitError):
        return 429  # Too Many Requests
    elif isinstance(exception, (DatabaseError, RAGError, EmbeddingError)):
        return 500  # Internal Server Error
    elif isinstance(exception, (ChartError, BedrockError, DataProcessingError)):
        return 422  # Unprocessable Entity
    elif isinstance(exception, ConfigurationError):
        return 503  # Service Unavailable
    else:
        return 500
    
class ModelLoadingError(RAGError):
    """Excepción para errores de carga de modelos"""
    def __init__(self, message: str, model_path: str = None):
        super().__init__(
            message=message,
            component="chart_detector",
            operation="model_loading"
        )
        self.model_path = model_path      # Internal Server Error

class SecurityValidationError(Exception):
    """
    Excepción para errores de validación de seguridad en consultas SQL
    """
    
    def __init__(
        self, 
        message: str = "Error de validación de seguridad",
        sql_query: str = None,
        dangerous_pattern: str = None,
        user_query: str = None,
        operation: str = "sql_validation"
    ):
        self.message = message
        self.sql_query = sql_query
        self.dangerous_pattern = dangerous_pattern
        self.user_query = user_query
        self.operation = operation
        self.error_type = "security_validation_error"
        
        # Construir mensaje detallado
        detail_message = f"{message}"
        if dangerous_pattern:
            detail_message += f" | Patrón peligroso: {dangerous_pattern}"
        if sql_query:
            # Limitar longitud del SQL en el mensaje
            safe_sql = sql_query[:100] + "..." if len(sql_query) > 100 else sql_query
            detail_message += f" | SQL: {safe_sql}"
        
        super().__init__(detail_message) 

class GeminiError(Exception):
    """Excepción personalizada para errores de Gemini API"""
    pass 

class CodeLlamaError(Exception):
    """Excepción personalizada para errores de CodeLlama"""
    pass

class ClaudeError(Exception):
    """Excepción personalizada para errores de Claude"""
    pass

class ChatServiceError(Exception):
    """Error general del Chat Service"""
    pass
