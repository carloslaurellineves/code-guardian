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

from app.views.base_page import BasePage
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
            Esta ferramenta gera testes unitários automáticos a partir do código-fonte fornecido.
            Escolha um dos três métodos de entrada e deixe a IA criar testes abrangentes para você.
            """
        )
        
        # Instruções de uso
        with st.expander("📜 Como usar"):
            st.markdown("""
            1. **Selecione o método de entrada**: Escolha entre inserção manual, upload de arquivo ou URL do GitLab
            2. **Forneça o código**: Preencha o campo correspondente à sua escolha
            3. **Gere os testes**: Clique no botão para que a IA analise e crie testes unitários
            4. **Revise os resultados**: Analise os testes gerados e adapte conforme necessário
            
            **📝 Formatos suportados**: Python (.py), JavaScript (.js), TypeScript (.ts), e outros
            """)
        
        # Separador
        st.markdown("---")
        
        # Seleção do método de entrada
        st.markdown("## 📝 Método de Entrada do Código")
        
        # Opções mutuamente exclusivas
        input_method = st.selectbox(
            "Selecione como você deseja fornecer o código:",
            options=["manual", "upload", "gitlab"],
            format_func=lambda x: {
                "manual": "📝 Inserir código manualmente",
                "upload": "📁 Fazer upload de arquivo",
                "gitlab": "🔗 Inserir URL do GitLab"
            }[x],
            index=0,
            key="input_method_selector"
        )
        
        # Armazenar método selecionado
        set_session_value("selected_input_method", input_method)
        
        # Variáveis para validação
        input_valid = False
        input_content = None
        
        # Renderizar interface baseada na seleção
        if input_method == "manual":
            input_content, input_valid = self._render_manual_input()
        elif input_method == "upload":
            input_content, input_valid = self._render_file_upload()
        elif input_method == "gitlab":
            input_content, input_valid = self._render_gitlab_input()
        
        # Separador
        st.markdown("---")
        
        # Botão de geração (centralizado)
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            generate_button = st.button(
                "🚀 Gerar Testes Unitários",
                disabled=not input_valid,
                key="generate_tests_btn",
                help="Clique para gerar testes unitários baseados no código fornecido" if input_valid else "Forneça o código antes de continuar"
            )
        
        # Processar geração quando botão for clicado
        if generate_button and input_valid:
            self._process_test_generation(input_method, input_content)
        
        # Área de resultados
        self._display_results()
    
    def _render_manual_input(self):
        """
        Renderiza o campo de entrada manual e valida a entrada.

        Returns:
            Tuple[str, bool]: Conteúdo do texto e se é válido
        """
        code_input = st.text_area(
            "Insira o código manualmente:",
            height=200,
            placeholder="Cole aqui o código-fonte"
        )
        is_valid = bool(code_input.strip())
        
        if not is_valid:
            st.warning("⚠️ Por favor, insira o código manual antes de prosseguir.")

        return code_input, is_valid

    def _render_file_upload(self):
        """
        Renderiza o campo de upload de arquivo e valida a entrada.

        Returns:
            Tuple[File, bool]: Arquivo carregado e se é válido
        """
        uploaded_file = st.file_uploader(
            "Faça upload de um arquivo de código:",
            type=["py", "js", "ts"]
        )
        is_valid = uploaded_file is not None

        if not is_valid:
            st.warning("⚠️ Por favor, faça upload de um arquivo antes de prosseguir.")

        return uploaded_file, is_valid

    def _render_gitlab_input(self):
        """
        Renderiza o campo de entrada para a URL do GitLab e valida a entrada.

        Returns:
            Tuple[str, bool]: URL do GitLab e se é válido
        """
        gitlab_url = st.text_input(
            "Insira a URL do repositório GitLab:",
            placeholder="https://gitlab.com/user/repo"
        )
        is_valid = bool(gitlab_url.strip())

        if not is_valid:
            st.warning("⚠️ Por favor, insira uma URL válida do GitLab antes de prosseguir.")

        return gitlab_url, is_valid

    def _process_test_generation(self, method, content):
        """
        Processa a geração de testes baseada no método de entrada.

        Args:
            method (str): Método de entrada selecionado
            content (Union[str, File]): Conteúdo do texto, arquivo ou URL
        """
        if method == "manual":
            self._generate_tests(code=content)
        elif method == "upload":
            self._generate_tests(file=content)
        elif method == "gitlab":
            self._generate_tests(gitlab_url=content)

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
                # Mock para desenvolvimento/demonstração
                self._generate_mock_tests(method)
            except Exception as e:
                st.error(f"❌ Erro inesperado: {str(e)}")
        
        set_session_value("tests_loading", False)

    def _generate_mock_tests(self, method):
        """
        Gera testes mockados para desenvolvimento/demonstração.
        
        Args:
            method (str): Método de entrada usado
        """
        # Template de teste unittest
        unittest_test = '''import unittest
from unittest.mock import patch, MagicMock

class TestExampleFunction(unittest.TestCase):
    
    def test_example_function_success(self):
        """Testa o comportamento normal da funcao."""
        # Arrange
        input_data = "test_input"
        expected_output = "expected_result"
        
        # Act
        result = example_function(input_data)
        
        # Assert
        self.assertEqual(result, expected_output)
    
    def test_example_function_edge_case(self):
        """Testa casos extremos da funcao."""
        # Arrange
        input_data = ""
        
        # Act & Assert
        with self.assertRaises(ValueError):
            example_function(input_data)

if __name__ == '__main__':
    unittest.main()'''
        
        # Template de teste pytest
        pytest_test = '''import pytest
from unittest.mock import Mock, patch

@pytest.fixture
def sample_data():
    """Fixture para dados de teste."""
    return {"key": "value", "numbers": [1, 2, 3]}

def test_another_function(sample_data):
    """Testa another_function com dados de exemplo."""
    # Arrange
    expected = True
    
    # Act
    result = another_function(sample_data)
    
    # Assert
    assert result == expected

@patch('module.external_service')
def test_function_with_external_dependency(mock_service):
    """Testa funcao com dependencia externa."""
    # Arrange
    mock_service.return_value = "mocked_response"
    
    # Act
    result = function_with_dependency()
    
    # Assert
    assert result == "mocked_response"
    mock_service.assert_called_once()'''
        
        mock_tests = {
            "tests": [unittest_test, pytest_test],
            "method_used": method,
            "total_tests": 2
        }
        
        set_session_value("generated_tests", mock_tests)
        st.info("💡 Usando testes mockados para demonstração")
    
    def _display_results(self):
        """
        Exibe os resultados dos testes gerados.
        """
        tests = get_session_value("generated_tests")
        
        if not tests:
            return
        
        # Cabeçalho dos resultados
        st.markdown("## 🧪 Testes Unitários Gerados")
        
        # Informações sobre os testes
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="📊 Total de Testes", 
                value=tests.get("total_tests", len(tests.get("tests", [])))
            )
        
        with col2:
            method_labels = {
                "manual": "Entrada Manual",
                "upload": "Upload de Arquivo", 
                "gitlab": "URL GitLab"
            }
            method_used = tests.get("method_used", "desconhecido")
            st.metric(
                label="📝 Método Usado", 
                value=method_labels.get(method_used, method_used.title())
            )
        
        with col3:
            st.metric(
                label="✨ Status", 
                value="Concluído"
            )
        
        st.markdown("---")
        
        # Exibir testes individuais
        for i, test in enumerate(tests.get("tests", []), 1):
            with st.expander(f"🧪 Teste Unitário {i}", expanded=i == 1):
                # Exibir código do teste
                st.code(test, language="python")
                
                # Botões de ação para cada teste
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button(f"📋 Copiar Teste {i}", key=f"copy_test_{i}"):
                        # Simulação de cópia (em uma implementação real seria com clipboard JS)
                        st.success(f"✅ Teste {i} copiado para área de transferência!")
                
                with col2:
                    if st.button(f"💾 Baixar Teste {i}", key=f"download_test_{i}"):
                        # Botão de download
                        st.download_button(
                            label=f"Download test_{i}.py",
                            data=test,
                            file_name=f"test_{i}.py",
                            mime="text/python",
                            key=f"download_btn_{i}"
                        )
        
        # Botões de ação globais
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            # Botão para baixar todos os testes
            all_tests = "\n\n# " + "="*50 + "\n\n".join(
                [f"# TESTE {i+1}\n\n{test}" for i, test in enumerate(tests.get("tests", []))]
            )
            st.download_button(
                label="💾 Baixar Todos os Testes",
                data=all_tests,
                file_name="generated_tests.py",
                mime="text/python",
                key="download_all_tests"
            )
        
        with col2:
            # Botão para gerar novos testes
            if st.button("🔄 Gerar Novos Testes", key="regenerate_tests"):
                set_session_value("generated_tests", None)
                st.rerun()
        
        with col3:
            # Botão para limpar resultados
            if st.button("🗑️ Limpar Resultados", key="clear_test_results"):
                set_session_value("generated_tests", None)
                st.rerun()
