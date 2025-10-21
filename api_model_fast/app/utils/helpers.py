import re
import json

def extract_json_from_response(response_text):
    # Buscar cualquier objeto JSON completo en el texto
    json_pattern = r'\{.*\}'
    match = re.search(json_pattern, response_text, re.DOTALL)
    
    if match:
        json_str = match.group()
        # Limpiar cualquier markdown residual
        json_str = json_str.replace("```json", "").replace("```", "").strip()
        return json.loads(json_str)
    else:
        raise ValueError("No se encontró JSON válido en la respuesta")