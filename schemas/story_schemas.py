"""
Schemas para funcionalidades de criação de histórias.

Este módulo define os modelos de dados para entrada e saída
da funcionalidade de criação de histórias em formato Gherkin.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class StoryType(str, Enum):
    """
    Tipos de histórias que podem ser geradas.
    """
    EPIC = "epic"
    USER_STORY = "user_story"
    TASK = "task"
    BUG = "bug"


class Priority(str, Enum):
    """
    Prioridades disponíveis para as histórias.
    """
    BAIXA = "baixa"
    MEDIA = "media"
    ALTA = "alta"
    URGENTE = "urgente"


class StoryRequest(BaseModel):
    """
    Schema para requisição de criação de histórias.
    
    Attributes:
        context: Contexto da funcionalidade ou produto
        story_type: Tipo de história a ser gerada
        additional_requirements: Requisitos adicionais específicos
        include_acceptance_criteria: Se deve incluir critérios de aceitação
        language: Idioma para geração da história
    """
    context: str = Field(..., min_length=10, description="Contexto da funcionalidade ou produto")
    story_type: StoryType = Field(default=StoryType.USER_STORY, description="Tipo de história a ser gerada")
    additional_requirements: Optional[List[str]] = Field(None, description="Lista de requisitos adicionais específicos")
    include_acceptance_criteria: bool = Field(default=True, description="Se deve incluir critérios de aceitação")
    language: str = Field(default="pt-BR", description="Idioma para geração da história")


class AcceptanceCriteria(BaseModel):
    """
    Schema para critérios de aceitação.
    
    Attributes:
        given: Condições iniciais
        when: Ação realizada
        then: Resultado esperado
    """
    given: str = Field(..., description="Condições iniciais")
    when: str = Field(..., description="Ação realizada")
    then: str = Field(..., description="Resultado esperado")


class DetailedTask(BaseModel):
    """
    Schema para tarefas detalhadas.
    
    Attributes:
        title: Título da tarefa
        description: Descrição detalhada da tarefa
        examples: Exemplos ou dados extras quando aplicável
    """
    title: str = Field(..., description="Título da tarefa")
    description: str = Field(..., description="Descrição detalhada da tarefa")
    examples: Optional[List[str]] = Field(default_factory=list, description="Exemplos ou dados extras")


class GeneratedStory(BaseModel):
    """
    Schema para uma história gerada com estrutura aprimorada.
    
    Attributes:
        id: ID da história
        title: Título claro e contextualizado
        description: Parágrafo explicativo detalhado
        story_type: Tipo da história (user_story, epic, task, bug)
        acceptance_criteria: Lista de critérios de aceitação em formato Gherkin
        tasks: Lista de tarefas detalhadas
        priority: Prioridade da história
        justificativa_prioridade: Justificativa para a prioridade atribuída
        estimation: Estimativa numérica em Story Points
        justificativa_estimativa: Justificativa para a complexidade estimada
    """
    id: str = Field(..., description="ID da história")
    title: str = Field(..., description="Título claro e contextualizado")
    description: str = Field(..., description="Parágrafo explicativo detalhado")
    story_type: StoryType = Field(..., description="Tipo da história")
    acceptance_criteria: List[AcceptanceCriteria] = Field(default_factory=list, description="Lista de critérios de aceitação")
    tasks: List[DetailedTask] = Field(default_factory=list, description="Lista de tarefas detalhadas")
    priority: Priority = Field(..., description="Prioridade da história")
    justificativa_prioridade: str = Field(..., description="Justificativa para a prioridade atribuída")
    estimation: int = Field(..., ge=1, le=21, description="Estimativa numérica em Story Points (1-21)")
    justificativa_estimativa: str = Field(..., description="Justificativa para a complexidade estimada")


class StoryResponse(BaseModel):
    """
    Schema para resposta de criação de histórias.
    
    Attributes:
        success: Indica se a operação foi bem-sucedida
        stories: Lista de histórias geradas
        summary: Resumo da geração
        recommendations: Recomendações para melhoria
        processing_time: Tempo de processamento em segundos
    """
    success: bool = Field(..., description="Indica se a operação foi bem-sucedida")
    stories: List[GeneratedStory] = Field(..., description="Lista de histórias geradas")
    summary: str = Field(..., description="Resumo da geração")
    recommendations: List[str] = Field(default_factory=list, description="Recomendações para melhoria")
    processing_time: float = Field(..., description="Tempo de processamento em segundos")
