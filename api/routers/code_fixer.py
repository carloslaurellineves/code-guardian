"""
Router para funcionalidades de Code Fixer.

Este módulo implementa endpoints para correção de bugs
e otimização de código usando agentes de IA.
"""

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
import time
from datetime import datetime

from schemas.code_schemas import BugFixRequest, BugFixResponse, CodeAnalysis
from schemas.common_schemas import ErrorResponse
from agents.bug_fixer_agent import BugFixerAgent

router = APIRouter()


@router.post(
    "/fix/bugs",
    response_model=BugFixResponse,
    status_code=status.HTTP_200_OK,
    summary="Corrigir Bugs",
    description="Corrige bugs no código fornecido"
)
async def fix_bugs(request: BugFixRequest) -> BugFixResponse:
    """
    Endpoint para correção de bugs no código.
    
    Args:
        request: Dados da requisição de correção de bugs
        
    Returns:
        BugFixResponse: Código corrigido e detalhes
        
    Raises:
        HTTPException: Em caso de erro na correção
    """
    try:
        start_time = time.time()
        
        # Inicializar agente corretor de código
        bug_fixer = BugFixerAgent()
        
        # Processar correção
        fixed_code_data = await bug_fixer.fix_bugs(request)
        
        processing_time = time.time() - start_time
        
        return BugFixResponse(
            success=True,
            fixed_code=fixed_code_data["code"],
            explanation=fixed_code_data["explanation"],
            changes_made=fixed_code_data["changes"],
            prevention_tips=fixed_code_data.get("tips", []),
            processing_time=processing_time
        )
        
    except Exception as e:
        error_response = ErrorResponse(
            error="BUG_FIX_ERROR",
            message=f"Erro ao corrigir código: {str(e)}",
            timestamp=datetime.now()
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response.dict()
        )


@router.post(
    "/analyze/code",
    response_model=CodeAnalysis,
    status_code=status.HTTP_200_OK,
    summary="Analisar Código",
    description="Analisa código em busca de problemas e oportunidades de melhoria"
)
async def analyze_code(code: str, language: str = "python") -> CodeAnalysis:
    """
    Endpoint para análise de código.
    
    Args:
        code: Código a ser analisado
        language: Linguagem de programação
        
    Returns:
        CodeAnalysis: Análise detalhada do código
        
    Raises:
        HTTPException: Em caso de erro na análise
    """
    try:
        # Inicializar agente corretor de código
        bug_fixer = BugFixerAgent()
        
        # Processar análise
        analysis = await bug_fixer.analyze_code(code, language)
        
        return analysis
        
    except Exception as e:
        error_response = ErrorResponse(
            error="CODE_ANALYSIS_ERROR",
            message=f"Erro ao analisar código: {str(e)}",
            timestamp=datetime.now()
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response.dict()
        )


@router.get(
    "/fix/suggestions",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Sugestões de Correção",
    description="Lista sugestões comuns para correção de bugs"
)
async def get_fix_suggestions() -> dict:
    """
    Endpoint para obter sugestões de correção.
    
    Returns:
        dict: Sugestões de correção organizadas por categoria
    """
    suggestions = {
        "common_fixes": {
            "null_pointer": [
                "Verificar se a variável foi inicializada",
                "Adicionar validação de nulo",
                "Usar operador de navegação segura"
            ],
            "index_out_of_bounds": [
                "Verificar o tamanho da lista/array",
                "Adicionar validação de índice",
                "Usar estruturas de controle apropriadas"
            ],
            "type_errors": [
                "Verificar tipos de dados",
                "Adicionar conversão de tipos",
                "Usar type hints em Python"
            ]
        },
        "best_practices": [
            "Seguir convenções de nomenclatura",
            "Adicionar documentação adequada",
            "Implementar tratamento de erros",
            "Usar padrões de design apropriados"
        ],
        "performance_tips": [
            "Otimizar loops aninhados",
            "Evitar operações desnecessárias",
            "Usar estruturas de dados eficientes",
            "Implementar cache quando apropriado"
        ]
    }
    
    return suggestions
