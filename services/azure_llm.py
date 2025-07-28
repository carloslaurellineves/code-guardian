"""
Serviço para integração com Azure OpenAI.

Implementação de comunicação e chamada aos serviços da
plataforma Azure OpenAI, utilizando credenciais configuradas.
"""

from typing import Any, Dict, Optional
import httpx
import logging
from config.settings import settings


class AzureLLMService:
    """
    Serviço responsável por interagir com o Azure OpenAI.

    Este serviço facilita a comunicação com a API para
    orquestração de tarefas de linguagem natural.
    """
    
    def __init__(self):
        """Inicializa o serviço com configurações do ambiente."""
        self.logger = logging.getLogger(__name__)
        
        # Obter configurações do Azure OpenAI
        self.config = settings.get_azure_openai_config()
        
        # Validar configurações obrigatórias
        self._validate_config()
        
        # Configurar cliente HTTP
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "api-key": self.config["api_key"],
                "Content-Type": "application/json"
            }
        )
        
        # Construir URL base
        self.base_url = self.config["endpoint"].rstrip('/') + '/openai/deployments/' + self.config["deployment_name"]
        
        self.logger.info(f"AzureLLMService inicializado com endpoint: {self.config['endpoint']}")
    
    def _validate_config(self) -> None:
        """Valida as configurações necessárias."""
        required_fields = ["endpoint", "api_key", "deployment_name"]
        missing_fields = [field for field in required_fields if not self.config.get(field)]
        
        if missing_fields:
            raise ValueError(
                f"Configurações obrigatórias do Azure OpenAI ausentes: {', '.join(missing_fields)}. "
                f"Verifique o arquivo .env."
            )
        
    async def generate_completion(self, prompt: str, max_tokens: int = 150) -> Dict[str, Any]:
        """
        Gera uma conclusão de linguagem baseada no prompt fornecido.
        
        Args:
            prompt: Texto prompt que orienta a geração
            max_tokens: Número máximo de tokens a serem gerados
            
        Returns:
            Dict[str, Any]: Resposta da API
        """
        url = f"{self.base_url}/completions?api-version=2023-05-15"
        
        payload = {
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": 0.7,
            "top_p": 1.0,
            "stop": None
        }
        
        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            self.logger.error(f"Erro na chamada para Azure OpenAI: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Erro inesperado: {e}")
            raise

    async def close(self):
        """Fecha o cliente HTTP se necessário."""
        await self.client.aclose()
