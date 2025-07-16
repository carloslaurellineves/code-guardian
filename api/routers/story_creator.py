"""
Router para funcionalidades de Story Creator.

Este módulo implementa endpoints para criação de histórias
em formato Gherkin usando agentes de IA.
"""

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
import time
import uuid
from datetime import datetime

from schemas.story_schemas import StoryRequest, StoryResponse, GeneratedStory, AcceptanceCriteria, StoryType
from schemas.common_schemas import ErrorResponse
from agents.story_agent import StoryAgent

router = APIRouter()


@router.post(
    "/stories/generate",
    response_model=StoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Gerar Histórias",
    description="Gera histórias em formato Gherkin baseadas no contexto fornecido"
)
async def generate_stories(request: StoryRequest) -> StoryResponse:
    """
    Endpoint para geração de histórias.
    
    Args:
        request: Dados da requisição de geração
        
    Returns:
        StoryResponse: Histórias geradas
        
    Raises:
        HTTPException: Em caso de erro na geração
    """
    try:
        start_time = time.time()
        
        # Inicializar agente de histórias
        story_agent = StoryAgent()
        
        # Processar requisição
        stories = await story_agent.generate_stories(request)
        
        processing_time = time.time() - start_time
        
        return StoryResponse(
            success=True,
            stories=stories,
            summary=f"Geradas {len(stories)} história(s) com sucesso",
            recommendations=[
                "Revise os critérios de aceitação gerados",
                "Considere adicionar mais contexto se necessário",
                "Valide as estimativas de esforço com a equipe"
            ],
            processing_time=processing_time
        )
        
    except Exception as e:
        error_response = ErrorResponse(
            error="STORY_GENERATION_ERROR",
            message=f"Erro ao gerar histórias: {str(e)}",
            timestamp=datetime.now()
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response.dict()
        )


@router.post(
    "/stories/validate",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Validar História",
    description="Valida uma história em formato Gherkin"
)
async def validate_story(story: GeneratedStory) -> dict:
    """
    Endpoint para validação de histórias.
    
    Args:
        story: História a ser validada
        
    Returns:
        dict: Resultado da validação
    """
    try:
        story_agent = StoryAgent()
        validation_result = await story_agent.validate_story(story)
        
        return {
            "valid": validation_result["valid"],
            "issues": validation_result.get("issues", []),
            "suggestions": validation_result.get("suggestions", []),
            "score": validation_result.get("score", 0)
        }
        
    except Exception as e:
        error_response = ErrorResponse(
            error="STORY_VALIDATION_ERROR",
            message=f"Erro ao validar história: {str(e)}",
            timestamp=datetime.now()
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response.dict()
        )


@router.get(
    "/stories/templates",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Listar Templates",
    description="Lista templates disponíveis para geração de histórias"
)
async def list_story_templates() -> dict:
    """
    Endpoint para listar templates de histórias.
    
    Returns:
        dict: Templates disponíveis
    """
    templates = {
        "epic": {
            "name": "Épico",
            "description": "Template para criação de épicos",
            "structure": "Como [tipo de usuário], eu quero [objetivo] para [benefício]"
        },
        "user_story": {
            "name": "História de Usuário",
            "description": "Template para criação de histórias de usuário",
            "structure": "Como [persona], eu quero [funcionalidade] para [valor de negócio]"
        },
        "task": {
            "name": "Tarefa",
            "description": "Template para criação de tarefas técnicas",
            "structure": "Implementar [funcionalidade] considerando [restrições]"
        }
    }
    
    return {
        "templates": templates,
        "supported_languages": ["pt-BR", "en-US", "es-ES"],
        "story_types": [story_type.value for story_type in StoryType]
    }
