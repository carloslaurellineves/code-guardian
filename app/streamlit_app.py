"""
Aplicação principal do Streamlit para CodeGuardian.

Este módulo configura a aplicação Streamlit com navegação multipáginas
e inicializa os componentes necessários para o funcionamento da interface.
"""

import streamlit as st
import sys
from pathlib import Path

# IMPORTANTE: Configurar identidade visual antes de qualquer outro comando Streamlit
st.set_page_config(
    page_title="CodeGuardian",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/your-repo/code-guardian',
        'Report a bug': 'https://github.com/your-repo/code-guardian/issues',
        'About': """
        # CodeGuardian 🛡️
        
        Uma aplicação AI-powered para:
        - Geração de User Stories
        - Criação de Testes Unitários
        - Correção de Bugs
        
        Desenvolvido com ❤️ usando Streamlit e LangChain
        """
    }
)

from app.config.streamlit_config import apply_custom_css

# Adicionar diretório raiz ao path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from app.views.home import HomePage
from app.views.story_creator import StoryCreatorPage
from app.views.code_tester import CodeTesterPage
from app.views.code_fixer import CodeFixerPage
from app.utils.sidebar import create_sidebar
from app.utils.session_state import initialize_session_state


def hide_streamlit_navigation():
    """
    Oculta a navegação automática do Streamlit via JavaScript.
    """
    hide_nav_script = """
    <script>
        // Oculta navegação automática do Streamlit
        var navElements = document.querySelectorAll('[data-testid="stSidebarNav"]');
        navElements.forEach(function(el) {
            el.style.display = 'none';
        });
        
        // Oculta links de páginas na sidebar
        var pageLinks = document.querySelectorAll('.css-1d391kg');
        pageLinks.forEach(function(el) {
            el.style.display = 'none';
        });
        
        // Oculta lista de páginas
        var pageList = document.querySelectorAll('.css-1lcbmhc');
        pageList.forEach(function(el) {
            el.style.display = 'none';
        });
    </script>
    """
    st.markdown(hide_nav_script, unsafe_allow_html=True)


def main():
    """
    Função principal da aplicação Streamlit.
    
    Configura a navegação entre páginas e inicializa o estado da sessão.
    """
    # Aplicar CSS customizado (identidade visual já foi configurada acima)
    apply_custom_css()
    
    # Ocultar navegação automática do Streamlit
    hide_streamlit_navigation()
    
    # Inicializar estado da sessão
    initialize_session_state()
    
    # Criar sidebar com navegação
    selected_page = create_sidebar()
    
    # Renderizar página selecionada
    if selected_page == "🏠 Home":
        home_page = HomePage()
        home_page.render()
    elif selected_page == "🧱 Story Creator":
        story_page = StoryCreatorPage()
        story_page.render()
    elif selected_page == "🧪 Code Tester":
        tester_page = CodeTesterPage()
        tester_page.render()
    elif selected_page == "🛠️ Code Fixer":
        fixer_page = CodeFixerPage()
        fixer_page.render()


if __name__ == "__main__":
    main()
