"""
Schemas para funcionalidades relacionadas a código.

Este módulo define os modelos de dados para entrada e saída
das funcionalidades de geração de testes e correção de código.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from enum import Enum
import re


class CodeLanguage(str, Enum):
    """
    Linguagens de programação suportadas.
    """
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    JAVA = "java"
    CSHARP = "csharp"
    TYPESCRIPT = "typescript"
    GO = "go"
    RUST = "rust"
    PHP = "php"


class InputType(str, Enum):
    """
    Tipos de entrada de código.
    """
    DIRECT = "direct"
    FILE_UPLOAD = "file_upload"
    GITLAB_REPO = "gitlab_repo"


class TestFramework(str, Enum):
    """
    Frameworks de teste suportados.
    """
    PYTEST = "pytest"
    UNITTEST = "unittest"
    JEST = "jest"
    JUNIT = "junit"
    NUNIT = "nunit"
    MOCHA = "mocha"
    GOTEST = "gotest"
    AUTO = "auto"  # Detecta automaticamente


class CodeRequest(BaseModel):
    """
    Schema para requisição de processamento de código.
    
    Attributes:
        input_type: Tipo de entrada do código
        code_content: Conteúdo do código (para entrada direta)
        file_name: Nome do arquivo (para upload)
        language: Linguagem de programação
        test_framework: Framework de teste preferido
        include_mocks: Se deve incluir mocks nos testes
        coverage_target: Meta de cobertura de código
        additional_context: Contexto adicional para geração
    """
    input_type: InputType = Field(..., description="Tipo de entrada do código")
    code_content: Optional[str] = Field(None, description="Conteúdo do código (para entrada direta)")
    file_name: Optional[str] = Field(None, description="Nome do arquivo (para upload)")
    language: CodeLanguage = Field(..., description="Linguagem de programação")
    test_framework: TestFramework = Field(default=TestFramework.AUTO, description="Framework de teste preferido")
    include_mocks: bool = Field(default=True, description="Se deve incluir mocks nos testes")
    coverage_target: int = Field(default=80, ge=0, le=100, description="Meta de cobertura de código")
    additional_context: Optional[str] = Field(None, description="Contexto adicional para geração")
    
    @validator('code_content')
    def validate_code_content(cls, v, values):
        """
        Valida se o código foi fornecido quando necessário.
        """
        if values.get('input_type') == InputType.DIRECT and not v:
            raise ValueError("code_content é obrigatório para entrada direta")
        return v
    
    @validator('file_name')
    def validate_file_name(cls, v, values):
        """
        Valida se o nome do arquivo foi fornecido quando necessário.
        """
        if values.get('input_type') == InputType.FILE_UPLOAD and not v:
            raise ValueError("file_name é obrigatório para upload de arquivo")
        return v


class GitLabRequest(BaseModel):
    """
    Schema para requisição de código do GitLab.
    
    Attributes:
        repository_url: URL do repositório GitLab
        branch: Branch a ser analisada
        file_path: Caminho específico do arquivo (opcional)
        access_token: Token de acesso (opcional)
        include_dependencies: Se deve incluir dependências na análise
        recursive: Se deve processar recursivamente
    """
    repository_url: str = Field(..., description="URL do repositório GitLab")
    branch: str = Field(default="main", description="Branch a ser analisada")
    file_path: Optional[str] = Field(None, description="Caminho específico do arquivo (opcional)")
    access_token: Optional[str] = Field(None, description="Token de acesso (opcional)")
    include_dependencies: bool = Field(default=False, description="Se deve incluir dependências na análise")
    recursive: bool = Field(default=True, description="Se deve processar recursivamente")
    
    @validator('repository_url')
    def validate_repository_url(cls, v):
        """
        Valida se a URL do repositório é válida.
        """
        gitlab_pattern = r'^https?://.*gitlab.*\.git$|^https?://.*gitlab.*/.*/.*/.*$'
        if not re.match(gitlab_pattern, v, re.IGNORECASE):
            raise ValueError("URL do repositório GitLab inválida")
        return v


class GeneratedTest(BaseModel):
    """
    Schema para um teste gerado.
    
    Attributes:
        test_name: Nome do teste
        test_code: Código do teste
        framework: Framework utilizado
        coverage_estimation: Estimativa de cobertura
        dependencies: Dependências necessárias
        description: Descrição do teste
    """
    test_name: str = Field(..., description="Nome do teste")
    test_code: str = Field(..., description="Código do teste")
    framework: TestFramework = Field(..., description="Framework utilizado")
    coverage_estimation: int = Field(..., ge=0, le=100, description="Estimativa de cobertura")
    dependencies: List[str] = Field(default_factory=list, description="Dependências necessárias")
    description: str = Field(..., description="Descrição do teste")


class CodeAnalysis(BaseModel):
    """
    Schema para análise de código.
    
    Attributes:
        complexity_score: Pontuação de complexidade
        maintainability_index: Índice de manutenibilidade
        test_coverage_potential: Potencial de cobertura de testes
        code_smells: Lista de problemas identificados
        suggestions: Sugestões de melhoria
    """
    complexity_score: int = Field(..., ge=0, le=100, description="Pontuação de complexidade")
    maintainability_index: int = Field(..., ge=0, le=100, description="Índice de manutenibilidade")
    test_coverage_potential: int = Field(..., ge=0, le=100, description="Potencial de cobertura de testes")
    code_smells: List[str] = Field(default_factory=list, description="Lista de problemas identificados")
    suggestions: List[str] = Field(default_factory=list, description="Sugestões de melhoria")


class CodeResponse(BaseModel):
    """
    Schema para resposta de processamento de código.
    
    Attributes:
        success: Indica se a operação foi bem-sucedida
        tests: Lista de testes gerados
        analysis: Análise do código
        summary: Resumo da geração
        recommendations: Recomendações para melhoria
        processing_time: Tempo de processamento em segundos
        metadata: Metadados adicionais
    """
    success: bool = Field(..., description="Indica se a operação foi bem-sucedida")
    tests: List[GeneratedTest] = Field(..., description="Lista de testes gerados")
    analysis: CodeAnalysis = Field(..., description="Análise do código")
    summary: str = Field(..., description="Resumo da geração")
    recommendations: List[str] = Field(default_factory=list, description="Recomendações para melhoria")
    processing_time: float = Field(..., description="Tempo de processamento em segundos")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadados adicionais")


class BugFixRequest(BaseModel):
    """
    Schema para requisição de correção de bugs.
    
    Attributes:
        code_with_bug: Código com o bug
        error_description: Descrição do erro
        error_traceback: Traceback do erro (opcional)
        language: Linguagem de programação
        context: Contexto adicional
        fix_approach: Abordagem preferida para correção
    """
    code_with_bug: str = Field(..., description="Código com o bug")
    error_description: str = Field(..., description="Descrição do erro")
    error_traceback: Optional[str] = Field(None, description="Traceback do erro (opcional)")
    language: CodeLanguage = Field(..., description="Linguagem de programação")
    context: Optional[str] = Field(None, description="Contexto adicional")
    fix_approach: Optional[str] = Field(None, description="Abordagem preferida para correção")


class BugFixResponse(BaseModel):
    """
    Schema para resposta de correção de bugs.
    
    Attributes:
        success: Indica se a operação foi bem-sucedida
        fixed_code: Código corrigido
        explanation: Explicação da correção
        changes_made: Lista de mudanças realizadas
        prevention_tips: Dicas para prevenir bugs similares
        processing_time: Tempo de processamento em segundos
    """
    success: bool = Field(..., description="Indica se a operação foi bem-sucedida")
    fixed_code: str = Field(..., description="Código corrigido")
    explanation: str = Field(..., description="Explicação da correção")
    changes_made: List[str] = Field(..., description="Lista de mudanças realizadas")
    prevention_tips: List[str] = Field(default_factory=list, description="Dicas para prevenir bugs similares")
    processing_time: float = Field(..., description="Tempo de processamento em segundos")
