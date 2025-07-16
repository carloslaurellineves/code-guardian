"""
Página Code Tester do CodeGuardian usando Streamlit.

Esta página permite ao usuário gerar testes unitários
a partir do código-fonte inserido ou enviado.
"""

import streamlit as st
from pathlib import Path
import sys
import requests

# Adicionar diretório raiz ao path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from app.pages.base_page import BasePage
from app.utils.session_state import get_session_value, set_session_value


class CodeTesterPage(BasePage):
    """
    Classe representando a página Code Tester.
    """
    
    def __init__(self):
        super().__init__("Code Tester", "🧪")
        self.api_base_url = get_session_value("api_base_url", "http://localhost:8000/api/v1")
    
    def render(self):
        """
        Renderiza a página Code Tester no Streamlit.
        """
        st.title("🧪 Code Tester")
        
        # Explicação da funcionalidade
        st.markdown("## Geração de Testes Unitários")
        st.info(
            """
            Esta ferramenta gera testes unitários a partir do código-fonte fornecido.
            """
        )
        
        # Instruções de uso
        with st.expander("📖 Como usar"):
            st.markdown("""
            1. **Escolha o método de entrada**: Cole o código, envie um arquivo ou forneça uma URL do GitLab.
            2. **Clique em Gerar**: O agente criará testes unitários baseados no código fornecido.
            3. **Revise e ajuste**: Valide se os testes gerados atendem suas expectativas.
            """)
        
        # Upload de arquivo
        uploaded_file = st.file_uploader("Faça upload do arquivo de código", type=["py", "js"])
        set_session_value("uploaded_file", uploaded_file)

        # Entrada de código manual ou URL
        code_input_method = st.radio(
            "Escolha o método de entrada:",
            ("text", "url"),
            index=0,
            format_func=lambda x: "Texto Manual" if x == "text" else "URL GitLab"
        )
        set_session_value("code_input_method", code_input_method)
        
        # Input de código manual
        if code_input_method == "text":
            code_input = st.text_area(
                "Insira o código:",
                height=200,
                placeholder="Cole aqui o código-fonte para gerar testes unitários"
            )
            set_session_value("code_input", code_input)
        
        # URL do GitLab
        if code_input_method == "url":
            gitlab_url = st.text_input(
                "Informe a URL do repositório GitLab:",
                value=get_session_value("gitlab_url", "")
            )
            set_session_value("gitlab_url", gitlab_url)
        
        # Botão para gerar testes
        if st.button("🚀 Gerar Testes"):
            if code_input_method == "text" and code_input.strip():
                self._generate_tests(code=code_input)
            elif code_input_method == "url" and gitlab_url.strip():
                self._generate_tests(gitlab_url=gitlab_url)
            elif uploaded_file is not None:
                self._generate_tests(file=uploaded_file)
            else:
                st.error("❌ Forneça o código, faça upload de um arquivo ou informe a URL.")
        
        # Área de resultados
        self._display_results()
    
    def _generate_tests(self, code=None, gitlab_url=None, file=None):
        """
        Gera testes unitários usando a API do backend.
        
        Args:
            code: Código fonte para gerar testes (opcional)
            gitlab_url: URL do repositório GitLab (opcional)
            file: Arquivo de código para gerar testes (opcional)
        """
        set_session_value("tests_loading", True)
        
        with st.spinner("⚙️ Gerando testes... Por favor, aguarde."):
            try:
                if file:
                    # Handle file upload
                    files = {"file": (file.name, file.getvalue())}
                    response = requests.post(
                        f"{self.api_base_url}/code/tests/generate", files=files
                    )
                else:
                    # Use code or URL
                    payload = {"code": code, "gitlab_url": gitlab_url}
                    response = requests.post(
                        f"{self.api_base_url}/code/tests/generate", json=payload
                    )
                
                if response.status_code == 200:
                    tests = response.json()
                    set_session_value("generated_tests", tests)
                    st.success("✅ Testes gerados com sucesso!")
                else:
                    st.error(f"❌ Erro na API: {response.status_code} - {response.text}")
            except requests.exceptions.ConnectionError:
                st.error("❌ Não foi possível conectar à API. Verifique se o backend está rodando.")
            except Exception as e:
                st.error(f"❌ Erro inesperado: {str(e)}")
        
        set_session_value("tests_loading", False)
    
    def _display_results(self):
        """
        Exibe os resultados dos testes gerados.
        """
        tests = get_session_value("generated_tests")
        
        if tests:
            st.markdown("## 🧪 Testes Gerados")
            
            for i, test in enumerate(tests.get("tests", []), 1):
                with st.expander(f"Teste {i}"):
                    st.code(test, language="python")

            # Botão para limpar resultados
            if st.button("🗑️ Limpar Resultados", key="clear_test_results"):
                set_session_value("generated_tests", None)
                st.experimental_rerun()
