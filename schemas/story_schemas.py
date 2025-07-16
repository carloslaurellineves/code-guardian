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
    additional_requirements: Optional[str] = Field(None, description="Requisitos adicionais específicos")
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


class GeneratedStory(BaseModel):
    """
    Schema para uma história gerada.
    
    Attributes:
        id: ID da história
        title: Título da história
        description: Descrição da história
        story_type: Tipo da história
        acceptance_criteria: Lista de critérios de aceitação
        tasks: Lista de tarefas relacionadas
        priority: Prioridade da história
        estimation: Estimativa de esforço
    """
    id: str = Field(..., description="ID da história")
    title: str = Field(..., description="Título da história")
    description: str = Field(..., description="Descrição da história")
    story_type: StoryType = Field(..., description="Tipo da história")
    acceptance_criteria: List[AcceptanceCriteria] = Field(default_factory=list, description="Lista de critérios de aceitação")
    tasks: List[str] = Field(default_factory=list, description="Lista de tarefas relacionadas")
    priority: Optional[str] = Field(None, description="Prioridade da história")
    estimation: Optional[str] = Field(None, description="Estimativa de esforço")


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
