"""
Agente para geração de testes unitários.

Este módulo implementa um agente baseado em LangGraph para
geração automatizada de testes unitários a partir de código.
"""

import uuid
from typing import List, Tuple, Dict, Any

from schemas.code_schemas import (
    CodeRequest, 
    GeneratedTest, 
    CodeAnalysis,
    TestFramework,
    InputType,
    CodeLanguage
)
from services.azure_llm import AzureLLMService
from services.gitlab_service import GitLabService


unit_test_policy = {
    "version": "1.0",
    "generated_for": "IA Agent - Test Generator",
    "last_updated": "2025-07-10",

    "naming": {
        "style": "human_readable_sentence",
        "examples": [
            "should_return_false_when_balance_is_insufficient",
            "should_throw_error_when_user_is_not_authenticated",
            "deve_retornar_erro_quando_usuario_estiver_desconectado"
        ],
        "guidelines": [
            "Use sentenças descritivas que expressem comportamento esperado",
            "Evite acoplamento a nomes internos de métodos ou variáveis",
            "Use snake_case ou camelCase conforme a linguagem exigir",
            "Use prefixos como 'should_', 'deve_', 'quando_', 'retorna_'"
        ]
    },

    "structure": {
        "format": "AAA",
        "steps": [
            {"arrange": "Configure os dados, mocks e contexto necessários"},
            {"act": "Execute a ação ou função sob teste"},
            {"assert": "Verifique o comportamento ou valor esperado"}
        ],
        "example_structure": [
            "Dado que uma conta tem saldo zero",
            "Quando uma retirada é solicitada",
            "Então deve retornar erro de saldo insuficiente"
        ]
    },

    "organization": {
        "project_folders": {
            "source_code": "/src/<project_name>/",
            "test_code": "/tests/<project_name>.Tests/"
        },
        "test_file_naming": {
            "pattern": "<ClassName>Should"
        },
        "test_grouping": [
            "Organizar testes por componente ou classe principal",
            "Testes relacionados a métodos similares podem estar no mesmo arquivo"
        ]
    },

    "quality_criteria": [
        "Testes devem ser rápidos (execução em milissegundos)",
        "Devem ser determinísticos (sem flutuação de resultados)",
        "Isolados de dependências externas (sem acesso real à rede, banco ou tempo)",
        "Utilizar mocks, stubs ou fakes para dependências externas",
        "Testes devem ser autoexplicativos sem necessidade de comentários",
        "Cobrir caminhos principais, bordas e exceções de forma independente"
    ],

    "test_design": {
        "test_type": "unit",
        "mock_usage": "true",
        "coverage_expectation": {
            "min_expected_coverage": 80,
            "required_for": ["critical modules", "core business logic"]
        },
        "language_independent_expectations": [
            "Os testes devem refletir regras de negócio, não apenas cobertura técnica",
            "Um teste por cenário, evitando múltiplos asserts se possível",
            "Falhas devem fornecer mensagens claras sobre a causa do erro"
        ]
    },

    "agent_instructions": {
        "expected_input": "Código-fonte em linguagem suportada, em texto puro ou estruturado",
        "expected_output": [
            "Arquivo ou trecho de teste com nomes claros e estruturado conforme esta política",
            "Uso explícito de AAA",
            "Inclusão de mocks quando detectadas dependências externas"
        ],
        "fallback_behavior": [
            "Se houver ambiguidade, gerar o teste mais simples possível e sinalizar incerteza",
            "Nunca inventar lógicas de negócio: basear-se apenas no código fornecido"
        ]
    }
}

class TestGeneratorAgent:
    """
    Agente responsável pela geração de testes unitários.
    
    Este agente utiliza LangGraph para orquestrar o processo
    de análise de código e geração de testes.
    """
    
    def __init__(self):
        """Inicializa o agente gerador de testes."""
        self.llm_service = AzureLLMService()
        self.gitlab_service = GitLabService()
        
    async def generate_tests(self, request: CodeRequest) -> Tuple[List[GeneratedTest], CodeAnalysis]:
        """
        Gera testes unitários baseados na requisição.
        
        Args:
            request: Dados da requisição de geração de testes
            
        Returns:
            Tuple[List[GeneratedTest], CodeAnalysis]: Testes gerados e análise
        """
        # Obter código baseado no tipo de entrada
        code_content = await self._get_code_content(request)
        
        # Analisar código
        analysis = await self._analyze_code(code_content, request.language)
        
        # Gerar testes
        tests = await self._generate_tests_for_code(code_content, request, analysis)
        
        return tests, analysis
        
    async def _get_code_content(self, request: CodeRequest) -> str:
        """
        Obtém o conteúdo do código baseado no tipo de entrada.
        
        Args:
            request: Dados da requisição
            
        Returns:
            str: Conteúdo do código
        """
        if request.input_type == InputType.DIRECT:
            return request.code_content
            
        elif request.input_type == InputType.FILE_UPLOAD:
            # Mock implementation - em produção, processar arquivo
            return f"# Código do arquivo: {request.file_name}\n\ndef exemplo_funcao():\n    return 'Hello World'"
            
        elif request.input_type == InputType.GITLAB_REPO:
            # Mock implementation - em produção, usar GitLabService
            return "# Código do repositório GitLab\n\ndef gitlab_function():\n    return 'From GitLab'"
            
        else:
            raise ValueError(f"Tipo de entrada não suportado: {request.input_type}")
            
    async def _analyze_code(self, code_content: str, language: CodeLanguage) -> CodeAnalysis:
        """
        Analisa o código fornecido.
        
        Args:
            code_content: Conteúdo do código
            language: Linguagem de programação
            
        Returns:
            CodeAnalysis: Análise do código
        """
        # Mock implementation
        return CodeAnalysis(
            complexity_score=75,
            maintainability_index=80,
            test_coverage_potential=85,
            code_smells=[
                "Função muito longa",
                "Falta de documentação"
            ],
            suggestions=[
                "Dividir função em funções menores",
                "Adicionar docstrings",
                "Implementar validação de entrada"
            ]
        )
        
    async def _generate_tests_for_code(self, code_content: str, request: CodeRequest, analysis: CodeAnalysis) -> List[GeneratedTest]:
        """
        Gera testes unitários para o código seguindo a política de testes.
        
        Args:
            code_content: Conteúdo do código
            request: Dados da requisição
            analysis: Análise do código
            
        Returns:
            List[GeneratedTest]: Lista de testes gerados
        """
        tests = []
        
        # Determinar framework de teste
        framework = self._determine_test_framework(request.test_framework, request.language)
        
        # Analisar código para extrair informações estruturais
        code_analysis = self._analyze_code_structure(code_content, request.language)
        
        # Gerar testes seguindo a política
        test_cases = self._generate_test_cases_from_policy(code_analysis, request.language)
        
        for test_case in test_cases:
            test_code = self._generate_test_code_following_policy(
                test_case, framework, request.language, code_analysis
            )
            
            test = GeneratedTest(
                test_name=test_case["name"],
                test_code=test_code,
                framework=framework,
                coverage_estimation=test_case["coverage"],
                dependencies=self._get_test_dependencies(framework),
                description=test_case["description"]
            )
            
            tests.append(test)
            
        return tests
    
    def _analyze_code_structure(self, code_content: str, language: CodeLanguage) -> Dict[str, Any]:
        """
        Analisa a estrutura do código para extrair informações relevantes.
        
        Args:
            code_content: Conteúdo do código
            language: Linguagem de programação
            
        Returns:
            Dict[str, Any]: Análise estrutural do código
        """
        # Mock implementation - em produção, usar parser de código
        import re
        
        analysis = {
            "functions": [],
            "classes": [],
            "dependencies": [],
            "complexity": "medium",
            "has_external_dependencies": False
        }
        
        if language == CodeLanguage.PYTHON:
            # Extrair funções
            function_pattern = r'def\s+(\w+)\s*\([^)]*\):'
            functions = re.findall(function_pattern, code_content)
            analysis["functions"] = functions
            
            # Extrair classes
            class_pattern = r'class\s+(\w+)\s*[\(:]'
            classes = re.findall(class_pattern, code_content)
            analysis["classes"] = classes
            
            # Detectar dependências externas
            external_deps = ['requests', 'database', 'file', 'network', 'time', 'random']
            for dep in external_deps:
                if dep in code_content.lower():
                    analysis["has_external_dependencies"] = True
                    analysis["dependencies"].append(dep)
                    break
        
        return analysis
    
    def _generate_test_cases_from_policy(self, code_analysis: Dict[str, Any], language: CodeLanguage) -> List[Dict[str, Any]]:
        """
        Gera casos de teste seguindo a política de testes.
        
        Args:
            code_analysis: Análise estrutural do código
            language: Linguagem de programação
            
        Returns:
            List[Dict[str, Any]]: Lista de casos de teste
        """
        test_cases = []
        
        # Definir prefixos baseados na linguagem
        prefixes = {
            CodeLanguage.PYTHON: "should_",
            CodeLanguage.JAVASCRIPT: "should_",
            CodeLanguage.JAVA: "should_",
            CodeLanguage.CSHARP: "Should_"
        }
        
        prefix = prefixes.get(language, "should_")
        
        # Gerar testes para cada função encontrada
        for func_name in code_analysis.get("functions", ["main_function"]):
            # Teste de comportamento normal
            test_cases.append({
                "name": f"{prefix}return_expected_value_when_{func_name}_called_with_valid_input",
                "description": f"Deve retornar o valor esperado quando {func_name} é chamada com entrada válida",
                "coverage": 85,
                "scenario": "happy_path",
                "target_function": func_name
            })
            
            # Teste de casos extremos
            test_cases.append({
                "name": f"{prefix}handle_edge_cases_when_{func_name}_receives_boundary_values",
                "description": f"Deve tratar casos extremos quando {func_name} recebe valores limítrofes",
                "coverage": 80,
                "scenario": "edge_cases",
                "target_function": func_name
            })
            
            # Teste de entradas inválidas
            test_cases.append({
                "name": f"{prefix}raise_appropriate_error_when_{func_name}_receives_invalid_input",
                "description": f"Deve lançar erro apropriado quando {func_name} recebe entrada inválida",
                "coverage": 75,
                "scenario": "error_handling",
                "target_function": func_name
            })
        
        # Se há dependências externas, gerar testes com mocks
        if code_analysis.get("has_external_dependencies", False):
            test_cases.append({
                "name": f"{prefix}work_correctly_with_mocked_dependencies",
                "description": "Deve funcionar corretamente com dependências mockadas",
                "coverage": 90,
                "scenario": "mocked_dependencies",
                "target_function": "main_function"
            })
        
        return test_cases
        
    def _determine_test_framework(self, requested_framework: TestFramework, language: CodeLanguage) -> TestFramework:
        """
        Determina o framework de teste a ser usado.
        
        Args:
            requested_framework: Framework solicitado
            language: Linguagem de programação
            
        Returns:
            TestFramework: Framework a ser usado
        """
        if requested_framework != TestFramework.AUTO:
            return requested_framework
            
        # Mapear linguagem para framework padrão
        language_framework_map = {
            CodeLanguage.PYTHON: TestFramework.PYTEST,
            CodeLanguage.JAVASCRIPT: TestFramework.JEST,
            CodeLanguage.JAVA: TestFramework.JUNIT,
            CodeLanguage.CSHARP: TestFramework.NUNIT
        }
        
        return language_framework_map.get(language, TestFramework.PYTEST)
        
    def _generate_test_code(self, test_case: Dict[str, Any], framework: TestFramework, language: CodeLanguage) -> str:
        """
        Gera o código do teste.
        
        Args:
            test_case: Dados do caso de teste
            framework: Framework de teste
            language: Linguagem de programação
            
        Returns:
            str: Código do teste
        """
        # Mock implementation - em produção, usar LLM
        if language == CodeLanguage.PYTHON and framework == TestFramework.PYTEST:
            return f'''
import pytest
from my_module import my_function

def {test_case["name"]}():
    \"\"\"
    {test_case["description"]}
    \"\"\"
    # Arrange
    input_data = "test_input"
    expected_result = "expected_output"
    
    # Act
    result = my_function(input_data)
    
    # Assert
    assert result == expected_result
'''
        
        elif language == CodeLanguage.JAVASCRIPT and framework == TestFramework.JEST:
            return f'''
const {{ myFunction }} = require('./my-module');

describe('My Function Tests', () => {{
    test('{test_case["name"]}', () => {{
        // Arrange
        const inputData = 'test_input';
        const expectedResult = 'expected_output';
        
        // Act
        const result = myFunction(inputData);
        
        // Assert
        expect(result).toBe(expectedResult);
    }});
}});
'''
        
        # Código genérico para outros casos
        return f"// Teste: {test_case['name']}\n// {test_case['description']}\n// TODO: Implementar teste específico"
        
    def _get_test_dependencies(self, framework: TestFramework) -> List[str]:
        """
        Obtém as dependências necessárias para o framework de teste.
        
        Args:
            framework: Framework de teste
            
        Returns:
            List[str]: Lista de dependências
        """
        dependencies_map = {
            TestFramework.PYTEST: ["pytest", "pytest-cov"],
            TestFramework.UNITTEST: [],  # Biblioteca padrão
            TestFramework.JEST: ["jest", "@types/jest"],
            TestFramework.JUNIT: ["junit", "mockito"],
            TestFramework.NUNIT: ["NUnit", "Moq"]
        }
        
        return dependencies_map.get(framework, [])
