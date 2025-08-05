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

        # Seleção de linguagem
        language_options = {
            "Python": "python",
            "JavaScript": "javascript",
            "TypeScript": "typescript",
            "Java": "java",
            "C#": "csharp",
            "Go": "go",
            "Rust": "rust",
            "PHP": "php"
        }
        
        selected_language = st.selectbox(
            "🔤 Selecione a linguagem do código:",
            options=list(language_options.keys()),
            index=0,
            help="Escolha a linguagem de programação do código com bug"
        )
        language_code = language_options[selected_language]
        set_session_value("selected_language", language_code)

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
            if error_message.strip() and bug_code.strip() and language_code:
                self._fix_code(error_message, bug_code, language_code)
            else:
                missing_fields = []
                if not error_message.strip():
                    missing_fields.append("mensagem de erro")
                if not bug_code.strip():
                    missing_fields.append("código com bug")
                if not language_code:
                    missing_fields.append("linguagem")
                
                st.error(f"❌ Campos obrigatórios faltantes: {', '.join(missing_fields)}")
        
        # Área de resultados
        self._display_results()
    
    def _fix_code(self, error_message: str, bug_code: str, language: str):
        """
        Corrige o código usando a API do backend.
        
        Args:
            error_message: Mensagem de erro fornecida pelo usuário
            bug_code: Código fonte com o bug
            language: Linguagem de programação
        """
        set_session_value("fix_loading", True)
        
        with st.spinner("🔧 Corrigindo código... Por favor, aguarde."):
            try:
                # Validação dos campos obrigatórios
                if not error_message.strip():
                    st.error("❌ Mensagem de erro é obrigatória")
                    return
                if not bug_code.strip():
                    st.error("❌ Código com bug é obrigatório")
                    return
                if not language:
                    st.error("❌ Linguagem é obrigatória")
                    return
                
                # Payload no formato correto esperado pela API
                payload = {
                    "code_with_bug": bug_code,
                    "error_description": error_message,
                    "language": language
                }
                
                st.write("**DEBUG - Fazendo requisição para:**", f"{self.api_base_url}/fix/bugs")
                st.write("**DEBUG - Payload:**")
                st.json(payload)
                
                response = requests.post(
                    f"{self.api_base_url}/fix/bugs",
                    json=payload,
                    timeout=30
                )
                
                st.write("**DEBUG - Status Code da resposta:**", response.status_code)
                st.write("**DEBUG - Headers da resposta:**", dict(response.headers))
                
                if response.status_code in [200, 201]:
                    # Processar resposta da API
                    fixed_code, explanation, changes_made, prevention_tips = self._process_api_response(response)
                    
                    if fixed_code is None:
                        st.error("❌ Erro ao processar resposta da API")
                        return
                    
                    # Armazenar dados na sessão
                    set_session_value("fixed_code", fixed_code)
                    set_session_value("fix_explanation", explanation)
                    set_session_value("fix_changes", changes_made)
                    set_session_value("fix_prevention_tips", prevention_tips)
                    
                    st.success("✅ Código corrigido com sucesso!")
                    st.rerun()
                        
                else:
                    st.error(f"❌ Erro na API: {response.status_code} - {response.text}")
                    
            except requests.exceptions.ConnectionError:
                st.error("❌ Não foi possível conectar à API. Verifique se o backend está rodando.")
                # Mock para desenvolvimento
                self._generate_mock_fix(error_message, bug_code)
            except requests.exceptions.Timeout:
                st.error("⏱️ Timeout na requisição. Tente novamente.")
            except requests.exceptions.RequestException as e:
                st.error(f"❌ Erro na requisição: {str(e)}")
            except ValueError as e:
                st.error(f"❌ Erro de validação: {str(e)}")
            except Exception as e:
                st.error(f"❌ Erro inesperado: {str(e)}")
        
        set_session_value("fix_loading", False)
    
    def _process_api_response(self, response):
        """
        Processa a resposta da API para extrair os dados corretamente.
        
        Args:
            response: Resposta da requisição HTTP
            
        Returns:
            tuple: (fixed_code, explanation, changes_made, prevention_tips)
        """
        try:
            import json
            
            # Obter dados JSON da resposta
            response_data = response.json()
            
            # DEBUG: Verificar tipo e conteúdo da resposta
            st.write("**DEBUG - Tipo da resposta:**", type(response_data))
            st.write("**DEBUG - Resposta completa:**")
            st.json(response_data)
            
            # Verificar se a resposta é uma string JSON que precisa ser parseada novamente
            if isinstance(response_data, str):
                try:
                    response_data = json.loads(response_data)
                except json.JSONDecodeError:
                    st.error("❌ Erro ao processar resposta da API - formato JSON inválido")
                    return None, None, None, None
            
            # Caso especial: se toda a resposta está aninhada como string
            if isinstance(response_data, str) and response_data.strip().startswith('{'):
                try:
                    response_data = json.loads(response_data)
                except json.JSONDecodeError:
                    pass
            
            # Extrair dados da resposta
            fixed_code = response_data.get("fixed_code", "")
            explanation = response_data.get("explanation", "")
            changes_made = response_data.get("changes_made", [])
            prevention_tips = response_data.get("prevention_tips", [])
            
            # Caso especial: verificar se fixed_code contém JSON aninhado
            if isinstance(fixed_code, str) and fixed_code.strip().startswith('{'):
                try:
                    # Se fixed_code for um JSON string, parsear e extrair o código
                    parsed_data = json.loads(fixed_code)
                    if isinstance(parsed_data, dict):
                        actual_fixed_code = parsed_data.get("fixed_code", fixed_code)
                        actual_explanation = parsed_data.get("explanation", explanation or "")
                        actual_changes = parsed_data.get("changes_made", changes_made or [])
                        actual_prevention_tips = parsed_data.get("prevention_tips", prevention_tips or [])
                        
                        fixed_code = actual_fixed_code
                        explanation = actual_explanation
                        changes_made = actual_changes
                        prevention_tips = actual_prevention_tips
                except json.JSONDecodeError:
                    # Se não conseguir parsear, usar o valor original
                    pass
            
            # Validar se temos pelo menos o código corrigido
            if not fixed_code:
                st.error("❌ Código corrigido não encontrado na resposta da API")
                return None, None, None, None
            
            return fixed_code, explanation, changes_made, prevention_tips
            
        except Exception as e:
            st.error(f"❌ Erro ao processar resposta da API: {str(e)}")
            return None, None, None, None
    
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
        
        # Gerar dados mockados adicionais para demonstração
        explanation = self._generate_mock_explanation(error_message)
        changes = self._generate_mock_changes(error_message)
        prevention_tips = self._generate_mock_prevention_tips(error_message)
        
        set_session_value("fixed_code", fixed_code)
        set_session_value("fix_explanation", explanation)
        set_session_value("fix_changes", changes)
        set_session_value("fix_prevention_tips", prevention_tips)
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
        Exibe os resultados da correção de código de forma organizada.
        """
        fixed_code = get_session_value("fixed_code")
        fix_explanation = get_session_value("fix_explanation")
        fix_changes = get_session_value("fix_changes")
        fix_prevention_tips = get_session_value("fix_prevention_tips", [])
        selected_language = get_session_value("selected_language", "python")

        if fixed_code:
            # 🔧 Código Corrigido
            st.markdown("## 🔧 Código Corrigido")
            st.code(fixed_code, language=selected_language)
            
            st.divider()
            
            # 💡 Explicação do erro
            if fix_explanation:
                with st.expander("💡 **Explicação do Erro**", expanded=True):
                    # Destacar termos importantes em negrito
                    explanation_formatted = fix_explanation
                    # Lista de termos para destacar
                    terms_to_highlight = [
                        "erro", "bug", "problema", "exceção", "falha",
                        "NameError", "TypeError", "SyntaxError", "IndexError", "KeyError", "AttributeError",
                        "undefined", "null", "NullPointerException", "segmentation fault"
                    ]
                    
                    for term in terms_to_highlight:
                        explanation_formatted = explanation_formatted.replace(
                            term, f"**{term}**"
                        )
                    
                    st.markdown(explanation_formatted)
            
            # 🛠️ Alterações Realizadas
            if fix_changes and len(fix_changes) > 0:
                with st.expander("🛠️ **Alterações Realizadas**", expanded=True):
                    for i, change in enumerate(fix_changes, 1):
                        st.markdown(f"{i}. {change}")
            
            # ✅ Dicas para Evitar Erros
            if fix_prevention_tips and len(fix_prevention_tips) > 0:
                with st.expander("✅ **Dicas para Evitar Erros Similares**", expanded=False):
                    for tip in fix_prevention_tips:
                        st.markdown(f"• {tip}")
            
            st.divider()
            
            # Botões de ação
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                # Botão para copiar código
                # Escape do código para JavaScript, preservando UTF-8
                code_escaped = fixed_code.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
                copy_button_id = 'copy-fixed-code-button'
                
                html_content = f"""
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
                """
                
                st.components.v1.html(
                    html_content,
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
                    set_session_value("fix_explanation", None)
                    set_session_value("fix_changes", None)
                    set_session_value("fix_prevention_tips", None)
                    st.rerun()
    
    def _generate_mock_explanation(self, error_message: str) -> str:
        """
        Gera explicação mockada baseada no tipo de erro.
        
        Args:
            error_message: Mensagem de erro fornecida
            
        Returns:
            str: Explicação formatada do erro
        """
        error_lower = error_message.lower()
        
        if "nameerror" in error_lower or "not defined" in error_lower:
            return "O **erro** NameError ocorre quando você tenta usar uma variável que não foi definida. Isso acontece quando o Python não consegue encontrar a variável no escopo atual ou em escopos anteriores."
        elif "syntaxerror" in error_lower or "invalid syntax" in error_lower:
            return "O **erro** SyntaxError indica que há um **problema** na estrutura do código. Geralmente ocorre por parênteses não fechados, dois pontos ausentes ou estruturas mal formadas."
        elif "indentationerror" in error_lower or "unexpected indent" in error_lower:
            return "O **erro** IndentationError acontece quando a indentação do código não está correta. Python usa indentação para definir blocos de código, e ela deve ser consistente."
        elif "typeerror" in error_lower:
            return "O **erro** TypeError ocorre quando você tenta realizar uma operação em um tipo de dado inadequado. Por exemplo, tentar somar um número com uma string sem conversão."
        elif "indexerror" in error_lower or "list index out of range" in error_lower:
            return "O **erro** IndexError acontece quando você tenta acessar um índice que não existe na lista. Isso geralmente ocorre quando a lista está vazia ou o índice é maior que o tamanho da lista."
        elif "keyerror" in error_lower:
            return "O **erro** KeyError ocorre quando você tenta acessar uma chave que não existe em um dicionário. É importante verificar se a chave existe antes de acessá-la."
        elif "attributeerror" in error_lower:
            return "O **erro** AttributeError acontece quando você tenta acessar um atributo ou método que não existe no objeto. Verifique se o objeto possui o atributo desejado."
        else:
            return "O **erro** identificado requer atenção especial. É importante analisar a **exceção** para entender sua causa raiz e implementar a correção adequada."
    
    def _generate_mock_changes(self, error_message: str) -> list:
        """
        Gera lista de alterações mockadas baseada no tipo de erro.
        
        Args:
            error_message: Mensagem de erro fornecida
            
        Returns:
            list: Lista de alterações realizadas
        """
        error_lower = error_message.lower()
        
        if "nameerror" in error_lower or "not defined" in error_lower:
            return [
                "Adicionadas definições de variáveis antes do uso",
                "Inicializadas variáveis com valores apropriados",
                "Verificação de escopo das variáveis"
            ]
        elif "syntaxerror" in error_lower or "invalid syntax" in error_lower:
            return [
                "Corrigida sintaxe do Python",
                "Adicionados parênteses faltantes",
                "Estrutura de código reorganizada"
            ]
        elif "indentationerror" in error_lower or "unexpected indent" in error_lower:
            return [
                "Corrigida indentação do código",
                "Padronizada para 4 espaços por nível",
                "Alinhamento de blocos de código"
            ]
        elif "typeerror" in error_lower:
            return [
                "Adicionadas conversões de tipo",
                "Verificação de tipos antes de operações",
                "Tratamento adequado de diferentes tipos de dados"
            ]
        elif "indexerror" in error_lower or "list index out of range" in error_lower:
            return [
                "Adicionada verificação de tamanho da lista",
                "Implementada validação de índices",
                "Tratamento para listas vazias"
            ]
        elif "keyerror" in error_lower:
            return [
                "Adicionada verificação de existência de chaves",
                "Implementado uso de .get() com valor padrão",
                "Tratamento para chaves inexistentes"
            ]
        elif "attributeerror" in error_lower:
            return [
                "Adicionada verificação com hasattr()",
                "Implementada validação de atributos",
                "Tratamento para objetos sem o atributo"
            ]
        else:
            return [
                "Adicionado tratamento de exceções",
                "Implementadas verificações de segurança",
                "Melhorada robustez do código"
            ]
    
    def _generate_mock_prevention_tips(self, error_message: str) -> list:
        """
        Gera dicas de prevenção mockadas baseada no tipo de erro.
        
        Args:
            error_message: Mensagem de erro fornecida
            
        Returns:
            list: Lista de dicas para evitar erros similares
        """
        error_lower = error_message.lower()
        
        if "nameerror" in error_lower or "not defined" in error_lower:
            return [
                "Sempre declare e inicialize variáveis antes de usá-las",
                "Use nomes de variáveis descritivos e consistentes",
                "Verifique o escopo das variáveis em funções",
                "Considere usar ferramentas de linting como pylint"
            ]
        elif "syntaxerror" in error_lower or "invalid syntax" in error_lower:
            return [
                "Use um editor com destacador de sintaxe",
                "Verifique se todos os parênteses, colchetes e chaves estão fechados",
                "Mantenha consistência na indentação",
                "Execute o código frequentemente durante o desenvolvimento"
            ]
        elif "indentationerror" in error_lower or "unexpected indent" in error_lower:
            return [
                "Configure seu editor para mostrar espaços e tabs",
                "Use sempre 4 espaços para indentação em Python",
                "Evite misturar tabs e espaços",
                "Use formatadores automáticos como black ou autopep8"
            ]
        elif "typeerror" in error_lower:
            return [
                "Sempre verifique os tipos de dados antes de operações",
                "Use type hints para maior clareza",
                "Implemente validação de entrada",
                "Considere usar ferramentas como mypy para verificação de tipos"
            ]
        elif "indexerror" in error_lower or "list index out of range" in error_lower:
            return [
                "Sempre verifique o tamanho de listas antes de acessar índices",
                "Use enumerate() quando precisar de índices em loops",
                "Considere usar try/except para capturar IndexError",
                "Prefira métodos como .get() para dicionários"
            ]
        elif "keyerror" in error_lower:
            return [
                "Use o método .get() com valores padrão",
                "Verifique se a chave existe antes de acessá-la",
                "Considere usar defaultdict para casos específicos",
                "Implemente tratamento adequado para chaves ausentes"
            ]
        elif "attributeerror" in error_lower:
            return [
                "Use hasattr() para verificar a existência de atributos",
                "Consulte a documentação dos objetos que está usando",
                "Implemente verificações defensivas",
                "Considere usar getattr() com valores padrão"
            ]
        else:
            return [
                "Implemente tratamento de exceções robusto",
                "Escreva testes unitários para seus códigos",
                "Use logging para rastrear problemas",
                "Mantenha seu código simples e legível",
                "Revise e refatore regularmente seu código"
            ]
