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
                page_title="CodeGuardian",
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
        
        /* Oculta os nomes das páginas na sidebar */
        .css-1d391kg {
            display: none !important;
        }
        
        /* Oculta a navegação de páginas padrão do Streamlit */
        .css-1rs6os .css-17ziqus {
            display: none !important;
        }
        
        /* Oculta a lista de páginas na sidebar */
        .css-1lcbmhc .css-1d391kg {
            display: none !important;
        }
        
        /* Oculta os links de navegação das páginas */
        .sidebar .sidebar-content .css-1d391kg {
            display: none !important;
        }
        
        /* Oculta o menu de navegação automático das páginas */
        [data-testid="stSidebarNav"] {
            display: none !important;
        }
        
        /* Oculta a lista de páginas na sidebar */
        .css-1lcbmhc {
            display: none !important;
        }
        
        /* Oculta navegação automática do Streamlit - seletores mais específicos */
        .css-1lcbmhc.e1fqkh3o0 {
            display: none !important;
        }
        
        .css-1d391kg.e1fqkh3o1 {
            display: none !important;
        }
        
        /* Oculta seção de páginas na sidebar */
        .css-1lcbmhc.e1fqkh3o3 {
            display: none !important;
        }
        
        /* Oculta links de páginas específicos */
        .sidebar .element-container .css-1d391kg {
            display: none !important;
        }
        
        /* Oculta qualquer elemento com text-content dos nomes das páginas */
        .sidebar .element-container:has-text('streamlit app'),
        .sidebar .element-container:has-text('base page'),
        .sidebar .element-container:has-text('code fixer'),
        .sidebar .element-container:has-text('code tester'),
        .sidebar .element-container:has-text('home'),
        .sidebar .element-container:has-text('story creator') {
            display: none !important;
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
