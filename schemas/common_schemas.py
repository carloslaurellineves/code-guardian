"""
Schemas comuns utilizados em toda a aplicação.

Este módulo define os modelos de dados compartilhados entre
diferentes componentes da API.
"""

from pydantic import BaseModel, Field
from typing import Any, Optional
from datetime import datetime


class HealthResponse(BaseModel):
    """
    Schema para resposta do health check.
    
    Attributes:
        status: Status da aplicação
        message: Mensagem informativa
        timestamp: Timestamp da verificação
        version: Versão da aplicação
    """
    status: str = Field(..., description="Status da aplicação")
    message: str = Field(..., description="Mensagem informativa")
    timestamp: datetime = Field(..., description="Timestamp da verificação")
    version: str = Field(..., description="Versão da aplicação")


class ErrorResponse(BaseModel):
    """
    Schema para resposta de erro.
    
    Attributes:
        error: Tipo do erro
        message: Mensagem de erro
        details: Detalhes adicionais do erro
        timestamp: Timestamp do erro
    """
    error: str = Field(..., description="Tipo do erro")
    message: str = Field(..., description="Mensagem de erro")
    details: Optional[Any] = Field(None, description="Detalhes adicionais do erro")
    timestamp: datetime = Field(..., description="Timestamp do erro")


class ProcessingStatus(BaseModel):
    """
    Schema para status de processamento.
    
    Attributes:
        status: Status do processamento
        progress: Progresso em porcentagem
        message: Mensagem de status
        started_at: Timestamp de início
        estimated_completion: Estimativa de conclusão
    """
    status: str = Field(..., description="Status do processamento")
    progress: int = Field(..., ge=0, le=100, description="Progresso em porcentagem")
    message: str = Field(..., description="Mensagem de status")
    started_at: datetime = Field(..., description="Timestamp de início")
    estimated_completion: Optional[datetime] = Field(None, description="Estimativa de conclusão")
