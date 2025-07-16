"""
Utilitários para gerenciar o estado da sessão do Streamlit.

Este módulo contém funções para inicializar e gerenciar
o estado da sessão entre as páginas da aplicação.
"""

import streamlit as st
from typing import Any, Dict


def initialize_session_state():
    """
    Inicializa o estado da sessão com valores padrão.
    
    Define chaves essenciais para o funcionamento da aplicação
    caso ainda não existam no session_state.
    """
    
    # Configurações gerais
    if "api_base_url" not in st.session_state:
        st.session_state.api_base_url = "http://localhost:8000/api/v1"
    
    if "current_page" not in st.session_state:
        st.session_state.current_page = "🏠 Home"
    
    # Estados para Story Creator
    if "story_context" not in st.session_state:
        st.session_state.story_context = ""
    
    if "generated_stories" not in st.session_state:
        st.session_state.generated_stories = None
    
    if "story_loading" not in st.session_state:
        st.session_state.story_loading = False
    
    # Estados para Code Tester
    if "code_input" not in st.session_state:
        st.session_state.code_input = ""
    
    if "code_input_method" not in st.session_state:
        st.session_state.code_input_method = "text"
    
    if "uploaded_file" not in st.session_state:
        st.session_state.uploaded_file = None
    
    if "gitlab_url" not in st.session_state:
        st.session_state.gitlab_url = ""
    
    if "generated_tests" not in st.session_state:
        st.session_state.generated_tests = None
    
    if "tests_loading" not in st.session_state:
        st.session_state.tests_loading = False
    
    # Estados para Code Fixer
    if "bug_code" not in st.session_state:
        st.session_state.bug_code = ""
    
    if "error_message" not in st.session_state:
        st.session_state.error_message = ""
    
    if "fixed_code" not in st.session_state:
        st.session_state.fixed_code = None
    
    if "fix_loading" not in st.session_state:
        st.session_state.fix_loading = False
    
    # Estados para resultados e cache
    if "last_operation" not in st.session_state:
        st.session_state.last_operation = None
    
    if "operation_history" not in st.session_state:
        st.session_state.operation_history = []


def get_session_value(key: str, default: Any = None) -> Any:
    """
    Obtém um valor do estado da sessão.
    
    Args:
        key: Chave do valor desejado
        default: Valor padrão caso a chave não exista
        
    Returns:
        Valor armazenado na sessão ou valor padrão
    """
    return st.session_state.get(key, default)


def set_session_value(key: str, value: Any):
    """
    Define um valor no estado da sessão.
    
    Args:
        key: Chave para armazenar o valor
        value: Valor a ser armazenado
    """
    st.session_state[key] = value


def clear_session_data(keys: list = None):
    """
    Limpa dados específicos da sessão.
    
    Args:
        keys: Lista de chaves a serem limpas. Se None, limpa dados de resultados.
    """
    if keys is None:
        keys = [
            "generated_stories",
            "generated_tests", 
            "fixed_code",
            "last_operation"
        ]
    
    for key in keys:
        if key in st.session_state:
            del st.session_state[key]


def add_to_history(operation: str, result: Dict[str, Any]):
    """
    Adiciona uma operação ao histórico da sessão.
    
    Args:
        operation: Tipo de operação realizada
        result: Resultado da operação
    """
    if "operation_history" not in st.session_state:
        st.session_state.operation_history = []
    
    history_entry = {
        "timestamp": st.session_state.get("current_time", ""),
        "operation": operation,
        "result": result
    }
    
    st.session_state.operation_history.append(history_entry)
    
    # Manter apenas os últimos 10 registros
    if len(st.session_state.operation_history) > 10:
        st.session_state.operation_history = st.session_state.operation_history[-10:]


def get_operation_history() -> list:
    """
    Obtém o histórico de operações da sessão.
    
    Returns:
        Lista com histórico de operações
    """
    return st.session_state.get("operation_history", [])
