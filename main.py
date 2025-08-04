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
        log_level="info",
        timeout_keep_alive=180  # 3 minutos para operações longas de LLM
    )


def start_frontend():
    """
    Inicia o frontend Streamlit.
    """
    print("🎨 Iniciando Code Guardian Frontend...")
    
    try:
        # Verificar se o arquivo do Streamlit existe
        streamlit_app_path = Path(__file__).parent / "app" / "streamlit_app.py"
        if not streamlit_app_path.exists():
            print("❌ Arquivo streamlit_app.py não encontrado")
            return
        
        # Determinar o endereço baseado no sistema operacional
        server_address = "localhost" if os.name == "nt" else "0.0.0.0"
        
        print(f"🌐 Iniciando servidor em http://{server_address}:8501")
        
        # Iniciar Streamlit
        import subprocess
        
        # Comando com parâmetros compatíveis com Windows e Streamlit atual
        cmd = [
            sys.executable, "-m", "streamlit", "run", 
            str(streamlit_app_path),
            "--server.port", "8501",
            "--server.address", server_address
        ]
        
        print(f"🔧 Executando comando: {' '.join(cmd)}")
        
        # Executar o comando
        result = subprocess.run(cmd, cwd=Path(__file__).parent)
        
        if result.returncode != 0:
            print(f"❌ Processo terminou com código de saída: {result.returncode}")
        
    except Exception as e:
        print(f"❌ Erro ao inicializar frontend: {e}")
        print("💡 Tente executar manualmente: streamlit run app/streamlit_app.py")


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
   python main.py api      - Inicia a API FastAPI (porta 8000)
   python main.py frontend - Inicia o frontend Streamlit (http://localhost:8501)
   python main.py test     - Executa os testes unitários
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
