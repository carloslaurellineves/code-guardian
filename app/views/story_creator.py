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
        
        with col1:
            if st.button("🗑️ Limpar Cache", key="clear_cache_btn"):
                set_session_value("generated_stories", None)
                st.cache_data.clear()
                st.rerun()
        
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
                    "include_acceptance_criteria": True
                }
                
                # Fazer requisição à API
                response = requests.post(
                    f"{self.api_base_url}/stories/generate",
                    json=payload,
                    timeout=120  # Aumentado para 2 minutos para suportar chamadas LLM mais longas
                )
                
                if response.status_code in [200, 201]:
                    result = response.json()
                    # Processar resposta da API e converter para formato esperado
                    processed_result = self._process_api_response(result)
                    # Marcar como dados da API
                    processed_result["data_source"] = "api"
                    set_session_value("generated_stories", processed_result)
                    add_to_history("story_generation", processed_result)
                    st.success("✅ Histórias geradas com sucesso pela API!")
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
    
    def _process_api_response(self, api_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa a resposta da API e converte para o formato esperado pelo frontend.
        
        Args:
            api_response: Resposta bruta da API
            
        Returns:
            Dict[str, Any]: Dados processados no formato esperado
        """
        processed_result = {
            "stories": [],
            "summary": api_response.get("summary", ""),
            "recommendations": api_response.get("recommendations", []),
            "processing_time": api_response.get("processing_time", 0)
        }
        
        # Processar histórias da API
        if "stories" in api_response and api_response["stories"]:
            for story in api_response["stories"]:
                processed_story = {
                    "title": story.get("title", ""),
                    "description": story.get("description", ""),
                    "story_type": story.get("story_type", "user_story"),
                    "priority": story.get("priority", "Média"),
                    "justificativa_prioridade": story.get("justificativa_prioridade", "Justificativa não fornecida"),
                    "estimation": story.get("estimation", "N/A"),
                    "justificativa_estimativa": story.get("justificativa_estimativa", "Justificativa não fornecida"),
                    "acceptance_criteria": [],
                    "tasks": story.get("tasks", []),
                }
                
                # Processar critérios de aceitação
                if story.get("acceptance_criteria"):
                    for criteria in story["acceptance_criteria"]:
                        if isinstance(criteria, dict) and "given" in criteria:
                            # Formato da API: {"given": "...", "when": "...", "then": "..."}
                            processed_story["acceptance_criteria"].append(criteria)
                        elif isinstance(criteria, str):
                            # Formato alternativo: string simples
                            processed_story["acceptance_criteria"].append({
                                "given": criteria,
                                "when": "N/A",
                                "then": "N/A"
                            })
                
                processed_result["stories"].append(processed_story)
        
        return processed_result
    
    def _generate_mock_stories(self, context: str):
        """
        Gera histórias básicas como fallback quando não há conexão com a API.
        
        Args:
            context: Contexto fornecido pelo usuário
        """
        # Fallback simples baseado no contexto real fornecido
        context_preview = context[:100] + "..." if len(context) > 100 else context
        
        fallback_result = {
            "stories": [
                {
                    "title": f"História baseada no contexto fornecido",
                    "description": f"Esta história foi gerada como fallback. Contexto: {context_preview}",
                    "story_type": "user_story",
                    "priority": "Média",
                    "estimation": "A definir",
                    "acceptance_criteria": [
                        {
                            "given": "Que o sistema está funcionando",
                            "when": "O usuário utiliza a funcionalidade",
                            "then": "A operação deve ser executada conforme especificado"
                        }
                    ],
                    "tasks": [
                        "Analisar requisitos detalhados",
                        "Implementar funcionalidade baseada no contexto",
                        "Realizar testes de validação"
                    ]
                }
            ],
            "summary": "História gerada como fallback - API indisponível",
            "recommendations": [
                "Verifique a conexão com a API para obter histórias mais detalhadas",
                "Revise e detalhe os requisitos com base no contexto fornecido"
            ],
            "processing_time": 0.1
        }
        
        # Marcar como dados de fallback
        fallback_result["data_source"] = "fallback"
        
        set_session_value("generated_stories", fallback_result)
        add_to_history("story_generation", fallback_result)
        st.warning("⚠️ API indisponível. Usando fallback básico baseado no seu contexto.")
    
    def _display_results(self):
        """
        Exibe os resultados das histórias geradas.
        """
        stories_response = get_session_value("generated_stories")
        
        if stories_response:
            st.markdown("## 📋 Histórias Geradas")
            
            # Verificar se existe um resumo da geração
            if "summary" in stories_response:
                st.info(f"📈 {stories_response['summary']}")
            
            # Verificar se existem recomendações
            if "recommendations" in stories_response and stories_response["recommendations"]:
                with st.expander("💡 Recomendações"):
                    for rec in stories_response["recommendations"]:
                        st.markdown(f"- {rec}")
            
            # Processar as histórias retornadas pela API
            if "stories" in stories_response and stories_response["stories"]:
                st.markdown("### 📖 Histórias de Usuário")
                
                for i, story in enumerate(stories_response["stories"], 1):
                    with st.expander(f"História {i}: {story['title']}", expanded=True):
                        # Descrição sem truncamento
                        st.markdown("**Descrição:**")
                        st.text_area(
                            "",
                            value=story['description'],
                            height=100,
                            disabled=True,
                            key=f"desc_{i}",
                            label_visibility="collapsed"
                        )
                        
                        # Colunas para organizar informações
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown(f"**Tipo:** {story.get('story_type', 'N/A')}")
                            if story.get('priority'):
                                st.markdown(f"**Prioridade:** {story['priority']}")
                            if story.get('estimation'):
                                st.markdown(f"**Estimativa:** {story['estimation']} Story Points")
                        
                        with col2:
                            # Justificativas sem truncamento
                            if story.get('justificativa_prioridade'):
                                st.markdown("**Justificativa da Prioridade:**")
                                st.text_area(
                                    "",
                                    value=story['justificativa_prioridade'],
                                    height=80,
                                    disabled=True,
                                    key=f"just_priority_{i}",
                                    label_visibility="collapsed"
                                )
                            
                            if story.get('justificativa_estimativa'):
                                st.markdown("**Justificativa da Estimativa:**")
                                st.text_area(
                                    "",
                                    value=story['justificativa_estimativa'],
                                    height=80,
                                    disabled=True,
                                    key=f"just_estimate_{i}",
                                    label_visibility="collapsed"
                                )
                        
                        # Critérios de aceitação em formato Gherkin
                        if story.get('acceptance_criteria'):
                            st.markdown("**Critérios de Aceitação (Gherkin):**")
                            gherkin_text = []
                            for j, criteria in enumerate(story['acceptance_criteria'], 1):
                                gherkin_text.append(f"Cenário {j}:")
                                gherkin_text.append(f"  Dado {criteria.get('given', '')}")
                                gherkin_text.append(f"  Quando {criteria.get('when', '')}")
                                gherkin_text.append(f"  Então {criteria.get('then', '')}")
                                gherkin_text.append("")
                            
                            st.code("\n".join(gherkin_text), language="gherkin")
                        
                        # Tarefas relacionadas sem truncamento
                        if story.get('tasks'):
                            st.markdown("**Tarefas:**")
                            for task_idx, task in enumerate(story['tasks']):
                                if isinstance(task, dict):
                                    # Task é um objeto DetailedTask
                                    with st.container():
                                        st.markdown(f"**{task_idx + 1}. {task.get('title', 'Tarefa sem título')}**")
                                        st.text_area(
                                            f"Descrição da tarefa {task_idx + 1}:",
                                            value=task.get('description', 'Sem descrição'),
                                            height=60,
                                            disabled=True,
                                            key=f"task_desc_{i}_{task_idx}",
                                            label_visibility="collapsed"
                                        )
                                        if task.get('examples'):
                                            st.markdown("*Exemplos:*")
                                            for example in task['examples']:
                                                st.markdown(f"  • {example}")
                                        st.markdown("---")
                                else:
                                    # Task é uma string simples
                                    st.markdown(f"- {task}")
                        
                        # Botão para copiar usando HTML/JavaScript (igual ao CodeTester e CodeFixer)
                        story_content = self._format_story_for_copy(story, i)
                        story_escaped = story_content.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
                        copy_button_id = f'copy-story-button-{i}'
                        
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
                                margin-bottom: 10px;
                            '>📋 Copiar História {i}</button>
                            <script>
                                document.getElementById('{copy_button_id}').onclick = function() {{
                                    try {{
                                        const storyContent = "{story_escaped}";
                                        navigator.clipboard.writeText(storyContent).then(function() {{
                                            alert('✅ História {i} copiada com sucesso para a área de transferência!');
                                        }}).catch(function(err) {{
                                            console.error('Erro ao copiar:', err);
                                            alert('❌ Erro ao copiar a história. Tente novamente.');
                                        }});
                                    }} catch(e) {{
                                        console.error('Erro:', e);
                                        alert('❌ Erro ao processar a história.');
                                    }}
                                }}
                            </script>
                            """,
                            height=50
                        )
            
            # Tempo de processamento
            if "processing_time" in stories_response:
                st.caption(f"⏱️ Tempo de processamento: {stories_response['processing_time']:.2f} segundos")
            
            # Botões de ação
            col1, col2 = st.columns([1, 1])
            
            with col1:
                # Botão para salvar em TXT
                if st.button("💾 Salvar em TXT", key="save_stories_txt"):
                    txt_content = self._generate_stories_txt(stories_response)
                    st.download_button(
                        label="📥 Download histórias.txt",
                        data=txt_content,
                        file_name="historias_e_tarefas.txt",
                        mime="text/plain",
                        key="download_stories_txt"
                    )
            
            with col2:
                # Botão para limpar resultados
                if st.button("🗑️ Limpar Resultados", key="clear_results"):
                    set_session_value("generated_stories", None)
                    st.rerun()
    
    def _generate_stories_txt(self, stories: Dict[str, Any]) -> str:
        """
        Gera o conteúdo em formato TXT das histórias e tarefas.
        
        Args:
            stories: Dicionário contendo as histórias geradas
            
        Returns:
            str: Conteúdo formatado em texto
        """
        from datetime import datetime
        
        txt_content = []
        txt_content.append("=" * 80)
        txt_content.append("               HISTÓRIAS E TAREFAS - CODE GUARDIAN")
        txt_content.append("=" * 80)
        txt_content.append(f"Data de geração: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        txt_content.append("=" * 80)
        txt_content.append("")
        
        # Processar todas as histórias com todos os campos
        if "stories" in stories and stories["stories"]:
            txt_content.append("📖 HISTÓRIAS DE USUÁRIO COMPLETAS")
            txt_content.append("-" * 80)
            txt_content.append("")
            
            for i, story in enumerate(stories["stories"], 1):
                txt_content.append(f"HISTÓRIA {i}")
                txt_content.append("=" * 40)
                txt_content.append(f"Título: {story['title']}")
                txt_content.append("")
                txt_content.append(f"Descrição: {story['description']}")
                txt_content.append("")
                txt_content.append(f"Tipo: {story.get('story_type', 'N/A')}")
                txt_content.append(f"Prioridade: {story.get('priority', 'Média')}")
                txt_content.append(f"Justificativa da Prioridade: {story.get('justificativa_prioridade', 'Não fornecida')}")
                txt_content.append(f"Estimativa: {story.get('estimation', 'N/A')} story points")
                txt_content.append(f"Justificativa da Estimativa: {story.get('justificativa_estimativa', 'Não fornecida')}")
                txt_content.append("")
                
                # Critérios de aceitação
                if story.get('acceptance_criteria'):
                    txt_content.append("Critérios de Aceitação (Gherkin):")
                    for j, criteria in enumerate(story['acceptance_criteria'], 1):
                        txt_content.append(f"  Cenário {j}:")
                        txt_content.append(f"    Dado {criteria.get('given', '')}")
                        txt_content.append(f"    Quando {criteria.get('when', '')}")
                        txt_content.append(f"    Então {criteria.get('then', '')}")
                        txt_content.append("")
                
                # Tarefas detalhadas
                if story.get('tasks'):
                    txt_content.append("Tarefas:")
                    for task_idx, task in enumerate(story['tasks'], 1):
                        if isinstance(task, dict):
                            txt_content.append(f"  {task_idx}. {task.get('title', 'Tarefa sem título')}")
                            txt_content.append(f"     Descrição: {task.get('description', 'Sem descrição')}")
                            if task.get('examples'):
                                txt_content.append("     Exemplos:")
                                for example in task['examples']:
                                    txt_content.append(f"       • {example}")
                        else:
                            txt_content.append(f"  {task_idx}. {task}")
                        txt_content.append("")
                
                txt_content.append("-" * 80)
                txt_content.append("")
        
        # Resumo e recomendações
        if stories.get('summary'):
            txt_content.append("📈 RESUMO")
            txt_content.append("-" * 30)
            txt_content.append(stories['summary'])
            txt_content.append("")
        
        if stories.get('recommendations'):
            txt_content.append("💡 RECOMENDAÇÕES")
            txt_content.append("-" * 30)
            for rec in stories['recommendations']:
                txt_content.append(f"- {rec}")
            txt_content.append("")
        
        txt_content.append("=" * 80)
        txt_content.append("Gerado pelo CodeGuardian - Story Creator")
        txt_content.append(f"Processamento: {stories.get('processing_time', 0):.2f} segundos")
        txt_content.append("=" * 80)
        
        return "\n".join(txt_content)
    
    def _format_story_for_copy(self, story: Dict[str, Any], story_number: int) -> str:
        """
        Formata uma história individual para cópia na área de transferência.
        
        Args:
            story: Dicionário contendo os dados da história
            story_number: Número da história para identificação
            
        Returns:
            str: Conteúdo formatado da história pronto para cópia
        """
        from datetime import datetime
        
        content = []
        content.append("=" * 60)
        content.append(f"          HISTÓRIA {story_number} - CODE GUARDIAN")
        content.append("=" * 60)
        content.append(f"Copiado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        content.append("=" * 60)
        content.append("")
        
        # Título
        content.append(f"📋 TÍTULO: {story['title']}")
        content.append("")
        
        # Descrição
        content.append("📝 DESCRIÇÃO:")
        content.append(story['description'])
        content.append("")
        
        # Informações básicas
        content.append("📊 INFORMAÇÕES BÁSICAS:")
        content.append(f"Tipo: {story.get('story_type', 'N/A')}")
        content.append(f"Prioridade: {story.get('priority', 'Média')}")
        content.append(f"Estimativa: {story.get('estimation', 'N/A')} Story Points")
        content.append("")
        
        # Justificativas
        if story.get('justificativa_prioridade'):
            content.append("💡 JUSTIFICATIVA DA PRIORIDADE:")
            content.append(story['justificativa_prioridade'])
            content.append("")
        
        if story.get('justificativa_estimativa'):
            content.append("📈 JUSTIFICATIVA DA ESTIMATIVA:")
            content.append(story['justificativa_estimativa'])
            content.append("")
        
        # Critérios de aceitação em formato Gherkin
        if story.get('acceptance_criteria'):
            content.append("✅ CRITÉRIOS DE ACEITAÇÃO (Gherkin):")
            for j, criteria in enumerate(story['acceptance_criteria'], 1):
                content.append(f"Cenário {j}:")
                content.append(f"  Dado {criteria.get('given', '')}")
                content.append(f"  Quando {criteria.get('when', '')}")
                content.append(f"  Então {criteria.get('then', '')}")
                content.append("")
        
        # Tarefas relacionadas
        if story.get('tasks'):
            content.append("📋 TAREFAS:")
            for task_idx, task in enumerate(story['tasks'], 1):
                if isinstance(task, dict):
                    # Task é um objeto DetailedTask
                    content.append(f"{task_idx}. {task.get('title', 'Tarefa sem título')}")
                    content.append(f"   Descrição: {task.get('description', 'Sem descrição')}")
                    if task.get('examples'):
                        content.append("   Exemplos:")
                        for example in task['examples']:
                            content.append(f"     • {example}")
                else:
                    # Task é uma string simples
                    content.append(f"{task_idx}. {task}")
                content.append("")
        
        content.append("=" * 60)
        content.append("Gerado pelo CodeGuardian - Story Creator")
        content.append("=" * 60)
        
        return "\n".join(content)
    
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
