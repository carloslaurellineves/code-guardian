#!/usr/bin/env python3
"""
Arquivo de teste para validar a correção da geração de testes unitários.

Este script testa se a funcionalidade CodeTester está gerando testes válidos 
baseados no código fornecido, ao invés de usar templates genéricos.
"""

import asyncio
from datetime import datetime
from typing import List, Optional

from schemas.code_schemas import CodeRequest, InputType, CodeLanguage, TestFramework
from agents.test_generator_agent import TestGeneratorAgent

# Código de exemplo que será testado (mesmo do problema relatado)
EXAMPLE_CODE = """
from datetime import datetime
from typing import List, Optional

class Transaction:
    def __init__(self, description: str, amount: float, date: Optional[datetime] = None):
        self.description = description
        self.amount = amount
        self.date = date or datetime.now()

    def __repr__(self):
        return f"<Transaction: {self.description} - R${self.amount:.2f} em {self.date.strftime('%Y-%m-%d')}>"

class Wallet:
    def __init__(self, owner: str):
        self.owner = owner
        self.transactions: List[Transaction] = []

    def add_transaction(self, transaction: Transaction) -> None:
        if transaction.amount == 0:
            raise ValueError("O valor da transação não pode ser zero.")
        self.transactions.append(transaction)

    def get_balance(self) -> float:
        return sum(t.amount for t in self.transactions)

    def get_statement(self) -> List[str]:
        return [str(t) for t in self.transactions]
"""

async def test_code_generator():
    """Testa a geração de testes unitários com a correção aplicada."""
    print("🧪 Testando a geração de testes unitários corrigida...")
    print("=" * 60)
    
    # Criar agente gerador de testes
    agent = TestGeneratorAgent()
    
    # Criar requisição de teste
    request = CodeRequest(
        input_type=InputType.DIRECT,
        code_content=EXAMPLE_CODE,
        language=CodeLanguage.PYTHON,
        test_framework=TestFramework.PYTEST
    )
    
    try:
        # Criar análise mock para o teste
        from schemas.code_schemas import CodeAnalysis
        mock_analysis = CodeAnalysis(
            complexity_score=75,
            maintainability_index=80,
            test_coverage_potential=85,
            code_smells=["Função muito longa", "Falta de documentação"],
            suggestions=["Dividir função em funções menores", "Adicionar docstrings"]
        )
        
        # Gerar testes usando o método fallback (simulando erro do LLM)
        tests = await agent._generate_tests_fallback(EXAMPLE_CODE, request, mock_analysis)
        analysis = mock_analysis
        
        print(f"✅ Geração concluída com sucesso!")
        print(f"📊 Total de testes gerados: {len(tests)}")
        print(f"📈 Análise de código: {analysis}")
        print("-" * 60)
        
        # Verificar se os testes foram gerados corretamente
        for i, test in enumerate(tests, 1):
            print(f"\n🧪 Teste {i}: {test.test_name}")
            print(f"📝 Descrição: {test.description}")
            print(f"🎯 Framework: {test.framework}")
            print(f"📈 Cobertura estimada: {test.coverage_estimation}%")
            print(f"📦 Dependências: {', '.join(test.dependencies)}")
            print("\n🔧 Código do teste:")
            print("-" * 40)
            print(test.test_code)
            print("-" * 40)
        
        # Validar se os testes não contêm referências genéricas
        generic_references = ["my_function", "my_module", "example_function"]
        valid_tests = 0
        
        for test in tests:
            has_generic_ref = any(ref in test.test_code for ref in generic_references)
            if not has_generic_ref:
                valid_tests += 1
            else:
                print(f"⚠️  Teste '{test.test_name}' ainda contém referências genéricas!")
        
        print(f"\n📊 Resultados da validação:")
        print(f"✅ Testes válidos: {valid_tests}/{len(tests)}")
        print(f"❌ Testes com referências genéricas: {len(tests) - valid_tests}/{len(tests)}")
        
        if valid_tests == len(tests):
            print("\n🎉 SUCESSO! Todos os testes foram gerados corretamente!")
            print("✅ O problema foi corrigido - os testes agora usam os nomes reais das classes e métodos.")
        else:
            print("\n⚠️  ATENÇÃO! Ainda existem testes com referências genéricas.")
            print("❌ A correção precisa de ajustes adicionais.")
            
    except Exception as e:
        print(f"❌ Erro durante a geração de testes: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_code_generator())
