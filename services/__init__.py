"""
Módulo de serviços para integração com sistemas externos.

Este módulo contém serviços para integração com Azure OpenAI,
GitLab e outros sistemas externos utilizados pela aplicação.
"""

from .azure_llm import AzureLLMService
from .gitlab_service import GitLabService

__all__ = [
    "AzureLLMService",
    "GitLabService"
]
