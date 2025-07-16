"""
Página Code Fixer do CodeGuardian usando Streamlit.

Esta página permite ao usuário identificar e corrigir bugs
a partir da mensagem de erro e do código relevante.
"""

import streamlit as st
from pathlib import Path
import sys
import requests

# Adicionar diretório raiz ao path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from app.utils.session_state import get_session_value, set_session_value


class CodeFixerPage:
    """
    Classe representando a página Code Fixer.
    """
    
    def __init__(self):
        self.api_base_url = get_session_value("api_base_url", "http://localhost:8000/api/v1")

    def render(self):
        """
        Renderiza a página Code Fixer no Streamlit.
        """
        st.title("🛠️ Code Fixer")
        
        # Explicação da funcionalidade
        st.markdown("## Identificação e Correção de Bugs")
        st.info(
            """
            Esta ferramenta ajuda a identificar e corrigir bugs de código com base
            na descrição do erro e no trecho de código fornecido.
            """
        )
        
        # Instruções de uso
        with st.expander("📖 Como usar"):
            st.markdown("""
            1. **Descreva a mensagem de erro e o código problemático**: Informe detalhes claros.
            2. **Clique em Corrigir**: O agente analisará o código e sugerirá correções.
            3. **Revise e ajuste**: Valide se as correções atendem suas expectativas.
            """)

        # Separador
        st.markdown("---")
        
        # Entrada de dados
        st.markdown("## 📝 Descrição do Bug e Código")

        # Mensagem de erro
        error_message = st.text_area(
            "Informe a mensagem de erro:",
            height=80,
            placeholder="Exemplo: NameError: name 'variavel' is not defined"
        )
        set_session_value("error_message", error_message)

        # Código problemático
        bug_code = st.text_area(
            "Insira o código problemático:",
            height=200,
            placeholder="Cole aqui o trecho de código que gerou o bug"
        )
        set_session_value("bug_code", bug_code)
        
        # Botão para corrigir código
        if st.button("🚀 Corrigir Código"):
            if error_message.strip() and bug_code.strip():
                self._fix_code(error_message, bug_code)
            else:
                st.error("❌ Informe tanto a mensagem de erro quanto o código problemático.")
        
        # Área de resultados
        self._display_results()
    
    def _fix_code(self, error_message: str, bug_code: str):
        """
        Corrige o código usando a API do backend.
        
        Args:
            error_message: Mensagem de erro fornecida pelo usuário
            bug_code: Código fonte com o bug
        """
        set_session_value("fix_loading", True)
        
        with st.spinner("🔧 Corrigindo código... Por favor, aguarde."):
            try:
                payload = {
                    "error_message": error_message,
                    "code": bug_code
                }
                response = requests.post(
                    f"{self.api_base_url}/fix/bugs",
                    json=payload
                )
                
                if response.status_code == 200:
                    fixed_code = response.json().get("fixed_code", "")
                    set_session_value("fixed_code", fixed_code)
                    st.success("✅ Código corrigido com sucesso!")
                else:
                    st.error(f"❌ Erro na API: {response.status_code} - {response.text}")
            except requests.exceptions.ConnectionError:
                st.error("❌ Não foi possível conectar à API. Verifique se o backend está rodando.")
            except Exception as e:
                st.error(f"❌ Erro inesperado: {str(e)}")
        
        set_session_value("fix_loading", False)
    
    def _display_results(self):
        """
        Exibe o código corrigido.
        """
        fixed_code = get_session_value("fixed_code")

        if fixed_code:
            st.markdown("## 🔧 Código Corrigido")
            st.code(fixed_code, language="python")

            # Botão para limpar resultados
            if st.button("🗑️ Limpar Resultados", key="clear_fix_results"):
                set_session_value("fixed_code", None)
                st.experimental_rerun()
