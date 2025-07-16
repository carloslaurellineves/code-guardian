#!/usr/bin/env python3
"""
Script principal para inicialização da aplicação Code Guardian.

Este script serve como ponto de entrada principal para a aplicação
e pode ser usado para inicializar tanto a API quanto o frontend.
"""

import sys
import os
import argparse
import subprocess
from pathlib import Path

# Adicionar o diretório raiz ao Python path
sys.path.insert(0, str(Path(__file__).parent))

from utils.logging_config import setup_logging
from utils.helpers import validate_environment_variables


def start_api():
    """
    Inicia o servidor da API FastAPI.
    """
    print("🚀 Iniciando Code Guardian API...")
    
    # Configurar logging
    setup_logging()
    
    # Validar variáveis de ambiente (opcional)
    # required_vars = ['AZURE_OPENAI_KEY']
    # validation = validate_environment_variables(required_vars)
    # if not validation['valid']:
    #     print(f"❌ Variáveis de ambiente ausentes: {validation['missing_vars']}")
    #     print("⚠️  Continuando com configuração mock...")
    
    # Iniciar servidor
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


def start_frontend():
    """
    Inicia o frontend Streamlit.
    """
    print("🎨 Iniciando Code Guardian Frontend...")
    
    # TODO: Implementar inicialização do Streamlit
    # Por enquanto, apenas uma mensagem
    print("⚠️  Frontend Streamlit será implementado em fase posterior")
    print("📖 Para acessar a API, utilize: http://localhost:8000/docs")


def run_tests():
    """
    Executa os testes da aplicação.
    """
    print("🧪 Executando testes...")
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "-v"],
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        if result.stderr:
            print("Erros:")
            print(result.stderr)
            
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Erro ao executar testes: {e}")
        return False


def show_info():
    """
    Mostra informações sobre a aplicação.
    """
    print("""\n🛡️  Code Guardian - Aplicação de Qualidade de Software

📖 Descrição:
   Aplicação corporativa baseada em IA Generativa para apoiar
   práticas de qualidade de software no ciclo de desenvolvimento.

🎯 Funcionalidades:
   • Story Creator: Geração de histórias em formato Gherkin
   • Code Tester: Geração automatizada de testes unitários  
   • Code Fixer: Identificação e correção de bugs

🔧 Comandos disponíveis:
   python main.py api      - Inicia a API (porta 8000)
   python main.py frontend - Inicia o frontend Streamlit
   python main.py test     - Executa os testes
   python main.py info     - Mostra estas informações

🌐 Endpoints da API:
   • Health Check: GET /api/v1/health
   • Documentação: GET /docs
   • Histórias: POST /api/v1/stories/generate
   • Testes: POST /api/v1/code/tests/generate
   • Correção: POST /api/v1/fix/bugs

📚 Documentação completa disponível em /docs após iniciar a API.
""")


def main():
    """
    Função principal que processa argumentos e executa ações.
    """
    parser = argparse.ArgumentParser(
        description="Code Guardian - Aplicação de Qualidade de Software"
    )
    
    parser.add_argument(
        "command",
        choices=["api", "frontend", "test", "info"],
        help="Comando a ser executado"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Porta para o servidor API (padrão: 8000)"
    )
    
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host para o servidor API (padrão: 0.0.0.0)"
    )
    
    # Se nenhum argumento foi fornecido, mostrar info
    if len(sys.argv) == 1:
        show_info()
        return
    
    args = parser.parse_args()
    
    if args.command == "api":
        start_api()
    elif args.command == "frontend":
        start_frontend()
    elif args.command == "test":
        success = run_tests()
        sys.exit(0 if success else 1)
    elif args.command == "info":
        show_info()


if __name__ == "__main__":
    main()
