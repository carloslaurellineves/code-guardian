"""
Página Code Fixer do CodeGuardian usando Streamlit.

Esta página permite ao usuário identificar e corrigir bugs
a partir da mensagem de erro e do código relevante.
"""

import streamlit as st
from pathlib import Path
import sys
import requests
import base64

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
                
                if response.status_code in [200, 201]:
                    fixed_code = response.json().get("fixed_code", "")
                    set_session_value("fixed_code", fixed_code)
                    st.success("✅ Código corrigido com sucesso!")
                else:
                    st.error(f"❌ Erro na API: {response.status_code} - {response.text}")
            except requests.exceptions.ConnectionError:
                st.error("❌ Não foi possível conectar à API. Verifique se o backend está rodando.")
                # Mock para desenvolvimento
                self._generate_mock_fix(error_message, bug_code)
            except requests.exceptions.Timeout:
                st.error("⏱️ Timeout na requisição. Tente novamente.")
            except Exception as e:
                st.error(f"❌ Erro inesperado: {str(e)}")
        
        set_session_value("fix_loading", False)
    
    def _generate_mock_fix(self, error_message: str, bug_code: str):
        """
        Gera correções mockadas para desenvolvimento/demonstração.
        
        Args:
            error_message: Mensagem de erro fornecida
            bug_code: Código com bug fornecido
        """
        # Análise básica do tipo de erro para gerar correção apropriada
        error_lower = error_message.lower()
        
        if "nameerror" in error_lower or "not defined" in error_lower:
            # Erro de variável não definida
            fixed_code = self._fix_name_error(bug_code, error_message)
        elif "syntaxerror" in error_lower or "invalid syntax" in error_lower:
            # Erro de sintaxe
            fixed_code = self._fix_syntax_error(bug_code, error_message)
        elif "indentationerror" in error_lower or "unexpected indent" in error_lower:
            # Erro de indentação
            fixed_code = self._fix_indentation_error(bug_code, error_message)
        elif "typeerror" in error_lower:
            # Erro de tipo
            fixed_code = self._fix_type_error(bug_code, error_message)
        elif "indexerror" in error_lower or "list index out of range" in error_lower:
            # Erro de índice
            fixed_code = self._fix_index_error(bug_code, error_message)
        elif "keyerror" in error_lower:
            # Erro de chave
            fixed_code = self._fix_key_error(bug_code, error_message)
        elif "attributeerror" in error_lower:
            # Erro de atributo
            fixed_code = self._fix_attribute_error(bug_code, error_message)
        else:
            # Correção genérica
            fixed_code = self._fix_generic_error(bug_code, error_message)
        
        # Adicionar comentários explicativos
        fixed_code = self._add_explanation_comments(fixed_code, error_message)
        
        set_session_value("fixed_code", fixed_code)
        st.info("💡 Usando correção mockada para demonstração")
    
    def _fix_name_error(self, code: str, error: str) -> str:
        """Corrige erros de NameError."""
        return f'''# CORREÇÃO APLICADA: NameError
# Erro original: {error}

# Variáveis foram definidas antes do uso
resultado = 0
variavel = "valor_exemplo"
contador = 1

{code}

# Comentário: Certifique-se de que todas as variáveis estão definidas antes de serem usadas'''
    
    def _fix_syntax_error(self, code: str, error: str) -> str:
        """Corrige erros de sintaxe."""
        # Adiciona parênteses faltantes e corrige sintaxe básica
        fixed = code.replace("print ", "print(")
        if "print(" in fixed and not fixed.endswith(")"):
            fixed += ")"
        
        return f'''# CORREÇÃO APLICADA: SyntaxError
# Erro original: {error}

{fixed}

# Comentário: Sintaxe corrigida - parênteses adicionados onde necessário'''
    
    def _fix_indentation_error(self, code: str, error: str) -> str:
        """Corrige erros de indentação."""
        lines = code.split('\n')
        fixed_lines = []
        
        for line in lines:
            if line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                if any(keyword in line for keyword in ['if', 'for', 'while', 'def', 'class']):
                    fixed_lines.append(line)
                else:
                    fixed_lines.append('    ' + line)  # Adiciona indentação
            else:
                fixed_lines.append(line)
        
        return f'''# CORREÇÃO APLICADA: IndentationError
# Erro original: {error}

{"".join(fixed_lines)}

# Comentário: Indentação corrigida - use 4 espaços por nível'''
    
    def _fix_type_error(self, code: str, error: str) -> str:
        """Corrige erros de tipo."""
        return f'''# CORREÇÃO APLICADA: TypeError
# Erro original: {error}

# Conversões de tipo adicionadas
{code}

# Exemplo de correções comuns:
# str(numero) para converter número em string
# int(texto) para converter string em inteiro
# list(iteravel) para converter em lista

# Comentário: Verifique os tipos de dados antes de operações'''
    
    def _fix_index_error(self, code: str, error: str) -> str:
        """Corrige erros de índice."""
        return f'''# CORREÇÃO APLICADA: IndexError
# Erro original: {error}

# Verificação de índice adicionada
if len(lista) > 0:  # Verifica se a lista não está vazia
    {code}
else:
    print("Lista vazia ou índice inválido")

# Comentário: Sempre verifique o tamanho da lista antes de acessar índices'''
    
    def _fix_key_error(self, code: str, error: str) -> str:
        """Corrige erros de chave."""
        return f'''# CORREÇÃO APLICADA: KeyError
# Erro original: {error}

# Verificação de chave adicionada
if 'chave' in dicionario:  # Verifica se a chave existe
    {code}
else:
    print("Chave não encontrada no dicionário")

# Alternativa: usar dicionario.get('chave', 'valor_padrao')

# Comentário: Sempre verifique se a chave existe antes de acessá-la'''
    
    def _fix_attribute_error(self, code: str, error: str) -> str:
        """Corrige erros de atributo."""
        return f'''# CORREÇÃO APLICADA: AttributeError
# Erro original: {error}

# Verificação de atributo adicionada
if hasattr(objeto, 'atributo'):  # Verifica se o atributo existe
    {code}
else:
    print("Atributo não encontrado no objeto")

# Comentário: Use hasattr() para verificar se um atributo existe'''
    
    def _fix_generic_error(self, code: str, error: str) -> str:
        """Correção genérica para outros tipos de erro."""
        return f'''# CORREÇÃO SUGERIDA
# Erro original: {error}

# Código com tratamento de erro adicionado
try:
    {code}
except Exception as e:
    print(f"Erro capturado: {{e}}")
    # Adicione aqui o tratamento apropriado

# Comentário: Considere adicionar tratamento de exceções específico'''
    
    def _add_explanation_comments(self, code: str, error: str) -> str:
        """Adiciona comentários explicativos ao código corrigido."""
        explanation = f'''{code}

# === EXPLICAÇÃO DA CORREÇÃO ===
# Erro detectado: {error}
# 
# Correções aplicadas:
# 1. Verificações de segurança adicionadas
# 2. Tratamento de casos especiais implementado
# 3. Comentários explicativos incluídos
# 
# Dicas para evitar erros similares:
# - Sempre inicialize variáveis antes de usar
# - Verifique tipos de dados antes de operações
# - Use try/except para tratar exceções
# - Teste com diferentes cenários de entrada
'''
        return explanation
    
    def _generate_fixed_code_txt(self, fixed_code: str) -> str:
        """
        Gera o conteúdo em formato TXT do código corrigido.
        
        Args:
            fixed_code: Código corrigido
            
        Returns:
            str: Conteúdo formatado em texto
        """
        from datetime import datetime
        
        # Recuperar informações da sessão
        error_message = get_session_value("error_message", "Não especificado")
        bug_code = get_session_value("bug_code", "Não especificado")
        
        txt_content = []
        txt_content.append("=" * 80)
        txt_content.append("                   CÓDIGO CORRIGIDO - CODE GUARDIAN")
        txt_content.append("=" * 80)
        txt_content.append(f"Data de correção: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        txt_content.append("=" * 80)
        txt_content.append("")
        
        # Informações do bug original
        txt_content.append("🐛 INFORMAÇÕES DO BUG ORIGINAL")
        txt_content.append("-" * 50)
        txt_content.append(f"Mensagem de erro: {error_message}")
        txt_content.append("")
        txt_content.append("Código problemático:")
        bug_lines = bug_code.split('\n')
        for line in bug_lines:
            txt_content.append(f"  {line}")
        txt_content.append("")
        txt_content.append("=" * 80)
        txt_content.append("")
        
        # Código corrigido
        txt_content.append("🔧 CÓDIGO CORRIGIDO")
        txt_content.append("-" * 50)
        fixed_lines = fixed_code.split('\n')
        for line in fixed_lines:
            txt_content.append(line)
        txt_content.append("")
        txt_content.append("=" * 80)
        txt_content.append("")
        
        # Informações adicionais
        txt_content.append("📝 INFORMAÇÕES ADICIONAIS")
        txt_content.append("-" * 50)
        txt_content.append("Este arquivo contém a correção gerada pelo CodeGuardian.")
        txt_content.append("")
        txt_content.append("Próximos passos recomendados:")
        txt_content.append("1. Revise o código corrigido cuidadosamente")
        txt_content.append("2. Teste a solução em um ambiente seguro")
        txt_content.append("3. Implemente as correções em seu projeto")
        txt_content.append("4. Execute testes unitários para validar")
        txt_content.append("")
        txt_content.append("=" * 80)
        txt_content.append("")
        txt_content.append("Gerado pelo CodeGuardian - Code Fixer")
        txt_content.append("")
        
        return "\n".join(txt_content)

    def _display_results(self):
        """
        Exibe o código corrigido.
        """
        fixed_code = get_session_value("fixed_code")

        if fixed_code:
            st.markdown("## 🔧 Código Corrigido")
            st.code(fixed_code, language="python")
            
            # Separador
            st.markdown("---")
            
            # Botões de ação
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                # Botão para copiar código
                # Escape do código para JavaScript, preservando UTF-8
                code_escaped = fixed_code.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
                copy_button_id = 'copy-fixed-code-button'
                
                st.components.v1.html(
                    f"""
                    <button id='{copy_button_id}' style='
                        background-color: #0e1117;
                        color: white;
                        border: 1px solid #262730;
                        border-radius: 0.25rem;
                        padding: 0.25rem 0.75rem;
                        font-size: 14px;
                        cursor: pointer;
                        font-family: "Source Sans Pro", sans-serif;
                        width: 100%;
                    '>📋 Copiar Código</button>
                    <script>
                        document.getElementById('{copy_button_id}').onclick = function() {{
                            try {{
                                const fixedCode = "{code_escaped}";
                                navigator.clipboard.writeText(fixedCode).then(function() {{
                                    alert('✅ Código corrigido copiado para a área de transferência!');
                                }}).catch(function(err) {{
                                    console.error('Erro ao copiar:', err);
                                    alert('❌ Erro ao copiar o código. Tente novamente.');
                                }});
                            }} catch(e) {{
                                console.error('Erro:', e);
                                alert('❌ Erro ao processar o código.');
                            }}
                        }}
                    </script>
                    """,
                    height=40
                )
            
            with col2:
                # Botão para salvar em TXT
                if st.button("💾 Salvar em TXT", key="save_fixed_code_txt"):
                    txt_content = self._generate_fixed_code_txt(fixed_code)
                    st.download_button(
                        label="📥 Download codigo_corrigido.txt",
                        data=txt_content,
                        file_name="codigo_corrigido.txt",
                        mime="text/plain",
                        key="download_fixed_code_txt"
                    )
            
            with col3:
                # Botão para limpar resultados
                if st.button("🗑️ Limpar Resultados", key="clear_fix_results"):
                    set_session_value("fixed_code", None)
                    st.rerun()
