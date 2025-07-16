"""
Router para funcionalidades de Code Tester.

Este módulo implementa endpoints para geração de testes
unitários e análise de código usando agentes de IA.
"""

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
import time
from datetime import datetime

from schemas.code_schemas import CodeRequest, CodeResponse, BugFixRequest, BugFixResponse
from schemas.common_schemas import ErrorResponse
from agents.test_generator_agent import TestGeneratorAgent
from agents.bug_fixer_agent import BugFixerAgent

router = APIRouter()


@router.post(
    "/code/tests/generate",
    response_model=CodeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Gerar Testes Unitários",
    description="Gera testes unitários baseados no código fornecido"
)
async def generate_tests(request: CodeRequest) -> CodeResponse:
    """
    Endpoint para geração de testes unitários.
    
    Args:
        request: Dados da requisição de geração de testes
        
    Returns:
        CodeResponse: Testes gerados e análise
        
    Raises:
        HTTPException: Em caso de erro na geração
    """
    try:
        start_time = time.time()
        
        # Inicializar agente gerador de testes
        test_agent = TestGeneratorAgent()
        
        # Processar geração de testes
        tests, analysis = await test_agent.generate_tests(request)
        
        processing_time = time.time() - start_time
        
        return CodeResponse(
            success=True,
            tests=tests,
            analysis=analysis,
            summary="Testes gerados com sucesso",
            recommendations=[
                "Revise os testes gerados",
                "Considere ajustar as coberturas de código",
                "Valide a integração com o código existente"
            ],
            processing_time=processing_time
        )
        
    except Exception as e:
        error_response = ErrorResponse(
            error="TEST_GENERATION_ERROR",
            message=f"Erro ao gerar testes: {str(e)}",
            timestamp=datetime.now()
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response.dict()
        )


@router.post(
    "/code/fix/bugs",
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
