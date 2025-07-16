"""
Cliente para consumir a API do backend CodeGuardian.

Este módulo fornece funções para interagir com os endpoints
da API do backend de forma padronizada.
"""

import requests
from typing import Dict, Any, Optional
from pathlib import Path
import sys

# Adicionar diretório raiz ao path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))


class APIClient:
    """
    Cliente para consumir a API do CodeGuardian.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000/api/v1"):
        """
        Inicializa o cliente da API.
        
        Args:
            base_url: URL base da API
        """
        self.base_url = base_url
        self.timeout = 30
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "CodeGuardian-Frontend/1.0"
        })
    
    def health_check(self) -> Dict[str, Any]:
        """
        Verifica o status da API.
        
        Returns:
            Dict com o status da API
        """
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            response.raise_for_status()
            return {"status": "healthy", "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"status": "error", "error": str(e)}
    
    def generate_stories(self, context: str, format_type: str = "gherkin") -> Dict[str, Any]:
        """
        Gera histórias usando o agente Story Creator.
        
        Args:
            context: Contexto do produto/funcionalidade
            format_type: Formato das histórias (gherkin, user_story, etc.)
            
        Returns:
            Dict com as histórias geradas ou erro
        """
        try:
            payload = {
                "context": context,
                "format": format_type,
                "include_acceptance_criteria": True
            }
            
            response = requests.post(
                f"{self.base_url}/stories/generate",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"status": "error", "error": str(e)}
    
    def generate_tests(self, code: Optional[str] = None, 
                      gitlab_url: Optional[str] = None,
                      file_content: Optional[bytes] = None,
                      file_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Gera testes unitários usando o agente Code Tester.
        
        Args:
            code: Código fonte para gerar testes
            gitlab_url: URL do repositório GitLab
            file_content: Conteúdo do arquivo enviado
            file_name: Nome do arquivo enviado
            
        Returns:
            Dict com os testes gerados ou erro
        """
        try:
            if file_content and file_name:
                # Upload de arquivo
                files = {"file": (file_name, file_content)}
                response = requests.post(
                    f"{self.base_url}/code/tests/generate",
                    files=files,
                    timeout=self.timeout
                )
            else:
                # Código ou URL
                payload = {
                    "code": code,
                    "gitlab_url": gitlab_url
                }
                response = requests.post(
                    f"{self.base_url}/code/tests/generate",
                    json=payload,
                    timeout=self.timeout
                )
            
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"status": "error", "error": str(e)}
    
    def fix_code(self, error_message: str, code: str) -> Dict[str, Any]:
        """
        Corrige bugs no código usando o agente Code Fixer.
        
        Args:
            error_message: Mensagem de erro
            code: Código com o bug
            
        Returns:
            Dict com o código corrigido ou erro
        """
        try:
            payload = {
                "error_message": error_message,
                "code": code
            }
            
            response = requests.post(
                f"{self.base_url}/fix/bugs",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"status": "error", "error": str(e)}


# Instância global do cliente
api_client = APIClient()
