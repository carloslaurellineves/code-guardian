"""
Configurações principais para a aplicação Code Guardian.

Carrega as variáveis de ambiente usando dotenv para acessar
informações sensíveis e configurações.
"""

import os
from pathlib import Path
from typing import List, Optional, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings

# Caminho para o arquivo .env
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"

class Settings(BaseSettings):
    """
    Configurações globais para a aplicação.

    Variáveis de ambiente e configurações sensíveis são
    configuradas através do arquivo .env.
    """

    # Configurações do Azure OpenAI
    azure_openai_endpoint: Optional[str] = Field(default=None, description="Endpoint do Azure OpenAI")
    azure_openai_api_key: Optional[str] = Field(default=None, description="Chave da API do Azure OpenAI")
    azure_openai_api_version: str = Field(default="2023-12-01-preview", description="Versão da API")
    azure_openai_deployment_name: Optional[str] = Field(default=None, description="Nome do deployment")
    azure_openai_model_name: str = Field(default="gpt-4", description="Nome do modelo")
    
    # Configurações da OpenAI Padrão (Fallback)
    openai_api_key: Optional[str] = Field(default=None, description="Chave da API do OpenAI")
    openai_model_name: str = Field(default="gpt-4o-mini", description="Nome do modelo OpenAI")
    
    # Configurações do GitLab
    gitlab_api_url: str = Field(default="https://gitlab.com/api/v4", description="URL da API do GitLab")
    gitlab_access_token: Optional[str] = Field(default=None, description="Token de acesso do GitLab")
    gitlab_project_id: Optional[str] = Field(default=None, description="ID do projeto GitLab")
    
    # Configurações da Aplicação
    app_name: str = Field(default="CodeGuardian", description="Nome da aplicação")
    app_version: str = Field(default="0.1.0", description="Versão da aplicação")
    app_environment: str = Field(default="development", description="Ambiente da aplicação")
    app_debug: bool = Field(default=False, description="Modo debug")
    app_log_level: str = Field(default="INFO", description="Nível de log")
    
    # Configurações do Servidor
    server_host: str = Field(default="0.0.0.0", description="Host do servidor")
    server_port: int = Field(default=8000, description="Porta do servidor")
    server_reload: bool = Field(default=False, description="Recarregamento automático")
    
    # Configurações de Segurança
    secret_key: str = Field(default="your-secret-key-change-in-production", description="Chave secreta")
    allowed_origins: Union[str, List[str]] = Field(default="*", description="Origens permitidas para CORS")
    
    @field_validator('allowed_origins', mode='before')
    @classmethod
    def parse_allowed_origins(cls, v):
        if isinstance(v, str):
            if ',' in v:
                return [origin.strip() for origin in v.split(',')]
            return [v]
        return v
    
    # Configurações de Banco de Dados
    database_url: str = Field(default="sqlite:///./code_guardian.db", description="URL do banco de dados")
    database_pool_size: int = Field(default=5, description="Tamanho do pool de conexões")
    database_max_overflow: int = Field(default=10, description="Overflow máximo do pool")
    
    # Configurações de Cache
    redis_url: str = Field(default="redis://localhost:6379/0", description="URL do Redis")
    cache_ttl: int = Field(default=3600, description="TTL do cache em segundos")
    
    # Configurações de Logging
    log_level: str = Field(default="INFO", description="Nível de log")
    log_format: str = Field(default="json", description="Formato do log")
    log_file_path: str = Field(default="logs/code_guardian.log", description="Caminho do arquivo de log")
    log_max_size: str = Field(default="10MB", description="Tamanho máximo do log")
    log_backup_count: int = Field(default=5, description="Número de backups de log")
    
    # Configurações de Testes
    test_azure_openai_endpoint: Optional[str] = Field(default=None, description="Endpoint de teste do Azure OpenAI")
    test_azure_openai_api_key: Optional[str] = Field(default=None, description="Chave de teste do Azure OpenAI")
    test_environment: str = Field(default="testing", description="Ambiente de teste")
    
    model_config = {
        "env_file": str(ENV_FILE),
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }
    
    @property
    def is_development(self) -> bool:
        """Check if application is running in development mode."""
        return self.app_environment.lower() == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if application is running in production mode."""
        return self.app_environment.lower() == "production"
    
    @property
    def is_testing(self) -> bool:
        """Check if application is running in testing mode."""
        return self.app_environment.lower() == "testing"
    
    def get_azure_openai_config(self) -> dict:
        """Get Azure OpenAI configuration as dictionary."""
        return {
            "endpoint": self.azure_openai_endpoint,
            "api_key": self.azure_openai_api_key,
            "api_version": self.azure_openai_api_version,
            "deployment_name": self.azure_openai_deployment_name,
            "model_name": self.azure_openai_model_name
        }
    
    def get_openai_config(self) -> dict:
        """Get OpenAI configuration as dictionary."""
        return {
            "api_key": self.openai_api_key,
            "model_name": self.openai_model_name
        }
    
    def get_gitlab_config(self) -> dict:
        """Get GitLab configuration as dictionary."""
        return {
            "api_url": self.gitlab_api_url,
            "access_token": self.gitlab_access_token,
            "project_id": self.gitlab_project_id
        }

# Instância global de configurações
settings = Settings()
