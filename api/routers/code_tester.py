"""
Router para funcionalidades de Code Tester.

Este módulo implementa endpoints para geração de testes
unitários e análise de código usando agentes de IA.
"""

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
import time
from datetime import datetime

from schemas.code_schemas import CodeRequest, CodeResponse, CodeLanguage, TestFramework
from schemas.common_schemas import ErrorResponse
from agents.test_generator_agent import TestGeneratorAgent

router = APIRouter()


def validate_language_framework_consistency(language: CodeLanguage, framework: TestFramework) -> tuple[bool, str]:
    """
    Valida se a linguagem é compatível com o framework de teste selecionado.
    
    Args:
        language: Linguagem de programação
        framework: Framework de teste
        
    Returns:
        tuple[bool, str]: (é_válido, mensagem_erro)
    """
    # Mapeamento de linguagens para frameworks compatíveis
    language_framework_compatibility = {
        CodeLanguage.PYTHON: [TestFramework.PYTEST, TestFramework.UNITTEST, TestFramework.AUTO],
        CodeLanguage.JAVASCRIPT: [TestFramework.JEST, TestFramework.MOCHA, TestFramework.AUTO],
        CodeLanguage.TYPESCRIPT: [TestFramework.JEST, TestFramework.MOCHA, TestFramework.AUTO],
        CodeLanguage.JAVA: [TestFramework.JUNIT, TestFramework.AUTO],
        CodeLanguage.CSHARP: [TestFramework.NUNIT, TestFramework.AUTO],
        CodeLanguage.GO: [TestFramework.GOTEST, TestFramework.AUTO],
        CodeLanguage.RUST: [TestFramework.PYTEST, TestFramework.AUTO],  # Fallback
        CodeLanguage.PHP: [TestFramework.PYTEST, TestFramework.AUTO]   # Fallback
    }
    
    compatible_frameworks = language_framework_compatibility.get(language, [TestFramework.AUTO])
    
    if framework in compatible_frameworks:
        return True, ""
    
    # Framework não compatível - gerar mensagem de erro informativa
    framework_names = [f.value for f in compatible_frameworks if f != TestFramework.AUTO]
    suggested_frameworks = ", ".join(framework_names) if framework_names else "AUTO"
    
    error_message = (
        f"Framework '{framework.value}' não é compatível com a linguagem '{language.value}'. "
        f"Frameworks suportados para {language.value}: {suggested_frameworks}"
    )
    
    return False, error_message


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
        
        # Validar consistência entre linguagem e framework
        is_valid, error_message = validate_language_framework_consistency(request.language, request.test_framework)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "error": "LANGUAGE_FRAMEWORK_INCOMPATIBLE",
                    "message": error_message,
                    "language": request.language.value,
                    "framework": request.test_framework.value,
                    "timestamp": datetime.now().isoformat()
                }
            )
        
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
                "timestamp": datetime.now().isoformat()
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
        
        # Serializar o ErrorResponse corretamente
        error_dict = error_response.dict()
        error_dict['timestamp'] = error_response.timestamp.isoformat()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_dict
        )
