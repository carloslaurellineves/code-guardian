"""
Agente para criação de histórias em formato Gherkin.

Este módulo implementa um agente baseado em LangGraph para
geração automatizada de histórias de usuário, épicos e tarefas.
"""

import uuid
from typing import List, Dict, Any
from datetime import datetime

from schemas.story_schemas import (
    StoryRequest, 
    GeneratedStory, 
    AcceptanceCriteria, 
    StoryType
)
from services.azure_llm import AzureLLMService


class StoryAgent:
    """
    Agente responsável pela geração de histórias.
    
    Este agente utiliza LangGraph para orquestrar o processo
    de criação de histórias em formato Gherkin.
    """
    
    def __init__(self):
        """Inicializa o agente de histórias."""
        self.llm_service = AzureLLMService()
        
    async def generate_stories(self, request: StoryRequest) -> List[GeneratedStory]:
        """
        Gera histórias baseadas na requisição.
        
        Args:
            request: Dados da requisição de geração
            
        Returns:
            List[GeneratedStory]: Lista de histórias geradas
        """
        # Mock implementation - em produção, usar LangGraph
        stories = []
        
        # Gerar história principal
        main_story = await self._generate_single_story(request)
        stories.append(main_story)
        
        # Se for épico, gerar histórias relacionadas
        if request.story_type == StoryType.EPIC:
            related_stories = await self._generate_related_stories(request, main_story)
            stories.extend(related_stories)
            
        return stories
        
    async def _generate_single_story(self, request: StoryRequest) -> GeneratedStory:
        """
        Gera uma única história.
        
        Args:
            request: Dados da requisição
            
        Returns:
            GeneratedStory: História gerada
        """
        # Mock implementation
        story_id = str(uuid.uuid4())
        
        # Títulos mockados baseados no tipo
        titles = {
            StoryType.EPIC: f"Épico: {request.context[:50]}...",
            StoryType.USER_STORY: f"Como usuário, eu quero {request.context[:30]}...",
            StoryType.TASK: f"Implementar {request.context[:40]}..."
        }
        
        # Gerar critérios de aceitação mockados
        acceptance_criteria = []
        if request.include_acceptance_criteria:
            acceptance_criteria = [
                AcceptanceCriteria(
                    given="Que o usuário está autenticado no sistema",
                    when="Ele acessa a funcionalidade",
                    then="Ele deve conseguir realizar a operação com sucesso"
                ),
                AcceptanceCriteria(
                    given="Que os dados são válidos",
                    when="O usuário submete o formulário",
                    then="O sistema deve processar a requisição"
                )
            ]
        
        tasks = [
            "Implementar interface de usuário",
            "Desenvolver lógica de negócio",
            "Criar testes unitários",
            "Realizar testes de integração"
        ]
        
        return GeneratedStory(
            id=story_id,
            title=titles.get(request.story_type, "História Genérica"),
            description=f"Baseado no contexto: {request.context}",
            story_type=request.story_type,
            acceptance_criteria=acceptance_criteria,
            tasks=tasks,
            priority="Média",
            estimation="5 Story Points"
        )
        
    async def _generate_related_stories(self, request: StoryRequest, main_story: GeneratedStory) -> List[GeneratedStory]:
        """
        Gera histórias relacionadas a um épico.
        
        Args:
            request: Dados da requisição
            main_story: História principal
            
        Returns:
            List[GeneratedStory]: Histórias relacionadas
        """
        # Mock implementation
        related_stories = []
        
        for i in range(2):  # Gerar 2 histórias relacionadas
            story_id = str(uuid.uuid4())
            
            related_story = GeneratedStory(
                id=story_id,
                title=f"História {i+1} do épico: {main_story.title}",
                description=f"História relacionada ao épico principal",
                story_type=StoryType.USER_STORY,
                acceptance_criteria=[
                    AcceptanceCriteria(
                        given="Condições específicas da história",
                        when="Ação específica é realizada",
                        then="Resultado específico é obtido"
                    )
                ],
                tasks=[
                    f"Tarefa 1 da história {i+1}",
                    f"Tarefa 2 da história {i+1}"
                ],
                priority="Alta" if i == 0 else "Média",
                estimation=f"{3 + i} Story Points"
            )
            
            related_stories.append(related_story)
            
        return related_stories
        
    async def validate_story(self, story: GeneratedStory) -> Dict[str, Any]:
        """
        Valida uma história gerada.
        
        Args:
            story: História a ser validada
            
        Returns:
            Dict[str, Any]: Resultado da validação
        """
        # Mock implementation
        issues = []
        suggestions = []
        
        # Validações básicas
        if len(story.title) < 10:
            issues.append("Título muito curto")
            suggestions.append("Expandir o título para ser mais descritivo")
            
        if len(story.description) < 20:
            issues.append("Descrição muito curta")
            suggestions.append("Adicionar mais detalhes na descrição")
            
        if not story.acceptance_criteria:
            issues.append("Critérios de aceitação ausentes")
            suggestions.append("Adicionar critérios de aceitação em formato Gherkin")
            
        # Calcular score
        score = max(0, 100 - (len(issues) * 20))
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "suggestions": suggestions,
            "score": score
        }
