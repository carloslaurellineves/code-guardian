# Refatoração da Funcionalidade StoryCreator

## Resumo das Alterações Realizadas

Este documento descreve as refatorações implementadas na funcionalidade StoryCreator para melhorar a integração com o LLM e a qualidade das histórias geradas.

## Problemas Identificados e Corrigidos

### 1. Interface do Usuário
- **Problema**: Mensagens redundantes na seção "Histórias Geradas"
- **Solução**: Removidos avisos duplicados sobre status da API na interface de exibição das histórias
- **Arquivo**: `app/views/story_creator.py`

### 2. Schema de Dados
- **Problema**: Estrutura limitada das histórias com campos superficiais
- **Solução**: Expandido o schema para incluir:
  - Novo enum `Priority` (baixa, media, alta, urgente)
  - Novo tipo `BUG` em `StoryType`
  - Classe `DetailedTask` para tarefas com descrições detalhadas
  - Campos de justificativa para prioridade e estimativa
  - Estimativa numérica em Story Points (1-21)

### 3. Integração com LLM
- **Problema**: Prompts genéricos gerando respostas superficiais
- **Solução**: 
  - Prompts aprimorados com instruções específicas para gerar tarefas detalhadas
  - Instruções claras sobre formato de resposta JSON
  - Validação de campos obrigatórios (justificativas)
  - Arquivo: `agents/story_agent.py`

## Alterações nos Schemas

### Novo Schema `DetailedTask`
```python
class DetailedTask(BaseModel):
    title: str = Field(..., description="Título da tarefa")
    description: str = Field(..., description="Descrição detalhada da tarefa")
    examples: Optional[List[str]] = Field(default_factory=list, description="Exemplos ou dados extras")
```

### Schema `GeneratedStory` Atualizado
- **priority**: Agora usa enum `Priority` em vez de string livre
- **justificativa_prioridade**: Campo obrigatório explicando a prioridade
- **estimation**: Valor numérico (1-21) em vez de string
- **justificativa_estimativa**: Campo obrigatório explicando a complexidade
- **tasks**: Agora usa `List[DetailedTask]` em vez de `List[str]`

## Prompts Aprimorados para LLM

### Instruções Específicas
- Tarefas devem ser específicas e acionáveis
- Exemplo: Em vez de "Analisar requisitos", usar "Analisar requisitos de autenticação: login via Active Directory, validação de sessão e logout automático"
- Justificativas obrigatórias para prioridade e estimativa
- Formato JSON estruturado com validação

### Exemplo de Prompt Sistema
```
Você é um especialista em metodologias ágeis, engenharia de software e product management.
Sua tarefa é gerar histórias de usuário, épicos e tarefas em formato estruturado e detalhado.

IMPORTANTE: Tarefas devem ser específicas e acionáveis.

Responda SEMPRE em formato JSON válido com a estrutura:
{
  "title": "Título claro e contextualizado",
  "description": "Parágrafo explicativo detalhado da funcionalidade",
  "tasks": [
    {"title": "Título da tarefa", "description": "Descrição detalhada com ações específicas", "examples": ["exemplo 1"]},
  ],
  "priority": "alta",
  "justificativa_prioridade": "Explicação do por que essa prioridade foi atribuída",
  "estimation": 8,
  "justificativa_estimativa": "Explicação da complexidade e fatores considerados na estimativa"
}
```

## Fallback Melhorado

### Implementação Mock Aprimorada
- Histórias baseadas no contexto real fornecido pelo usuário
- Tarefas detalhadas e específicas
- Critérios de aceitação contextuais
- Prioridades e estimativas justificadas

## Princípios SOLID Aplicados

### Single Responsibility Principle (SRP)
- `StoryAgent`: Responsável apenas pela geração de histórias
- `DetailedTask`: Classe específica para tarefas detalhadas
- `Priority`: Enum específico para prioridades

### Open/Closed Principle (OCP)
- Schema extensível através de herança e composição
- Novos tipos de história podem ser adicionados sem alterar código existente

### Dependency Inversion Principle (DIP)
- Integração exclusiva via `llm_factory`
- Abstração do LLM permite troca de provedores sem impacto

## Arquivos Modificados

1. **schemas/story_schemas.py**
   - Adicionados novos enums e classes
   - Campos aprimorados em `GeneratedStory`

2. **agents/story_agent.py**
   - Prompts aprimorados
   - Lógica de fallback melhorada
   - Geração de tarefas detalhadas

3. **app/views/story_creator.py**
   - Remoção de mensagens redundantes
   - Interface mais limpa

4. **services/llm_factory.py**
   - Documentação dos novos prompts
   - Comentários sobre integração com StoryCreator

## Compatibilidade

### Retrocompatibilidade
- ⚠️ **BREAKING CHANGES**: Alterações no schema podem quebrar código existente
- Campos obrigatórios adicionados podem causar erros de validação
- Necessário atualizar código cliente que consuma as APIs

### Migração Necessária
- Atualizar testes unitários para novo schema
- Revisar integrações que dependem dos campos alterados
- Atualizar documentação da API

## Testes Recomendados

1. **Testes Unitários**
   - Validação de schemas com novos campos
   - Geração de histórias com LLM
   - Fallback quando LLM indisponível

2. **Testes de Integração**
   - API endpoints com novo formato
   - Frontend consumindo nova estrutura
   - Persistência dos novos campos

3. **Testes de Aceitação**
   - Histórias geradas são mais detalhadas
   - Justificativas estão presentes
   - Interface sem mensagens redundantes

## Status da Implementação

- [x] Schemas atualizados
- [x] Prompts aprimorados
- [x] Interface limpa
- [x] Fallback melhorado
- [x] Documentação criada
- [ ] Testes unitários atualizados
- [ ] Validação com LLM real
- [ ] Deploy e validação em produção

## Próximos Passos

1. Executar testes para validar as alterações
2. Ajustar código se necessário para compatibilidade
3. Testar integração com LLM real (Azure/OpenAI)
4. Validar interface do usuário
5. Implementar métricas de qualidade das histórias geradas
