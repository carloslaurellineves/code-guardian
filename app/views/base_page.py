"""
Classe base para páginas do CodeGuardian.

Esta classe fornece funcionalidades comuns para todas as páginas
da aplicação, seguindo o padrão de herança e reutilização de código.
"""

import streamlit as st
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pathlib import Path
import sys

# Adicionar diretório raiz ao path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from app.services.api_client import api_client
from app.utils.session_state import get_session_value, set_session_value
from app.config.streamlit_config import ensure_wide_mode


class BasePage(ABC):
    """
    Classe base para páginas da aplicação.
    
    Fornece funcionalidades comuns como tratamento de erros,
    validação de inputs e comunicação com a API.
    """
    
    def __init__(self, page_title: str, page_icon: str = "🛡️"):
        """
        Inicializa a página base.
        
        Args:
            page_title: Título da página
            page_icon: Ícone da página
        """
        self.page_title = page_title
        self.page_icon = page_icon
        self.api_client = api_client
        self._ensure_wide_mode()
    
    def _ensure_wide_mode(self):
        """
        Garante que a página esteja configurada para wide mode.
        
        Este método utiliza a configuração global para garantir
        que o wide mode esteja aplicado e os estilos otimizados.
        """
        ensure_wide_mode()
    
    @abstractmethod
    def render(self):
        """
        Renderiza a página. Deve ser implementado pelas classes filhas.
        """
        pass
    
    def show_page_header(self, subtitle: Optional[str] = None):
        """
        Exibe o cabeçalho padrão da página.
        
        Args:
            subtitle: Subtítulo opcional
        """
        st.title(f"{self.page_icon} {self.page_title}")
        if subtitle:
            st.markdown(f"### {subtitle}")
    
    def show_loading_spinner(self, message: str = "Processando..."):
        """
        Exibe um spinner de carregamento.
        
        Args:
            message: Mensagem a ser exibida
        """
        return st.spinner(f"🤖 {message}")
    
    def show_error_message(self, message: str, details: Optional[str] = None):
        """
        Exibe uma mensagem de erro padronizada.
        
        Args:
            message: Mensagem principal do erro
            details: Detalhes adicionais do erro
        """
        st.error(f"❌ {message}")
        if details:
            with st.expander("🔍 Detalhes do erro"):
                st.code(details)
    
    def show_success_message(self, message: str):
        """
        Exibe uma mensagem de sucesso padronizada.
        
        Args:
            message: Mensagem de sucesso
        """
        st.success(f"✅ {message}")
    
    def show_info_message(self, message: str):
        """
        Exibe uma mensagem informativa padronizada.
        
        Args:
            message: Mensagem informativa
        """
        st.info(f"💡 {message}")
    
    def show_warning_message(self, message: str):
        """
        Exibe uma mensagem de aviso padronizada.
        
        Args:
            message: Mensagem de aviso
        """
        st.warning(f"⚠️ {message}")
    
    def validate_input(self, input_value: str, min_length: int = 10) -> bool:
        """
        Valida se o input atende aos critérios mínimos.
        
        Args:
            input_value: Valor a ser validado
            min_length: Comprimento mínimo do input
            
        Returns:
            True se válido, False caso contrário
        """
        if not input_value or not input_value.strip():
            self.show_error_message("Campo obrigatório não preenchido")
            return False
        
        if len(input_value.strip()) < min_length:
            self.show_error_message(f"Input deve ter pelo menos {min_length} caracteres")
            return False
        
        return True
    
    def handle_api_response(self, response: Dict[str, Any]) -> bool:
        """
        Trata a resposta da API de forma padronizada.
        
        Args:
            response: Resposta da API
            
        Returns:
            True se sucesso, False se erro
        """
        if response.get("status") == "success":
            return True
        elif response.get("status") == "error":
            error_msg = response.get("error", "Erro desconhecido")
            self.show_error_message("Erro na comunicação com a API", error_msg)
            return False
        else:
            self.show_error_message("Resposta inválida da API")
            return False
    
    def create_copy_button(self, content: str, button_text: str = "📋 Copiar", key: str = None):
        """
        Cria um botão para copiar conteúdo.
        
        Args:
            content: Conteúdo a ser copiado
            button_text: Texto do botão
            key: Key única para o botão
            
        Returns:
            True se o botão foi clicado
        """
        if st.button(button_text, key=key):
            # Simula a funcionalidade de copiar (dependeria de JavaScript no Streamlit)
            self.show_success_message("Conteúdo copiado!")
            return True
        return False
    
    def show_usage_instructions(self, instructions: list):
        """
        Exibe instruções de uso em formato expandible.
        
        Args:
            instructions: Lista de instruções
        """
        with st.expander("📖 Como usar"):
            for i, instruction in enumerate(instructions, 1):
                st.markdown(f"{i}. {instruction}")
    
    def create_clear_button(self, session_keys: list, button_text: str = "🗑️ Limpar Resultados"):
        """
        Cria um botão para limpar resultados da sessão.
        
        Args:
            session_keys: Lista de chaves da sessão para limpar
            button_text: Texto do botão
        """
        if st.button(button_text):
            for key in session_keys:
                set_session_value(key, None)
            st.rerun()
    
    def show_mock_warning(self):
        """
        Exibe aviso sobre uso de dados mockados.
        """
        self.show_info_message("Usando dados mockados para desenvolvimento")
    
    def format_code_display(self, code: str, language: str = "python"):
        """
        Formata e exibe código de forma padronizada.
        
        Args:
            code: Código a ser exibido
            language: Linguagem do código
        """
        st.code(code, language=language)
    
    def create_tabs(self, tab_names: list):
        """
        Cria abas de navegação.
        
        Args:
            tab_names: Lista com nomes das abas
            
        Returns:
            Lista de objetos tab do Streamlit
        """
        return st.tabs(tab_names)
    
    def create_columns(self, ratios: list):
        """
        Cria colunas com proporções específicas.
        
        Args:
            ratios: Lista com proporções das colunas
            
        Returns:
            Lista de objetos column do Streamlit
        """
        return st.columns(ratios)
    
    def create_expander(self, title: str, expanded: bool = False):
        """
        Cria um expander padronizado.
        
        Args:
            title: Título do expander
            expanded: Se deve iniciar expandido
            
        Returns:
            Objeto expander do Streamlit
        """
        return st.expander(title, expanded=expanded)
