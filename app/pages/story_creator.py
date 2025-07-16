"""
Página Story Creator do CodeGuardian usando Streamlit.

Esta página permite ao usuário criar histórias e critérios de aceite
usando metodologias ágeis e linguagem Gherkin.
"""

import streamlit as st
import requests
import json
from typing import Dict, Any
from pathlib import Path
import sys

# Adicionar diretório raiz ao path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from app.utils.session_state import get_session_value, set_session_value, add_to_history


class StoryCreatorPage:
    """
    Classe representando a página Story Creator.
    """
    
    def __init__(self):
        self.api_base_url = get_session_value("api_base_url", "http://localhost:8000/api/v1")
    
    def render(self):
        """
        Renderiza a página Story Creator no Streamlit.
        """
        st.title("🧱 Story Creator")
        
        # Explicação da funcionalidade
        st.markdown("## Geração de Histórias em Formato Gherkin")
        st.info(
            """
            Esta ferramenta gera épicos, histórias e tarefas seguindo metodologias ágeis.
            Os artefatos são criados no padrão **Gherkin** (Given-When-Then) para garantir
            clareza e aderência às diretrizes de qualidade.
            """
        )
        
        # Instruções de uso
        with st.expander("📖 Como usar"):
            st.markdown("""
            1. **Descreva o contexto**: Forneça informações sobre o produto ou funcionalidade
            2. **Seja específico**: Inclua detalhes sobre o objetivo, usuários e requisitos
            3. **Clique em Gerar**: O agente criará histórias estruturadas para você
            4. **Revise e ajuste**: Valide se as histórias atendem suas expectativas
            """)
        
        # Separador
        st.markdown("---")
        
        # Área de input
        st.markdown("## 📝 Entrada de Contexto")
        
        # Campo de texto para contexto
        context_input = st.text_area(
            "Descreva o contexto do produto ou funcionalidade:",
            value=get_session_value("story_context", ""),
            height=150,
            placeholder="Exemplo: Desenvolver uma funcionalidade de login para um sistema de gestão de usuários corporativo. O sistema deve permitir autenticação via Active Directory e manter sessões seguras...",
            help="Quanto mais detalhado for o contexto, melhor será a qualidade das histórias geradas."
        )
        
        # Salvar contexto na sessão
        set_session_value("story_context", context_input)
        
        # Botão para gerar histórias
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col2:
            if st.button(
                "🚀 Gerar Histórias",
                disabled=not context_input.strip(),
                key="generate_stories_btn"
            ):
                self._generate_stories(context_input)
        
        # Separador
        st.markdown("---")
        
        # Área de resultados
        self._display_results()
        
        # Histórico de operações
        self._display_history()
    
    def _generate_stories(self, context: str):
        """
        Gera histórias usando a API do backend.
        
        Args:
            context: Contexto fornecido pelo usuário
        """
        set_session_value("story_loading", True)
        
        with st.spinner("🤖 Gerando histórias... Por favor, aguarde."):
            try:
                # Preparar dados para API
                payload = {
                    "context": context,
                    "format": "gherkin",
                    "include_acceptance_criteria": True
                }
                
                # Fazer requisição à API
                response = requests.post(
                    f"{self.api_base_url}/stories/generate",
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    set_session_value("generated_stories", result)
                    add_to_history("story_generation", result)
                    st.success("✅ Histórias geradas com sucesso!")
                else:
                    st.error(f"❌ Erro na API: {response.status_code} - {response.text}")
                    
            except requests.exceptions.ConnectionError:
                st.error("❌ Não foi possível conectar à API. Verifique se o backend está rodando.")
                # Mock para desenvolvimento
                self._generate_mock_stories(context)
            except requests.exceptions.Timeout:
                st.error("⏱️ Timeout na requisição. Tente novamente.")
            except Exception as e:
                st.error(f"❌ Erro inesperado: {str(e)}")
        
        set_session_value("story_loading", False)
    
    def _generate_mock_stories(self, context: str):
        """
        Gera histórias mockadas para desenvolvimento.
        
        Args:
            context: Contexto fornecido pelo usuário
        """
        mock_result = {
            "epic": {
                "title": "Sistema de Autenticação Corporativa",
                "description": "Como desenvolvedor, quero implementar um sistema de autenticação robusto para garantir segurança e controle de acesso.",
                "acceptance_criteria": [
                    "Integração com Active Directory",
                    "Sessões seguras com timeout",
                    "Log de auditoria"
                ]
            },
            "stories": [
                {
                    "title": "Login com Active Directory",
                    "description": "Como usuário corporativo, quero fazer login usando minha conta do AD para acessar o sistema de forma segura.",
                    "gherkin": """
Funcionalidade: Login com Active Directory
    
Cenário: Login bem-sucedido
    Dado que o usuário possui uma conta válida no AD
    Quando ele inserir suas credenciais corretas
    Então ele deve ser autenticado com sucesso
    E deve ser redirecionado para a página inicial

Cenário: Falha na autenticação
    Dado que o usuário inseriu credenciais inválidas
    Quando ele tentar fazer login
    Então deve ser exibida uma mensagem de erro
    E o sistema deve registrar a tentativa de login falhada
                    """,
                    "acceptance_criteria": [
                        "Validação de credenciais via LDAP",
                        "Timeout de sessão configurável",
                        "Mensagens de erro claras"
                    ]
                }
            ],
            "tasks": [
                {
                    "title": "Implementar conexão LDAP",
                    "description": "Configurar e implementar conexão com servidor LDAP do AD",
                    "estimate": "5 story points"
                },
                {
                    "title": "Criar interface de login",
                    "description": "Desenvolver tela de login responsiva",
                    "estimate": "3 story points"
                }
            ]
        }
        
        set_session_value("generated_stories", mock_result)
        add_to_history("story_generation", mock_result)
        st.info("💡 Usando dados mockados para desenvolvimento")
    
    def _display_results(self):
        """
        Exibe os resultados das histórias geradas.
        """
        stories = get_session_value("generated_stories")
        
        if stories:
            st.markdown("## 📋 Histórias Geradas")
            
            # Épico
            if "epic" in stories:
                st.markdown("### 🎯 Épico")
                epic = stories["epic"]
                st.markdown(f"**{epic['title']}**")
                st.markdown(epic['description'])
                
                if epic.get('acceptance_criteria'):
                    st.markdown("**Critérios de Aceite:**")
                    for criteria in epic['acceptance_criteria']:
                        st.markdown(f"- {criteria}")
                
                st.markdown("---")
            
            # Histórias
            if "stories" in stories:
                st.markdown("### 📖 Histórias de Usuário")
                
                for i, story in enumerate(stories["stories"], 1):
                    with st.expander(f"História {i}: {story['title']}", expanded=True):
                        st.markdown(f"**Descrição:** {story['description']}")
                        
                        if story.get('gherkin'):
                            st.markdown("**Gherkin:**")
                            st.code(story['gherkin'], language="gherkin")
                        
                        if story.get('acceptance_criteria'):
                            st.markdown("**Critérios de Aceite:**")
                            for criteria in story['acceptance_criteria']:
                                st.markdown(f"- {criteria}")
                        
                        # Botão para copiar
                        if st.button(f"📋 Copiar História {i}", key=f"copy_story_{i}"):
                            st.success(f"História {i} copiada!")
            
            # Tarefas
            if "tasks" in stories:
                st.markdown("### ✅ Tarefas")
                
                for i, task in enumerate(stories["tasks"], 1):
                    with st.expander(f"Tarefa {i}: {task['title']}"):
                        st.markdown(f"**Descrição:** {task['description']}")
                        if task.get('estimate'):
                            st.markdown(f"**Estimativa:** {task['estimate']}")
            
            # Botão para limpar resultados
            if st.button("🗑️ Limpar Resultados", key="clear_results"):
                set_session_value("generated_stories", None)
                st.rerun()
    
    def _display_history(self):
        """
        Exibe o histórico de operações realizadas.
        """
        history = get_session_value("operation_history", [])
        story_history = [op for op in history if op["operation"] == "story_generation"]
        
        if story_history:
            with st.expander("📚 Histórico de Gerações"):
                st.markdown(f"**Total de gerações:** {len(story_history)}")
                
                for i, entry in enumerate(reversed(story_history[-5:]), 1):
                    st.markdown(f"**Geração {i}:**")
                    if entry["result"].get("epic"):
                        st.markdown(f"- Épico: {entry['result']['epic']['title']}")
                    if entry["result"].get("stories"):
                        st.markdown(f"- Histórias: {len(entry['result']['stories'])}")
                    if entry["result"].get("tasks"):
                        st.markdown(f"- Tarefas: {len(entry['result']['tasks'])}")
                    st.markdown("---")
