from datetime import date, datetime
from decimal import Decimal
import httpx
from typing import Dict, Any, Optional
from app.config.config import Config


async def save_conversation(
    conversation_id: Optional[str], response_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Guarda una conversación en el servicio de conversaciones.

    Args:
        conversation_id: ID de la conversación existente (None para nueva)
        response_data: Diccionario con los datos de respuesta

    Returns:
        Dict con los datos de respuesta actualizados
    """
    CONVERSATIONS_URL = Config.CONVERSATIONS_URL

    def serialize_data(obj):
        """
        Función recursiva para serializar objetos no serializables por defecto.
        """
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, (list, tuple)):
            return [serialize_data(item) for item in obj]
        elif isinstance(obj, dict):
            return {key: serialize_data(value) for key, value in obj.items()}
        elif hasattr(obj, "__dict__"):
            return serialize_data(obj.__dict__)
        else:
            return obj

    # Serializar los resultados antes de construir la conversación
    resultados_serializados = serialize_data(response_data["resultados"])

    conversation = {
        "title": response_data.get("title", ""),
        "messages": [
            {
                "isUser": True,
                "content": response_data["pregunta"],
            },
            {
                "isUser": False,
                "content": {
                    "query_sql": response_data["sql_generado"],
                    "query_result": resultados_serializados,
                    "chart_base64": response_data.get("chart", {}).get(
                        "chart_image", None
                    ),
                },
            },
        ],
    }

    async with httpx.AsyncClient() as client:
        try:
            if conversation_id:
                # Verificar si la conversación existe
                response = await client.get(f"{CONVERSATIONS_URL}/{conversation_id}")

                if response.status_code == 200:
                    # Conversación existe, actualizamos
                    conversation = {
                        "_id": conversation_id,
                        "messages": conversation["messages"],
                    }

                    update_response = await client.post(
                        f"{CONVERSATIONS_URL}/multiple-messages", json=conversation
                    )
                    update_response.raise_for_status()
                else:
                    # Si no existe o hay error, creamos nueva
                    response.raise_for_status()

            # Si no hay conversation_id o la validación falló, creamos nueva
            if not conversation_id or response.status_code != 200:
                r = await client.post(CONVERSATIONS_URL, json=conversation)
                r.raise_for_status()
                conversation_id = r.json()["_id"]
                response_data["_id"] = conversation_id

        except httpx.HTTPStatusError as e:
            # Manejar errores HTTP
            print(f"Error HTTP: {e}")
            raise
        except Exception as e:
            # Manejar otros errores
            print(f"Error inesperado: {e}")
            raise

    # 4️⃣ Devolver resultado con el _id (para el frontend)
    return response_data
