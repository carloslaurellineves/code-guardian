"""
Testes unitários para a funcionalidade StoryCreator refatorada.

Este módulo testa as correções implementadas na funcionalidade StoryCreator,
incluindo:
- Geração completa de histórias com todos os campos obrigatórios
- Exibição adequada no front-end sem truncamento
- Exportação completa para TXT
- Validação de schemas e integração com LLM Factory
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from datetime import datetime

from schemas.story_schemas import (
    StoryRequest, GeneratedStory, AcceptanceCriteria, 
    StoryType, Priority, DetailedTask
)
from agents.story_agent import StoryAgent
from app.views.story_creator import StoryCreatorPage


class TestStorySchemas:
    """Testes para validação dos schemas de histórias."""
    
    def test_generated_story_complete_schema(self):
        """Testa se o schema GeneratedStory contém todos os campos obrigatórios."""
        story = GeneratedStory(
            id="test-123",
            title="Como usuário, eu quero fazer login para acessar o sistema",
            description="Esta é uma história completa para teste de login no sistema corporativo.",
            story_type=StoryType.USER_STORY,
            acceptance_criteria=[
                AcceptanceCriteria(
                    given="Que o usuário possui credenciais válidas",
                    when="Ele tenta fazer login",
                    then="Ele deve ser autenticado com sucesso"
                )
            ],
            tasks=[
                DetailedTask(
                    title="Implementar validação de credenciais",
                    description="Desenvolver sistema de validação de usuário e senha",
                    examples=["Hash de senha", "Validação de email", "Rate limiting"]
                )
            ],
            priority=Priority.ALTA,
            justificativa_prioridade="Alta prioridade devido ao impacto direto na segurança",
            estimation=5,
            justificativa_estimativa="Complexidade média considerando validações de segurança"
        )
        
        # Verificar se todos os campos obrigatórios estão presentes
        assert story.id == "test-123"
        assert story.title is not None and len(story.title) > 0
        assert story.description is not None and len(story.description) > 0
        assert story.story_type == StoryType.USER_STORY
        assert len(story.acceptance_criteria) > 0
        assert len(story.tasks) > 0
        assert story.priority in [Priority.BAIXA, Priority.MEDIA, Priority.ALTA, Priority.URGENTE]
        assert story.justificativa_prioridade is not None and len(story.justificativa_prioridade) > 0
        assert isinstance(story.estimation, int) and 1 <= story.estimation <= 21
        assert story.justificativa_estimativa is not None and len(story.justificativa_estimativa) > 0
    
    def test_detailed_task_schema(self):
        """Testa se o schema DetailedTask funciona corretamente."""
        task = DetailedTask(
            title="Implementar autenticação",
            description="Desenvolver sistema de autenticação seguro com JWT",
            examples=["JWT tokens", "OAuth2", "Rate limiting", "Session management"]
        )
        
        assert task.title == "Implementar autenticação"
        assert task.description is not None and len(task.description) > 0
        assert len(task.examples) == 4
        assert "JWT tokens" in task.examples


class TestStoryAgent:
    """Testes para o agente de geração de histórias."""
    
    @pytest.fixture
    def story_agent(self):
        """Fixture para criar instância do StoryAgent."""
        return StoryAgent()
    
    @pytest.fixture
    def sample_request(self):
        """Fixture para criar uma requisição de exemplo."""
        return StoryRequest(
            context="Desenvolver funcionalidade de login para sistema corporativo com autenticação via Active Directory e controle de sessões.",
            story_type=StoryType.USER_STORY,
            include_acceptance_criteria=True,
            language="pt-BR"
        )
    
    @pytest.mark.asyncio
    async def test_generate_stories_mock(self, story_agent, sample_request):
        """Testa a geração de histórias usando implementação mock."""
        # Forçar uso do mock
        story_agent.use_llm = False
        
        stories = await story_agent.generate_stories(sample_request)
        
        # Verificar se histórias foram geradas
        assert len(stories) > 0
        
        story = stories[0]
        assert isinstance(story, GeneratedStory)
        assert story.title is not None and len(story.title) > 0
        assert story.description is not None and len(story.description) > 0
        assert len(story.acceptance_criteria) > 0
        assert len(story.tasks) > 0
        assert story.justificativa_prioridade is not None
        assert story.justificativa_estimativa is not None
        assert isinstance(story.estimation, int)
    
    def test_extract_feature_keywords(self, story_agent):
        """Testa extração de palavras-chave do contexto."""
        context = "Desenvolver funcionalidade de login para administrador com autenticação segura"
        keywords = story_agent._extract_feature_keywords(context)
        
        assert "main_feature" in keywords
        assert "user_type" in keywords
        assert "action" in keywords
        assert "benefit" in keywords
        
        # Verificar se detectou corretamente o tipo de usuário
        assert "administrador" in keywords["user_type"]
        assert "autenticação" in keywords["main_feature"]
    
    def test_generate_contextual_criteria(self, story_agent):
        """Testa geração de critérios contextuais."""
        context = "Sistema de formulário com notificações para usuários"
        criteria = story_agent._generate_contextual_criteria(context)
        
        assert len(criteria) > 0
        
        # Verificar se todos os critérios são válidos
        for criterion in criteria:
            assert isinstance(criterion, AcceptanceCriteria)
            assert criterion.given is not None and len(criterion.given) > 0
            assert criterion.when is not None and len(criterion.when) > 0
            assert criterion.then is not None and len(criterion.then) > 0
    
    def test_generate_contextual_detailed_tasks(self, story_agent):
        """Testa geração de tarefas detalhadas contextuais."""
        context = "Sistema com banco de dados, API REST e autenticação"
        tasks = story_agent._generate_contextual_detailed_tasks(context)
        
        assert len(tasks) > 0
        
        # Verificar se as tarefas são DetailedTask
        for task in tasks:
            assert isinstance(task, DetailedTask)
            assert task.title is not None and len(task.title) > 0
            assert task.description is not None and len(task.description) > 0


class TestStoryCreatorPage:
    """Testes para a página StoryCreator no Streamlit."""
    
    @pytest.fixture
    def story_page(self):
        """Fixture para criar instância da página."""
        return StoryCreatorPage()
    
    def test_process_api_response(self, story_page):
        """Testa processamento da resposta da API."""
        api_response = {
            "success": True,
            "stories": [
                {
                    "id": "story-123",
                    "title": "Como usuário, eu quero fazer login",
                    "description": "História completa de login no sistema",
                    "story_type": "user_story",
                    "priority": "alta",
                    "justificativa_prioridade": "Crítico para segurança",
                    "estimation": 8,
                    "justificativa_estimativa": "Complexidade alta devido às validações",
                    "acceptance_criteria": [
                        {
                            "given": "Que o usuário tem credenciais",
                            "when": "Ele faz login",
                            "then": "Ele é autenticado"
                        }
                    ],
                    "tasks": [
                        {
                            "title": "Implementar validação",
                            "description": "Criar sistema de validação",
                            "examples": ["JWT", "OAuth"]
                        }
                    ]
                }
            ],
            "summary": "História gerada com sucesso",
            "recommendations": ["Revisar critérios de aceitação"],
            "processing_time": 2.5
        }
        
        processed = story_page._process_api_response(api_response)
        
        # Verificar estrutura processada
        assert "stories" in processed
        assert len(processed["stories"]) == 1
        
        story = processed["stories"][0]
        assert story["title"] == "Como usuário, eu quero fazer login"
        assert story["description"] == "História completa de login no sistema"
        assert story["justificativa_prioridade"] == "Crítico para segurança"
        assert story["justificativa_estimativa"] == "Complexidade alta devido às validações"
        assert len(story["acceptance_criteria"]) == 1
        assert len(story["tasks"]) == 1
    
    def test_generate_stories_txt_complete(self, story_page):
        """Testa geração completa do arquivo TXT."""
        stories_data = {
            "stories": [
                {
                    "title": "Como usuário, eu quero fazer login para acessar o sistema",
                    "description": "Esta é uma história completa que não deve ser truncada no arquivo TXT final.",
                    "story_type": "user_story",
                    "priority": "Alta",
                    "justificativa_prioridade": "Alta prioridade devido ao impacto crítico na segurança do sistema",
                    "estimation": 8,
                    "justificativa_estimativa": "8 story points devido à complexidade de implementar múltiplas validações",
                    "acceptance_criteria": [
                        {
                            "given": "Que o usuário possui credenciais válidas",
                            "when": "Ele tenta fazer login",
                            "then": "Ele deve ser autenticado com sucesso"
                        },
                        {
                            "given": "Que o usuário inseriu credenciais inválidas",
                            "when": "Ele tenta fazer login",
                            "then": "O sistema deve mostrar mensagem de erro"
                        }
                    ],
                    "tasks": [
                        {
                            "title": "Implementar validação de credenciais",
                            "description": "Desenvolver sistema completo de validação de usuário e senha com hash seguro",
                            "examples": ["Bcrypt hashing", "Rate limiting", "Account lockout"]
                        },
                        {
                            "title": "Criar interface de login",
                            "description": "Desenvolver tela responsiva de login com feedback visual",
                            "examples": ["Form validation", "Loading states", "Error messages"]
                        }
                    ]
                }
            ],
            "summary": "História gerada com sucesso pela API",
            "recommendations": [
                "Revisar os critérios de aceitação gerados",
                "Validar estimativas com a equipe de desenvolvimento"
            ],
            "processing_time": 3.2
        }
        
        txt_content = story_page._generate_stories_txt(stories_data)
        
        # Verificar se o conteúdo TXT contém todos os campos
        assert "Como usuário, eu quero fazer login para acessar o sistema" in txt_content
        assert "Esta é uma história completa que não deve ser truncada" in txt_content
        assert "Alta prioridade devido ao impacto crítico na segurança" in txt_content
        assert "8 story points devido à complexidade de implementar" in txt_content
        assert "Implementar validação de credenciais" in txt_content
        assert "Desenvolver sistema completo de validação" in txt_content
        assert "Bcrypt hashing" in txt_content
        assert "Criar interface de login" in txt_content
        assert "Form validation" in txt_content
        assert "Cenário 1:" in txt_content
        assert "Cenário 2:" in txt_content
        assert "RESUMO" in txt_content
        assert "RECOMENDAÇÕES" in txt_content
        assert "Processamento: 3.20 segundos" in txt_content
        
        # Verificar que não há truncamento
        assert "..." not in txt_content or txt_content.count("...") <= 1  # Apenas no contexto se aplicável


class TestIntegration:
    """Testes de integração end-to-end."""
    
    @pytest.mark.asyncio
    async def test_complete_story_generation_flow(self):
        """Testa o fluxo completo de geração de histórias."""
        # Criar requisição
        request = StoryRequest(
            context="Desenvolver sistema de gestão de ideias inovadoras para colaboradores com workflow de aprovação e métricas de engajamento",
            story_type=StoryType.EPIC,
            include_acceptance_criteria=True,
            language="pt-BR"
        )
        
        # Gerar histórias usando mock
        agent = StoryAgent()
        agent.use_llm = False  # Usar mock para teste
        
        stories = await agent.generate_stories(request)
        
        # Verificar que épico gera múltiplas histórias
        assert len(stories) > 1
        
        # Verificar primeira história (principal)
        main_story = stories[0]
        assert isinstance(main_story, GeneratedStory)
        assert main_story.title is not None and len(main_story.title) > 0
        assert main_story.description is not None and len(main_story.description) > 0
        assert len(main_story.acceptance_criteria) > 0
        assert len(main_story.tasks) > 0
        assert main_story.justificativa_prioridade is not None
        assert main_story.justificativa_estimativa is not None
        
        # Verificar que tarefas são DetailedTask
        for task in main_story.tasks:
            assert isinstance(task, DetailedTask)
            assert task.title is not None and len(task.title) > 0
            assert task.description is not None and len(task.description) > 0
        
        # Simular processamento no frontend
        page = StoryCreatorPage()
        
        # Simular resposta da API
        api_response = {
            "success": True,
            "stories": [
                {
                    "id": story.id,
                    "title": story.title,
                    "description": story.description,
                    "story_type": story.story_type.value,
                    "priority": story.priority.value,
                    "justificativa_prioridade": story.justificativa_prioridade,
                    "estimation": story.estimation,
                    "justificativa_estimativa": story.justificativa_estimativa,
                    "acceptance_criteria": [
                        {
                            "given": criteria.given,
                            "when": criteria.when,
                            "then": criteria.then
                        } for criteria in story.acceptance_criteria
                    ],
                    "tasks": [
                        {
                            "title": task.title,
                            "description": task.description,
                            "examples": task.examples
                        } for task in story.tasks
                    ]
                } for story in stories
            ],
            "summary": f"Geradas {len(stories)} história(s) com sucesso",
            "recommendations": [
                "Revise os critérios de aceitação gerados",
                "Considere adicionar mais contexto se necessário"
            ],
            "processing_time": 2.8
        }
        
        # Processar resposta
        processed_result = page._process_api_response(api_response)
        
        # Verificar processamento
        assert len(processed_result["stories"]) == len(stories)
        assert processed_result["summary"] is not None
        assert len(processed_result["recommendations"]) > 0
        
        # Gerar TXT e verificar completude
        txt_content = page._generate_stories_txt(processed_result)
        
        # Verificar que TXT contém informações completas
        assert "HISTÓRIAS DE USUÁRIO COMPLETAS" in txt_content
        assert processed_result["stories"][0]["title"] in txt_content
        assert processed_result["stories"][0]["justificativa_prioridade"] in txt_content
        assert processed_result["stories"][0]["justificativa_estimativa"] in txt_content
        
        # Verificar que as tarefas detalhadas estão no TXT
        first_task = processed_result["stories"][0]["tasks"][0]
        assert first_task["title"] in txt_content
        assert first_task["description"] in txt_content
        
        print("✅ Teste de integração end-to-end concluído com sucesso")


if __name__ == "__main__":
    # Executar testes específicos
    pytest.main([__file__, "-v"])
