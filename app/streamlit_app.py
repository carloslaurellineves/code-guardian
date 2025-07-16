"""
Aplicação principal do Streamlit para CodeGuardian.

Este módulo configura a aplicação Streamlit com navegação multipáginas
e inicializa os componentes necessários para o funcionamento da interface.
"""

import streamlit as st
import sys
from pathlib import Path

# Adicionar diretório raiz ao path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from app.pages.home import HomePage
from app.pages.story_creator import StoryCreatorPage
from app.pages.code_tester import CodeTesterPage
from app.pages.code_fixer import CodeFixerPage
from app.utils.sidebar import create_sidebar
from app.utils.session_state import initialize_session_state


def main():
    """
    Função principal da aplicação Streamlit.
    
    Configura a navegação entre páginas e inicializa o estado da sessão.
    """
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
