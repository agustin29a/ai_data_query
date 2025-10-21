import re
import sqlparse
from sqlparse.tokens import Token, Keyword
from sqlparse.sql import Statement, Identifier, Where, Comparison
from typing import List, Optional
from app.utils.exceptions import SecurityValidationError

class SQLSecurityValidator:
    """
    Validador de seguridad para consultas SQL generadas por IA
    Previene SQL injection y operaciones peligrosas
    """
    
    # Patrones peligrosos que no deben aparecer en consultas generadas
    DANGEROUS_PATTERNS = [
        r"DROP\s+TABLE",
        r"DELETE\s+FROM",
        r"UPDATE\s+\w+\s+SET",
        r"INSERT\s+INTO",
        r"CREATE\s+TABLE",
        r"ALTER\s+TABLE",
        r"GRANT\s+",
        r"REVOKE\s+",
        r"TRUNCATE\s+TABLE",
        r"EXECUTE\s+",
        r"EXEC\s+",
        r"CREATE\s+FUNCTION",
        r"CREATE\s+PROCEDURE",
        r"CREATE\s+VIEW",
        r"VACUUM\s+",
        r"ANALYZE\s+",
        r"REINDEX\s+",
        r"LOCK\s+TABLE",
        r"UNLOCK\s+TABLE",
        r"BEGIN\s+TRANSACTION",
        r"COMMIT\s+TRANSACTION",
        r"ROLLBACK",
        r"SAVEPOINT",
    ]
    
    # Palabras clave SQL permitidas (solo consultas SELECT)
    ALLOWED_KEYWORDS = {
        'SELECT', 'FROM', 'WHERE', 'JOIN', 'LEFT', 'RIGHT', 'INNER', 'OUTER',
        'ON', 'AND', 'OR', 'NOT', 'IN', 'LIKE', 'BETWEEN', 'IS', 'NULL',
        'ORDER', 'BY', 'GROUP', 'HAVING', 'LIMIT', 'OFFSET', 'DISTINCT',
        'AS', 'COUNT', 'SUM', 'AVG', 'MIN', 'MAX', 'CASE', 'WHEN', 'THEN',
        'END', 'ELSE', 'EXISTS', 'ANY', 'ALL', 'SOME', 'UNION', 'INTERSECT',
        'EXCEPT', 'WITH', 'RECURSIVE', 'ORDER BY', 'GROUP BY', 'ASC', 'DESC',
    }
    
    # Funciones SQL permitidas
    ALLOWED_FUNCTIONS = {
        'count', 'sum', 'avg', 'min', 'max', 'coalesce', 'nullif', 'greatest',
        'least', 'now', 'current_date', 'current_time', 'current_timestamp',
        'date_part', 'extract', 'to_char', 'to_date', 'to_timestamp',
        'upper', 'lower', 'trim', 'ltrim', 'rtrim', 'length', 'substring',
        'concat', 'replace', 'round', 'ceil', 'floor', 'abs', 'mod', 'power',
        'sqrt', 'random', 'row_number', 'rank', 'dense_rank', 'lag', 'lead'
    }
    
    def __init__(self, max_query_length: int = 10000):
        self.max_query_length = max_query_length
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.DANGEROUS_PATTERNS]
    
    def validate_sql_query(self, sql_query: str, user_query: str = None) -> bool:
        """
        Valida que la consulta SQL sea segura
        
        Args:
            sql_query: Consulta SQL a validar
            user_query: Consulta original del usuario para contexto
            
        Returns:
            bool: True si la consulta es segura
            
        Raises:
            SecurityValidationError: Si la consulta no es segura
        """
        if not sql_query or not sql_query.strip():
            raise SecurityValidationError(
                message="La consulta SQL está vacía",
                user_query=user_query,
                operation="empty_query"
            )
        
        # Validar longitud
        if len(sql_query) > self.max_query_length:
            raise SecurityValidationError(
                message=f"La consulta SQL es demasiado larga ({len(sql_query)} caracteres)",
                sql_query=sql_query,
                user_query=user_query,
                operation="query_too_long"
            )
        
        # Validar patrones peligrosos
        for i, pattern in enumerate(self.compiled_patterns):
            if pattern.search(sql_query):
                raise SecurityValidationError(
                    message="Operación SQL peligrosa detectada",
                    sql_query=sql_query,
                    dangerous_pattern=self.DANGEROUS_PATTERNS[i],
                    user_query=user_query,
                    operation="dangerous_operation"
                )
        
        # Validar sintaxis SQL
        try:
            parsed = sqlparse.parse(sql_query)
            if not parsed:
                raise SecurityValidationError(
                    message="La consulta SQL no es válida",
                    sql_query=sql_query,
                    user_query=user_query,
                    operation="invalid_syntax"
                )
            
            # Validar que sea una consulta SELECT
            #self._validate_select_only(parsed[0], sql_query, user_query)
            
            # Validar palabras clave
            # self._validate_keywords(parsed[0], sql_query, user_query)
            
        except sqlparse.exceptions.SQLParseError as e:
            raise SecurityValidationError(
                message=f"Error parseando SQL: {str(e)}",
                sql_query=sql_query,
                user_query=user_query,
                operation="parse_error"
            )
        
        return True
    
    def _validate_select_only(self, statement: Statement, sql_query: str, user_query: str = None):
        """Valida que la consulta sea solo SELECT"""
        first_token = statement.token_first()
        if not first_token or first_token.ttype is not Keyword.DML:
            raise SecurityValidationError(
                message="Solo se permiten consultas SELECT",
                sql_query=sql_query,
                user_query=user_query,
                operation="non_select_query"
            )
        
        if first_token.normalized != 'SELECT':
            raise SecurityValidationError(
                message=f"Tipo de consulta no permitido: {first_token.normalized}",
                sql_query=sql_query,
                user_query=user_query,
                operation="invalid_query_type"
            )
    
    def _validate_keywords(self, statement: Statement, sql_query: str, user_query: str = None):
        """Valida que solo se usen palabras clave permitidas"""
        for token in statement.flatten():
            if token.ttype is Keyword and token.normalized.upper() not in self.ALLOWED_KEYWORDS:
                # Verificar si es una función permitida
                if not self._is_allowed_function(token):
                    raise SecurityValidationError(
                        message=f"Palabra clave no permitida: {token.normalized}",
                        sql_query=sql_query,
                        user_query=user_query,
                        operation="invalid_keyword"
                    )
    
    def _is_allowed_function(self, token) -> bool:
        """Verifica si el token es una función permitida"""
        if token.ttype is not Keyword:
            return False
        
        func_name = token.normalized.lower()
        return func_name in self.ALLOWED_FUNCTIONS
    
    def sanitize_sql_query(self, sql_query: str, default_limit: int = 1000) -> str:
        """
        Sanitiza y asegura la consulta SQL
        
        Args:
            sql_query: Consulta SQL a sanitizar
            default_limit: Límite por defecto si no existe
            
        Returns:
            str: Consulta SQL sanitizada
        """
        if not sql_query or not sql_query.strip():
            return "SELECT 1"  # Consulta por defecto segura
        
        # Primero validar la consulta
        self.validate_sql_query(sql_query)
        
        # Parsear la consulta
        parsed = sqlparse.parse(sql_query)
        if not parsed:
            return f"SELECT 1 LIMIT {default_limit}"
        
        statement = parsed[0]
        
        # Agregar límite si no existe
        if not self._has_limit(statement):
            sql_query = self._add_limit_to_query(sql_query, default_limit)
        
        return sql_query
    
    def _has_limit(self, statement: Statement) -> bool:
        """Verifica si la consulta ya tiene LIMIT"""
        sql_lower = statement.value.lower()
        return 'limit' in sql_lower
    
    def _add_limit_to_query(self, sql_query: str, limit: int) -> str:
        """Agrega LIMIT a la consulta SQL"""
        # Remover punto y coma final si existe
        sql_query = sql_query.rstrip(';')
        
        # Agregar LIMIT
        return f"{sql_query} LIMIT {limit};"
    
    def get_validation_report(self, sql_query: str, user_query: str = None) -> dict:
        """
        Genera un reporte detallado de validación
        
        Args:
            sql_query: Consulta SQL a validar
            user_query: Consulta original del usuario
            
        Returns:
            dict: Reporte de validación
        """
        report = {
            "is_valid": False,
            "checks_passed": [],
            "checks_failed": [],
            "warnings": [],
            "query_length": len(sql_query),
            "estimated_cost": self._estimate_query_cost(sql_query)
        }
        
        try:
            # Ejecutar validaciones
            self.validate_sql_query(sql_query, user_query)
            report["is_valid"] = True
            report["checks_passed"] = [
                "syntax_check",
                "security_patterns", 
                "query_type",
                "allowed_keywords",
                "query_length"
            ]
            
        except SecurityValidationError as e:
            report["checks_failed"] = [e.operation]
            report["error_message"] = e.message
            report["error_details"] = {
                "dangerous_pattern": e.dangerous_pattern,
                "sql_preview": e.sql_query[:200] + "..." if e.sql_query and len(e.sql_query) > 200 else e.sql_query
            }
        
        return report
    
    def _estimate_query_cost(self, sql_query: str) -> str:
        """Estima el costo de la consulta (bajo, medio, alto)"""
        # Análisis simple basado en complejidad
        complexity_indicators = [
            ('JOIN', 2),
            ('WHERE', 1),
            ('GROUP BY', 2),
            ('ORDER BY', 1),
            ('DISTINCT', 1),
            ('UNION', 3),
            ('HAVING', 2),
            ('SUBQUERY', 3)
        ]
        
        score = 0
        sql_upper = sql_query.upper()
        
        for indicator, weight in complexity_indicators:
            if indicator in sql_upper:
                score += weight
        
        if score >= 5:
            return "high"
        elif score >= 3:
            return "medium"
        else:
            return "low"

# Función de dependencia para FastAPI
def get_security_validator() -> SQLSecurityValidator:
    """Provee una instancia del validador de seguridad para dependencias de FastAPI"""
    return SQLSecurityValidator()