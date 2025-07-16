"""
Utilitários para criar e gerenciar a sidebar da aplicação Streamlit.

Este módulo contém funções para criar a navegação lateral
e outros componentes da sidebar.
"""

import streamlit as st
from pathlib import Path
import sys

# Adicionar diretório raiz ao path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))


def create_sidebar() -> str:
    """
    Cria a sidebar com navegação e informações da aplicação.
    
    Returns:
        str: Nome da página selecionada
    """
    with st.sidebar:
        # Logo e título
        st.markdown("# 🛡️ CodeGuardian")
        st.markdown("*Uma aplicação do COE de Qualidade de Software*")
        
        st.markdown("---")
        
        # Navegação principal
        st.markdown("## 📋 Navegação")
        
        pages = [
            "🏠 Home",
            "🧱 Story Creator", 
            "🧪 Code Tester",
            "🛠️ Code Fixer"
        ]
        
        # Usar selectbox para navegação
        selected_page = st.selectbox(
            "Escolha uma página:",
            pages,
            key="page_selector"
        )
        
        st.markdown("---")
        
        # Informações da aplicação
        st.markdown("## ℹ️ Informações")
        
        with st.expander("Sobre o CodeGuardian"):
            st.markdown("""
            **CodeGuardian** é uma aplicação corporativa baseada em 
            Inteligência Artificial Generativa desenvolvida para apoiar, 
            padronizar e escalar práticas de qualidade de software.
            
            **Funcionalidades:**
            - 🧱 **Story Creator**: Geração de histórias Gherkin
            - 🧪 **Code Tester**: Geração de testes unitários
            - 🛠️ **Code Fixer**: Correção de bugs
            """)
        
        with st.expander("Tecnologias"):
            st.markdown("""
            - **Frontend**: Streamlit
            - **Backend**: FastAPI + Python
            - **IA**: Azure OpenAI
            - **Orquestração**: LangChain + LangGraph
            - **Repositório**: GitLab
            """)
        
        # Status da API
        st.markdown("## 🔌 Status")
        if st.button("Verificar API", key="check_api"):
            check_api_status()
        
        # Footer
        st.markdown("---")
        st.markdown("🏢 **Governança de Tecnologia**")
        st.markdown("*Time de Qualidade de Software*")
        
        return selected_page


def check_api_status():
    """
    Verifica o status da API do backend.
    """
    try:
        import requests
        response = requests.get("http://localhost:8000/api/v1/health", timeout=5)
        if response.status_code == 200:
            st.success("✅ API conectada")
        else:
            st.error(f"❌ API retornou código {response.status_code}")
    except requests.exceptions.ConnectionError:
        st.error("❌ Não foi possível conectar à API")
        st.info("💡 Certifique-se de que a API está rodando em http://localhost:8000")
    except Exception as e:
        st.error(f"❌ Erro ao verificar API: {str(e)}")
