import logging
import logging.config
import json
import sys
from pathlib import Path
from typing import Dict, Any
import os
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """Formateador personalizado para logs en formato JSON"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Formatea el log record como JSON"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Agregar campos adicionales si existen
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
        if hasattr(record, 'endpoint'):
            log_entry['endpoint'] = record.endpoint
        if hasattr(record, 'response_time'):
            log_entry['response_time'] = record.response_time
        if hasattr(record, 'sql_query'):
            log_entry['sql_query'] = record.sql_query
        if hasattr(record, 'confidence_score'):
            log_entry['confidence_score'] = record.confidence_score
        
        # Agregar excepción si existe
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry, ensure_ascii=False)

class ColorFormatter(logging.Formatter):
    """Formateador con colores para consola"""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Verde
        'WARNING': '\033[33m',    # Amarillo
        'ERROR': '\033[31m',      # Rojo
        'CRITICAL': '\033[41m',   # Fondo rojo
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record: logging.LogRecord) -> str:
        """Formatea el log record con colores"""
        level_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        
        # Formato base con colores
        formatted_record = (
            f"{self.COLORS['RESET']}[{self.formatTime(record, self.datefmt)}] "
            f"{level_color}{record.levelname:8}{self.COLORS['RESET']} "
            f"| {record.name} | {record.getMessage()}"
        )
        
        # Agregar información adicional específica de la aplicación
        extra_info = []
        if hasattr(record, 'sql_query'):
            extra_info.append(f"SQL: {record.sql_query[:100]}...")
        if hasattr(record, 'confidence_score'):
            extra_info.append(f"Conf: {record.confidence_score}")
        if hasattr(record, 'response_time'):
            extra_info.append(f"Time: {record.response_time:.2f}s")
        
        if extra_info:
            formatted_record += f" | {' | '.join(extra_info)}"
        
        # Agregar excepción si existe
        if record.exc_info:
            formatted_record += f"\n{self.formatException(record.exc_info)}"
        
        return formatted_record

class RAGFilter(logging.Filter):
    """Filtro personalizado para logs RAG"""
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Filtra y enriquece records de log para RAG"""
        # Agregar contexto específico de RAG
        if not hasattr(record, 'component'):
            record.component = 'unknown'
        
        # Mantener todos los logs por defecto
        return True

def setup_logging(
    log_level: str = "INFO",
    enable_file_logging: bool = True,
    enable_json_logging: bool = False,
    log_dir: str = "data/logs"
) -> None:
    """
    Configura el sistema de logging para la aplicación RAG
    
    Args:
        log_level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        enable_file_logging: Habilitar logging a archivos
        enable_json_logging: Habilitar formato JSON para archivos
        log_dir: Directorio donde guardar los logs
    """
    
    # Crear directorio de logs si no existe
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    
    # Configuración base de logging
    config: Dict[str, Any] = {
        'version': 1,
        'disable_existing_loggers': False,
        'filters': {
            'rag_filter': {
                '()': RAGFilter
            }
        },
        'formatters': {
            'color': {
                '()': ColorFormatter,
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'json': {
                '()': JSONFormatter
            },
            'detailed': {
                'format': '[%(asctime)s] %(levelname)-8s | %(name)s | %(module)s:%(lineno)d - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'stream': sys.stdout,
                'level': log_level,
                'formatter': 'color',
                'filters': ['rag_filter']
            }
        },
        'loggers': {
            'app': {
                'level': log_level,
                'handlers': ['console'],
                'propagate': False
            },
            'rag_monitor': {
                'level': 'INFO',
                'handlers': ['console'],
                'propagate': False
            },
            'uvicorn': {
                'level': 'INFO',
                'handlers': ['console'],
                'propagate': False
            },
            'fastapi': {
                'level': 'INFO',
                'handlers': ['console'],
                'propagate': False
            }
        },
        'root': {
            'level': 'WARNING',
            'handlers': ['console']
        }
    }
    
    # Configurar handlers de archivo si está habilitado
    if enable_file_logging:
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        # Handler para todos los logs
        config['handlers']['file_all'] = {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': log_path / f'app_{current_date}.log',
            'maxBytes': 10 * 1024 * 1024,  # 10MB
            'backupCount': 5,
            'level': 'INFO',
            'formatter': 'json' if enable_json_logging else 'detailed',
            'filters': ['rag_filter']
        }
        
        # Handler específico para errores
        config['handlers']['file_errors'] = {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': log_path / f'errors_{current_date}.log',
            'maxBytes': 5 * 1024 * 1024,  # 5MB
            'backupCount': 5,
            'level': 'WARNING',
            'formatter': 'json' if enable_json_logging else 'detailed',
            'filters': ['rag_filter']
        }
        
        # Handler específico para RAG
        config['handlers']['file_rag'] = {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': log_path / f'rag_{current_date}.log',
            'maxBytes': 10 * 1024 * 1024,  # 10MB
            'backupCount': 5,
            'level': 'INFO',
            'formatter': 'json' if enable_json_logging else 'detailed',
            'filters': ['rag_filter']
        }
        
        # Agregar handlers a los loggers
        for logger_name in ['app', 'rag_monitor']:
            config['loggers'][logger_name]['handlers'].extend([
                'file_all', 'file_errors', 'file_rag'
            ])
    
    # Aplicar configuración
    logging.config.dictConfig(config)
    
    # Configurar logging asíncrono seguro
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    
    # Log inicial
    logger = logging.getLogger("app")
    logger.info(
        "Sistema de logging inicializado",
        extra={
            "log_level": log_level,
            "file_logging": enable_file_logging,
            "json_format": enable_json_logging,
            "log_directory": str(log_path.absolute())
        }
    )

def get_logger(name: str) -> logging.Logger:
    """
    Obtiene un logger con el nombre especificado
    
    Args:
        name: Nombre del logger
        
    Returns:
        Logger configurado
    """
    return logging.getLogger(name)

class RAGLogger:
    """Logger especializado para operaciones RAG"""
    
    def __init__(self, component: str):
        self.logger = get_logger(f"rag.{component}")
        self.component = component
    
    def log_query(
        self, 
        pregunta: str, 
        sql_query: str, 
        confidence_score: float,
        response_time: float,
        success: bool = True,
        user_id: str = None,
        request_id: str = None
    ) -> None:
        """Log especializado para consultas RAG"""
        extra = {
            'component': self.component,
            'sql_query': sql_query,
            'confidence_score': confidence_score,
            'response_time': response_time,
            'user_id': user_id,
            'request_id': request_id,
            'endpoint': '/rag/nl-to-sql'
        }
        
        if success:
            self.logger.info(
                f"Consulta RAG exitosa: {pregunta[:100]}...",
                extra=extra
            )
        else:
            self.logger.error(
                f"Consulta RAG fallida: {pregunta[:100]}...",
                extra=extra
            )
    
    def log_schema_operation(
        self, 
        operation: str, 
        table_count: int = None,
        success: bool = True
    ) -> None:
        """Log para operaciones de esquema"""
        extra = {
            'component': self.component,
            'operation': operation,
            'table_count': table_count
        }
        
        if success:
            self.logger.info(
                f"Operación de esquema completada: {operation}",
                extra=extra
            )
        else:
            self.logger.error(
                f"Operación de esquema fallida: {operation}",
                extra=extra
            )
    
    def log_vector_store_operation(
        self,
        operation: str,
        chunk_count: int = None,
        cache_hit: bool = None
    ) -> None:
        """Log para operaciones del vector store"""
        extra = {
            'component': self.component,
            'operation': operation,
            'chunk_count': chunk_count,
            'cache_hit': cache_hit
        }
        
        self.logger.info(
            f"Operación Vector Store: {operation}",
            extra=extra
        )

# Funciones de utilidad para logging rápido
def log_rag_success(pregunta: str, sql_query: str, confidence: float, time_taken: float):
    """Función rápida para loguear éxito RAG"""
    rag_logger = RAGLogger("api")
    rag_logger.log_query(pregunta, sql_query, confidence, time_taken, True)

def log_rag_error(pregunta: str, error: str, time_taken: float = 0.0):
    """Función rápida para loguear error RAG"""
    logger = get_logger("rag.api")
    logger.error(
        f"Error en consulta RAG: {pregunta[:100]}... - {error}",
        extra={
            'component': 'api',
            'response_time': time_taken,
            'endpoint': '/rag/nl-to-sql'
        }
    )

def log_schema_update(table_count: int):
    """Función rápida para loguear actualización de esquema"""
    rag_logger = RAGLogger("schema_processor")
    rag_logger.log_schema_operation("update", table_count, True)

# Configuración por entorno
def setup_logging_from_env():
    """Configura logging basado en variables de entorno"""
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    enable_file_logging = os.getenv('ENABLE_FILE_LOGGING', 'true').lower() == 'true'
    enable_json_logging = os.getenv('ENABLE_JSON_LOGGING', 'false').lower() == 'true'
    log_dir = os.getenv('LOG_DIR', 'data/logs')
    
    setup_logging(
        log_level=log_level,
        enable_file_logging=enable_file_logging,
        enable_json_logging=enable_json_logging,
        log_dir=log_dir
    )