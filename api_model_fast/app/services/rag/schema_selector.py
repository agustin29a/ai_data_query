"""
Sistema basado en reglas para selección eficiente de esquema.
Reemplaza embeddings por búsqueda por keywords + relaciones.
"""

import re
import logging
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class TableMetadata:
    """Metadata de una tabla para búsqueda rápida"""

    name: str
    keywords: Set[str]
    columns: List[str]
    relationships: Dict[str, str]  # {columna: tabla_referenciada}
    description: str


class SchemaSelector:
    """
    Selección de esquema basada en reglas + keywords.
    Mucho más rápido y predecible que embeddings semánticos.
    """

    def __init__(self, db_service):
        self.db_service = db_service
        self.tables_metadata: Dict[str, TableMetadata] = {}
        self.keyword_index: Dict[str, Set[str]] = {}
        self._build_indexes()

    def _extract_schema_from_db(self) -> Dict:
        """Extrae el esquema completo de la base de datos"""
        try:
            # Obtener todas las tablas
            tables_query = """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """
            tables_result = self.db_service.execute_query(tables_query)
            tables = [row[0] for row in tables_result["data"]]

            schema_info = {}

            for table in tables:
                # Obtener columnas y tipos
                columns_query = f"""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns
                    WHERE table_name = '{table}'
                    ORDER BY ordinal_position
                """
                columns_result = self.db_service.execute_query(columns_query)

                # Obtener relaciones (FKs)
                relations_query = f"""
                    SELECT
                        kcu.column_name,
                        ccu.table_name AS foreign_table_name,
                        ccu.column_name AS foreign_column_name
                    FROM information_schema.table_constraints AS tc
                    JOIN information_schema.key_column_usage AS kcu
                        ON tc.constraint_name = kcu.constraint_name
                    JOIN information_schema.constraint_column_usage AS ccu
                        ON ccu.constraint_name = tc.constraint_name
                    WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_name = '{table}'
                """
                relations_result = self.db_service.execute_query(relations_query)

                schema_info[table] = {
                    "columns": [
                        {"name": col[0], "type": col[1], "nullable": col[2] == "YES"}
                        for col in columns_result["data"]
                    ],
                    "relationships": [
                        {
                            "column": rel[0],
                            "references_table": rel[1],
                            "references_column": rel[2],
                        }
                        for rel in relations_result.get("data", [])
                    ],
                }

            # Obtener comentarios
            comments_query = """
                SELECT 
                    tbl.table_name,
                    col.column_name,
                    pg_catalog.col_description(cl.oid, col.ordinal_position::int) as column_comment,
                    pg_catalog.obj_description(cl.oid, 'pg_class') as table_comment
                FROM information_schema.tables tbl
                JOIN information_schema.columns col 
                    ON tbl.table_name = col.table_name 
                    AND tbl.table_schema = col.table_schema
                JOIN pg_catalog.pg_class cl ON cl.relname = tbl.table_name
                JOIN pg_catalog.pg_namespace n ON n.oid = cl.relnamespace
                WHERE tbl.table_schema = 'public'
                AND tbl.table_type = 'BASE TABLE'
                AND n.nspname = 'public'
                ORDER BY tbl.table_name, col.ordinal_position
            """
            comments_result = self.db_service.execute_query(comments_query)

            # Integrar comentarios
            comments = {}
            for row in comments_result["data"]:
                table_name, column_name, col_comment, table_comment = row
                if table_name not in comments:
                    comments[table_name] = {
                        "table_comment": table_comment,
                        "columns": {},
                    }
                if col_comment:
                    comments[table_name]["columns"][column_name] = col_comment

            for table in schema_info:
                if table in comments:
                    schema_info[table]["table_comment"] = comments[table][
                        "table_comment"
                    ]
                    for col in schema_info[table]["columns"]:
                        if col["name"] in comments[table]["columns"]:
                            col["comment"] = comments[table]["columns"][col["name"]]

            return schema_info

        except Exception as e:
            logger.error(f"Error extrayendo esquema: {e}")
            raise

    def _build_indexes(self):
        """Construye índices de búsqueda rápida"""
        schema = self._extract_schema_from_db()

        for table_name, table_info in schema.items():
            keywords = self._extract_keywords(table_name, table_info)

            metadata = TableMetadata(
                name=table_name,
                keywords=keywords,
                columns=[col["name"] for col in table_info["columns"]],
                relationships=self._extract_relationships(table_info),
                description=table_info.get("table_comment", ""),
            )

            self.tables_metadata[table_name] = metadata

            # Indexar keywords -> tablas
            for keyword in keywords:
                if keyword not in self.keyword_index:
                    self.keyword_index[keyword] = set()
                self.keyword_index[keyword].add(table_name)

        logger.info(
            f"✅ Índices construidos: {len(self.tables_metadata)} tablas, "
            f"{len(self.keyword_index)} keywords"
        )

    def _extract_keywords(self, table_name: str, table_info: Dict) -> Set[str]:
        """Extrae keywords relevantes de una tabla"""
        keywords = set()

        # Nombre de tabla (singular/plural)
        keywords.add(table_name.lower())
        keywords.add(table_name.rstrip("s").lower())
        keywords.update(table_name.lower().split("_"))

        # Keywords de descripción
        if table_info.get("table_comment"):
            desc_words = re.findall(r"\b\w{4,}\b", table_info["table_comment"].lower())
            keywords.update(desc_words[:10])

        # Nombres de columnas importantes
        skip_columns = {"id", "created_at", "updated_at", "activo"}
        for col in table_info.get("columns", []):
            col_name = col["name"].lower()
            if col_name not in skip_columns:
                keywords.add(col_name)
                keywords.update(col_name.split("_"))

        # Keywords de comentarios de columnas
        for col in table_info.get("columns", []):
            if col.get("comment"):
                comment_words = re.findall(r"\b\w{4,}\b", col["comment"].lower())
                keywords.update(comment_words[:5])

        return keywords

    def _extract_relationships(self, table_info: Dict) -> Dict[str, str]:
        """Extrae foreign keys de una tabla"""
        relationships = {}
        for rel in table_info.get("relationships", []):
            relationships[rel["column"]] = rel["references_table"]
        return relationships

    def _tokenize_query(self, query: str) -> List[str]:
        """Tokeniza la query en palabras relevantes"""
        query = query.lower()
        tokens = re.findall(r"\b\w{3,}\b", query)

        # Remover stopwords
        stopwords = {
            "los",
            "las",
            "del",
            "para",
            "con",
            "por",
            "que",
            "una",
            "este",
            "esta",
            "estos",
            "estas",
            "ese",
            "esa",
            "esos",
            "esas",
        }
        tokens = [t for t in tokens if t not in stopwords]

        return tokens

    def _score_table(self, table_name: str, query_tokens: List[str]) -> float:
        """Calcula score de relevancia para una tabla"""
        if table_name not in self.tables_metadata:
            return 0.0

        metadata = self.tables_metadata[table_name]
        score = 0.0

        for token in query_tokens:
            # Match exacto con nombre de tabla
            if token in table_name.lower():
                score += 10.0

            # Match con keywords
            if token in metadata.keywords:
                score += 5.0

            # Match con columnas
            if token in [col.lower() for col in metadata.columns]:
                score += 3.0

            # Match en descripción
            if metadata.description and token in metadata.description.lower():
                score += 1.0

        return score

    def select_relevant_tables(
        self, query: str, max_tables: int = 5
    ) -> List[Tuple[str, float]]:
        """Selecciona tablas relevantes para la query"""
        query_tokens = self._tokenize_query(query)

        # Búsqueda por keywords
        candidate_tables = set()
        for token in query_tokens:
            if token in self.keyword_index:
                candidate_tables.update(self.keyword_index[token])

        # Si no hay candidatos, usar todas
        if not candidate_tables:
            candidate_tables = set(self.tables_metadata.keys())

        # Calcular scores
        table_scores = []
        for table_name in candidate_tables:
            score = self._score_table(table_name, query_tokens)
            if score > 0:
                table_scores.append((table_name, score))

        table_scores.sort(key=lambda x: x[1], reverse=True)

        # Expandir con tablas relacionadas
        final_tables = set()
        for table_name, score in table_scores[:max_tables]:
            final_tables.add(table_name)

            metadata = self.tables_metadata[table_name]
            for related_table in metadata.relationships.values():
                if len(final_tables) < max_tables * 2:
                    final_tables.add(related_table)

        # Recalcular scores
        final_scores = []
        for table_name in final_tables:
            score = self._score_table(table_name, query_tokens)
            final_scores.append((table_name, score))

        final_scores.sort(key=lambda x: x[1], reverse=True)

        logger.debug(
            f"🎯 Tablas seleccionadas: {[t for t, _ in final_scores[:max_tables]]}"
        )

        return final_scores[:max_tables]

    def build_schema_context(self, query: str) -> str:
        """Construye contexto de esquema para el LLM"""
        relevant_tables = self.select_relevant_tables(query, max_tables=5)

        if not relevant_tables:
            return "No se encontraron tablas relevantes."

        full_schema = self._extract_schema_from_db()

        context = "ESQUEMA DE BASE DE DATOS RELEVANTE (TODOS LOS CAMPOS):\n\n"

        for table_name, score in relevant_tables:
            if table_name in full_schema:
                context += self._format_table(table_name, full_schema[table_name])
                context += "\n\n"

        return context

    def _format_table(self, table_name: str, table_info: Dict) -> str:
        """Formatea una tabla completa"""
        result = f"--- Tabla: {table_name} ---\n"

        if table_info.get("table_comment"):
            result += f"Descripción: {table_info['table_comment']}\n"

        result += "Columnas:\n"
        for col in table_info["columns"]:
            result += f"  - {col['name']} ({col['type']})"
            if not col["nullable"]:
                result += " NOT NULL"
            if col.get("comment"):
                result += f"\n    Comentario: {col['comment']}"
            result += "\n"

        if table_info.get("relationships"):
            result += "Relaciones:\n"
            for rel in table_info["relationships"]:
                result += f"  - {rel['column']} → {rel['references_table']}.{rel['references_column']}\n"

        return result
