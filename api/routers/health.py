"""
Router de health check para monitoramento da aplicação.

Este módulo implementa endpoints para verificação de saúde
e status da aplicação.
"""

from fastapi import APIRouter, status
from datetime import datetime

from schemas.common_schemas import HealthResponse

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    description="Verifica se a aplicação está funcionando corretamente"
)
async def health_check() -> HealthResponse:
    """
    Endpoint de health check.
    
    Returns:
        HealthResponse: Status da aplicação
    """
    return HealthResponse(
        status="healthy",
        message="Code Guardian API está funcionando corretamente",
        timestamp=datetime.now(),
        version="0.1.0"
    )


@router.get(
    "/health/detailed",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Health Check Detalhado",
    description="Verifica o status detalhado dos componentes da aplicação"
)
async def detailed_health_check() -> dict:
    """
    Endpoint de health check detalhado.
    
    Returns:
        dict: Status detalhado dos componentes
    """
    # Em implementação futura, verificar conexões com serviços externos
    components = {
        "api": {
            "status": "healthy",
            "message": "API funcionando normalmente"
        },
        "azure_openai": {
            "status": "unknown",
            "message": "Verificação não implementada"
        },
        "gitlab_connection": {
            "status": "unknown", 
            "message": "Verificação não implementada"
        },
        "agents": {
            "status": "unknown",
            "message": "Verificação não implementada"
        }
    }
    
    overall_status = "healthy"
    
    return {
        "status": overall_status,
        "timestamp": datetime.now(),
        "components": components,
        "version": "0.1.0"
    }
