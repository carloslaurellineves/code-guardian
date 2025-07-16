"""
Configurações globais para o Streamlit.

Este módulo contém configurações globais que devem ser aplicadas
antes da inicialização da aplicação Streamlit.
"""

import streamlit as st


def configure_streamlit():
    """
    Configura a aplicação Streamlit com as configurações globais.
    
    Esta função deve ser chamada antes da inicialização de qualquer página
    para garantir que todas as configurações sejam aplicadas corretamente.
    """
    # Verifica se a configuração já foi aplicada
    if not hasattr(st.session_state, 'streamlit_configured'):
        try:
            st.set_page_config(
                page_title="Code Guardian",
                page_icon="🛡️",
                layout="wide",
                initial_sidebar_state="expanded",
                menu_items={
                    'Get Help': 'https://github.com/your-repo/code-guardian',
                    'Report a bug': 'https://github.com/your-repo/code-guardian/issues',
                    'About': """
                    # Code Guardian 🛡️
                    
                    Uma aplicação AI-powered para:
                    - Geração de User Stories
                    - Criação de Testes Unitários
                    - Correção de Bugs
                    
                    Desenvolvido com ❤️ usando Streamlit e LangChain
                    """
                }
            )
            st.session_state.streamlit_configured = True
        except st.errors.StreamlitAPIException:
            # Se a configuração já foi definida, apenas marca como configurada
            st.session_state.streamlit_configured = True


def apply_custom_css():
    """
    Aplica estilos CSS customizados para otimizar o layout wide mode.
    """
    custom_css = """
    <style>
        /* Otimizações para wide mode */
        .main .block-container {
            max-width: 100%;
            padding-left: 2rem;
            padding-right: 2rem;
        }
        
        /* Melhora o espaçamento dos elementos */
        .stButton > button {
            width: 100%;
        }
        
        /* Otimiza o layout das colunas */
        .col-container {
            display: flex;
            flex-direction: row;
            gap: 1rem;
        }
        
        /* Melhora a aparência dos expandables */
        .streamlit-expanderHeader {
            font-weight: bold;
        }
        
        /* Otimiza o sidebar */
        .sidebar .sidebar-content {
            padding-top: 1rem;
        }
        
        /* Melhora a aparência dos code blocks */
        .stCodeBlock {
            font-size: 0.9rem;
        }
        
        /* Responsividade para diferentes tamanhos de tela */
        @media (max-width: 768px) {
            .main .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }
        }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)


def ensure_wide_mode():
    """
    Garante que o wide mode esteja ativo em todas as páginas.
    
    Esta função deve ser chamada no início de cada página para
    garantir que a configuração esteja sempre aplicada.
    """
    configure_streamlit()
    apply_custom_css()
