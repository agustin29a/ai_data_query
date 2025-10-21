import boto3
from app.config.config import Config
from app.utils.exceptions import BedrockError

class BedrockService:
    def __init__(self):
        self.config = Config()
        self.client = self._initialize_bedrock_client()
    
    def _initialize_bedrock_client(self):
        """Inicializa el cliente de Bedrock"""
        try:
            return boto3.client(
                service_name="bedrock-runtime",
                region_name=self.config.AWS_REGION
            )
        except Exception as e:
            raise BedrockError(f"Error inicializando cliente Bedrock: {str(e)}")
    
# Instancia global del servicio
bedrock_service = BedrockService()

