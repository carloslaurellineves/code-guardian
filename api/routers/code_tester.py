"""
Router para funcionalidades de Code Tester.

Este módulo implementa endpoints para geração de testes
unitários e análise de código usando agentes de IA.
"""

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
import time
from datetime import datetime

from schemas.code_schemas import CodeRequest, CodeResponse
from schemas.common_schemas import ErrorResponse
from agents.test_generator_agent import TestGeneratorAgent

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
        
        # Validar integridade dos testes gerados
        tests_valid, validation_errors = test_agent._validate_test_integrity(tests)
        
        if not tests_valid:
            # Se testes são inválidos, retornar erro 422 (Unprocessable Entity)
            from fastapi import HTTPException
            error_details = {
                "error": "INVALID_TESTS_GENERATED",
                "message": "Os testes gerados não atendem aos critérios de qualidade",
                "validation_errors": validation_errors,
                "timestamp": datetime.now()
            }
            raise HTTPException(
                status_code=422,
                detail=error_details
            )
        
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
