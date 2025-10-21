import psycopg2
from app.config.config import Config
from app.utils.exceptions import DatabaseError
from app.utils.logging_config import get_logger

logger = get_logger(__name__)


class DatabaseService:
    def __init__(self):
        self.config = Config()

    def get_connection(self):
        """Establece conexión con la base de datos"""
        try:
            conn = psycopg2.connect(
                host=self.config.DB_HOST,
                port=self.config.DB_PORT,
                dbname=self.config.DB_NAME,
                user=self.config.DB_USER,
                password=self.config.DB_PASS,
            )
            return conn
        except Exception as e:
            raise DatabaseError(f"Error al conectar con la base de datos: {str(e)}")

    def execute_query(self, query):
        """Ejecuta una consulta SQL y retorna los resultados"""
        try:
            logger.info(f"Ejecutando consulta SQL: {query}")
            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute(query)

            # Intentar obtener resultados (para SELECT)
            try:
                resultados = cur.fetchall()
                column_names = [desc[0] for desc in cur.description]
                resultados_formateados = {"columns": column_names, "data": resultados}
            except psycopg2.ProgrammingError:
                # Para INSERT, UPDATE, DELETE que no retornan datos
                resultados_formateados = {
                    "rows_affected": cur.rowcount,
                    "message": "Operación ejecutada correctamente",
                }

            conn.commit()
            cur.close()
            conn.close()
            return resultados_formateados

        except Exception as e:
            raise DatabaseError(f"Error ejecutando consulta: {str(e)}")


# Instancia global del servicio
db_service = DatabaseService()
