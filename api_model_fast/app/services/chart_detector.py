import torch
from transformers import DistilBertForSequenceClassification, DistilBertTokenizer
import os
import re
from app.utils.exceptions import ModelLoadingError
from app.utils.logging_config import get_logger

# Usa get_logger en lugar de RAGLogger para el logger estándar
logger = get_logger("chart_detector")

class ChartDetector:
    def __init__(self, model_path=None):
        if model_path is None:
            self.model_path = os.path.join(
                os.path.dirname(__file__), 
                '..', 
                'models', 
                'modelo_distilbert_mejorado'
            )
        else:
            self.model_path = model_path
            
        self.model = None
        self.tokenizer = None
        self.device = None
        self.label_mapping = None
        self._load_model()
    
    def _load_model(self):
        """Carga el modelo y tokenizer entrenados con fine-tuning"""
        try:
            # Verificar que los archivos existan
            required_files = [
                'config.json', 
                'tokenizer_config.json',
                'vocab.txt', 
                'special_tokens_map.json'
            ]
            
            for file in required_files:
                file_path = os.path.join(self.model_path, file)
                if not os.path.exists(file_path):
                    raise ModelLoadingError(
                        message=f"Archivo del modelo no encontrado: {file}",
                        model_path=self.model_path
                    )
            
            logger.info(f"Cargando modelo fine-tuned desde: {self.model_path}")
            
            # Cargar modelo y tokenizer
            self.model = DistilBertForSequenceClassification.from_pretrained(self.model_path)
            self.tokenizer = DistilBertTokenizer.from_pretrained(self.model_path)
            self.model.eval()
            
            # Determinar dispositivo (GPU/CPU)
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            self.model.to(self.device)
            
            # Definir el mapeo de etiquetas (según tu fine-tuning)
            self.label_mapping = {
                'ninguno': 0,
                'barras': 1,
                'histograma': 2,
                'lineal': 3,
                'circular': 4,
                'dispersion': 5
            }
            
            logger.info(f"Modelo fine-tuned cargado exitosamente en: {self.device}")
            
        except Exception as e:
            raise ModelLoadingError(
                message=f"Error cargando el modelo de detección de gráficos: {str(e)}",
                model_path=self.model_path
            )
    
    def preprocess_text(self, text: str) -> str:
        """Preprocesa el texto de entrada (igual que en tu fine-tuning)"""
        if isinstance(text, str):
            text = text.lower()
            text = re.sub(r'[^\w\s]', '', text)
            return text.strip()
        return ""
    
    def predict(self, text: str, schema_context: str = "") -> dict:
        """Predice si el texto requiere gráfico y el tipo usando el modelo fine-tuned"""
        try:
            resultado = self._predict_with_model(text)
            return {
                "needs_chart": resultado['necesita_grafico'],
                "chart_type": resultado['tipo_grafico'],
                "confidence": resultado['confianza'],
                "reasoning": self._generate_reasoning(
                    text, 
                    resultado['necesita_grafico'], 
                    resultado['tipo_grafico'], 
                    resultado['confianza']
                )
            }
        except Exception as e:
            logger.warning(f"Error en predicción con modelo, usando fallback: {str(e)}")
            return self._fallback_detection(text)
    
    def _predict_with_model(self, text: str) -> dict:
        """Predicción basada en modelo fine-tuned"""
        self.model.eval()
        texto_limpio = self.preprocess_text(text)

        encoding = self.tokenizer(
            texto_limpio,
            truncation=True,
            padding='max_length',
            max_length=128,
            return_tensors='pt'
        )

        input_ids = encoding['input_ids'].to(self.device)
        attention_mask = encoding['attention_mask'].to(self.device)

        with torch.no_grad():
            outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
            predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
            predicted_class = torch.argmax(predictions, dim=1).item()
            confidence = predictions[0][predicted_class].item()

        reverse_mapping = {v: k for k, v in self.label_mapping.items()}
        tipo_grafico = reverse_mapping[predicted_class]
        necesita_grafico = tipo_grafico != 'ninguno'

        if confidence < 0.7 and tipo_grafico == 'ninguno':
            palabras_sin_grafico = ['lista', 'listar', 'mostrar', 'obtener', 'consulta', 'dame', 'muestra', 'detalle', 'datos', 'información']
            palabras_con_grafico = ['grafico', 'gráfico', 'chart', 'plot', 'grafica', 'gráfica', 'visualiza', 'histograma', 'barras', 'circular', 'pastel', 'lineal', 'dispersión']
            texto_lower = text.lower()

            conteo_sin_grafico = sum(1 for palabra in palabras_sin_grafico if palabra in texto_lower)
            conteo_con_grafico = sum(1 for palabra in palabras_con_grafico if palabra in texto_lower)

            if conteo_con_grafico > conteo_sin_grafico:
                necesita_grafico = True
                tipo_grafico = 'barras'
                confidence = 0.5

        return {
            'consulta': text,
            'necesita_grafico': necesita_grafico,
            'tipo_grafico': tipo_grafico,
            'confianza': confidence
        }
    
    def _generate_reasoning(self, text: str, needs_chart: bool, chart_type: str, confidence: float) -> str:
        """Genera explicación de la predicción"""
        if not needs_chart:
            return f"El modelo no detectó necesidad de gráfico (confianza: {confidence:.2f})"
        
        reasoning_map = {
            "barras": f"El modelo detectó necesidad de gráfico de barras (confianza: {confidence:.2f})",
            "histograma": f"El modelo detectó necesidad de histograma (confianza: {confidence:.2f})",
            "lineal": f"El modelo detectó necesidad de gráfico lineal (confianza: {confidence:.2f})",
            "circular": f"El modelo detectó necesidad de gráfico circular (confianza: {confidence:.2f})",
            "dispersion": f"El modelo detectó necesidad de gráfico de dispersión (confianza: {confidence:.2f})"
        }
        
        return reasoning_map.get(chart_type, f"El modelo detectó necesidad de gráfico (confianza: {confidence:.2f})")
    
    def _fallback_detection(self, text: str) -> dict:
        """Lógica de fallback en caso de error del modelo"""
        text_lower = text.lower()
        chart_keywords = ['gráfico', 'grafico', 'chart', 'plot', 'grafica', 'gráfica']
        needs_chart = any(keyword in text_lower for keyword in chart_keywords)
        chart_type = 'barras' if needs_chart else 'ninguno'
        
        logger.warning("Usando detección de respaldo por fallo del modelo")
        return {
            "needs_chart": needs_chart,
            "chart_type": chart_type,
            "confidence": 0.5,
            "reasoning": "Detección de respaldo por fallo del modelo"
        }