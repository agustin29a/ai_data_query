"""
Pipeline RAG optimizado con selección basada en reglas.
"""

import logging
from app.services.rag.schema_selector import SchemaSelector
from app.services.chart_detector import ChartDetector

logger = logging.getLogger(__name__)


class RAGPipeline:
    """Pipeline RAG para text-to-SQL con detección de gráficos"""

    def __init__(self, db_service):
        self.db_service = db_service
        self.schema_selector = SchemaSelector(db_service)
        self.chart_detector = ChartDetector()
        logger.info("✅ RAG Pipeline inicializado correctamente")

    def retrieve_relevant_schema(self, natural_language_query: str) -> str:
        """Recupera el esquema relevante para la consulta"""
        try:
            return self.schema_selector.build_schema_context(natural_language_query)
        except Exception as e:
            logger.error(f"❌ Error recuperando esquema: {e}")
            raise

    def enhance_prompt_with_rag(self, natural_language_query: str) -> str:
        """Mejora el prompt con contexto RAG y detección de gráficos"""
        # Obtener contexto del esquema
        schema_context = self.retrieve_relevant_schema(natural_language_query)

        # Detectar requisitos de gráfico
        chart_requirements = self.chart_detector.predict(
            natural_language_query, schema_context
        )

        logger.info(
            "🔍 Generando prompt enriquecido con RAG para la consulta: '%s' (necesita gráfico: %s, tipo: %s)",
            natural_language_query,
            chart_requirements["needs_chart"],
            chart_requirements["chart_type"],
        )

        enhanced_prompt = f"""
# CONTEXTO DE BASE DE DATOS (ESQUEMA ESTRICTO)
{schema_context}

# REQUISITOS DE VISUALIZACIÓN
- Necesita gráfico: {chart_requirements['needs_chart']}
- Tipo de gráfico sugerido: {chart_requirements['chart_type']}
- Confianza: {chart_requirements['confidence']}
- Razón: {chart_requirements['reasoning']}

# INSTRUCCIONES GENERALES
Eres un experto en PostgreSQL y visualización de datos. Tu tarea es generar una consulta SQL **válida y ejecutable** en PostgreSQL, basada **exclusivamente** en el esquema proporcionado.

# REGLAS CRÍTICAS (OBLIGATORIAS)
1. **Usa SOLO** las tablas y columnas mencionadas en el esquema del contexto.  
   - Si el esquema no incluye una columna o tabla, **no la inventes** ni la derives.
   - Si no hay suficiente información para responder, **devuelve un error controlado** (ver más abajo).
2. Usa los nombres exactos de tablas y columnas tal como aparecen en el esquema.
3. Si la consulta requiere un JOIN, solo usa relaciones foreign key inferibles del esquema.
4. Optimiza para rendimiento, pero prioriza exactitud sobre optimización.
5. Considera los requisitos de visualización (tipo de gráfico, ejes, categorías, etc.)
6. No uses alias o funciones sobre columnas inexistentes.
7. No inventes métricas o agregaciones no justificadas.

# MANEJO DE ERRORES
Si la consulta no puede generarse sin violar las reglas anteriores, responde con el siguiente formato de error JSON:

{{
    "error": "No se puede generar la consulta sin inventar columnas o tablas fuera del esquema provisto.",
    "reason": "Explicación breve del motivo."
}}

# FORMATO DE RESPUESTA (CRÍTICO)
**Responde EXCLUSIVAMENTE con JSON válido (sin markdown, sin ```json, sin texto adicional):**

{{
    "sql_query": "Consulta SQL aquí",
    "needs_chart": {str(chart_requirements['needs_chart']).lower()},
    "chart_type": "bar|line|scatter|pie|histogram|area|box_plot|null",
    "chart_fields": {{
        "x_axis": "nombre_columna_x o null",
        "category_field": "nombre_columna_categoria o null",
        "color_field": "nombre_columna_color o null",
        "chart_code": "código Python completo usando matplotlib o seaborn para generar el gráfico, o null si no necesita gráfico"
    }},
    "confidence_score": 0.95,
    "tables_used": ["tabla1", "tabla2"],
    "title": "Titulo sugerido de la consulta"
}}

# ESPECIFICACIONES DE CAMPOS PARA GRÁFICOS
- bar chart: x_axis = categoría
- line chart: x_axis = temporal
- scatter plot: x_axis = numérico, necesita dos columnas numéricas
- pie chart: x_axis = categoría
- histogram: x_axis = numérico
- area chart: x_axis = temporal
- box_plot: x_axis = categoría (opcional)
- null: cuando no se necesita gráfico

# ESPECIFICACIONES PARA chart_code
Cuando needs_chart es true, debes generar código Python completo que:
1. Asume que existe un DataFrame llamado `df` con los datos de la consulta SQL
2. Usa matplotlib.pyplot (importado como plt) o seaborn (importado como sns)
3. Crea una figura con tamaño apropiado: plt.figure(figsize=(10, 6))
4. Configura títulos, etiquetas de ejes y leyendas apropiadas
5. Aplica estilo profesional (grid, colores, etc.)
6. NO incluye plt.show() al final (será manejado externamente)
7. Maneja valores nulos o vacíos apropiadamente

Ejemplo de chart_code para un bar chart:
"import matplotlib.pyplot as plt\\nimport seaborn as sns\\n\\nplt.figure(figsize=(10, 6))\\nsns.barplot(data=df, x='categoria', y='valor')\\nplt.title('Título del Gráfico')\\nplt.xlabel('Categoría')\\nplt.ylabel('Valor')\\nplt.xticks(rotation=45)\\nplt.tight_layout()"

Ejemplo de chart_code para un line chart:
"import matplotlib.pyplot as plt\\n\\nplt.figure(figsize=(12, 6))\\nplt.plot(df['fecha'], df['valor'], marker='o', linewidth=2)\\nplt.title('Título del Gráfico')\\nplt.xlabel('Fecha')\\nplt.ylabel('Valor')\\nplt.grid(True, alpha=0.3)\\nplt.xticks(rotation=45)\\nplt.tight_layout()"

# NOTAS DE IMPLEMENTACIÓN
- La consulta será ejecutada en PostgreSQL.
- El campo chart_code contendrá código Python listo para ejecutar sobre el DataFrame resultante.
- x_axis debe corresponder a una columna real del DataFrame (derivada directamente de columnas del esquema).
- El código del gráfico debe ser robusto y manejar casos edge (datos vacíos, valores nulos, etc.).

# CONSULTA DEL USUARIO
"{natural_language_query}"
"""

        return enhanced_prompt

    def update_schema(self):
        """Actualiza el esquema (reconstruye índices)"""
        try:
            logger.info("🔄 Actualizando índices de esquema...")
            self.schema_selector._build_indexes()
            logger.info("✅ Índices actualizados correctamente")
        except Exception as e:
            logger.error(f"❌ Error actualizando esquema: {e}")
            raise
