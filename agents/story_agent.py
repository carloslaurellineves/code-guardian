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
    StoryType,
    Priority,
    DetailedTask
)
from services.llm_factory import load_llm


class StoryAgent:
    """
    Agente responsável pela geração de histórias.
    
    Este agente utiliza LangGraph para orquestrar o processo
    de criação de histórias em formato Gherkin.
    """
    
    def __init__(self):
        """Inicializa o agente de histórias."""
        try:
            self.llm = load_llm()
            self.use_llm = True
        except Exception as e:
            print(f"Aviso: Não foi possível carregar LLM ({e}). Usando implementação mock.")
            self.llm = None
            self.use_llm = False
        
    async def generate_stories(self, request: StoryRequest) -> List[GeneratedStory]:
        """
        Gera histórias baseadas na requisição.
        
        Args:
            request: Dados da requisição de geração
            
        Returns:
            List[GeneratedStory]: Lista de histórias geradas
        """
        if self.use_llm:
            return await self._generate_stories_with_llm(request)
        else:
            return await self._generate_stories_mock(request)
            
    async def _generate_stories_with_llm(self, request: StoryRequest) -> List[GeneratedStory]:
        """
        Gera histórias usando o LLM real.
        
        Args:
            request: Dados da requisição de geração
            
        Returns:
            List[GeneratedStory]: Lista de histórias geradas
        """
        from langchain_core.messages import HumanMessage, SystemMessage
        import json
        
        # Prompt sistema para geração de histórias com estrutura aprimorada
        system_prompt = """
        Você é um especialista em metodologias ágeis, engenharia de software e product management.
        Sua tarefa é gerar histórias de usuário, épicos e tarefas em formato estruturado e detalhado.
        
        Baseado no contexto fornecido, gere:
        1. Título claro e contextualizado (seguindo padrão: "Como [persona], eu quero [funcionalidade] para [benefício]")
        2. Descrição detalhada (parágrafo explicativo compreensível por todo o time)
        3. Critérios de aceitação em formato Gherkin (Dado/Quando/Então)
        4. Lista de tarefas detalhadas com ações específicas
        5. Prioridade com justificativa (baixa, media, alta, urgente)
        6. Estimativa numérica em Story Points (1-21) com justificativa de complexidade
        
        IMPORTANTE: Tarefas devem ser específicas e acionáveis. Em vez de "Analisar requisitos", 
        use "Analisar requisitos de autenticação: login via Active Directory, validação de sessão e logout automático".
        
        Responda SEMPRE em formato JSON válido com a estrutura:
        {
          "title": "Título claro e contextualizado",
          "description": "Parágrafo explicativo detalhado da funcionalidade",
          "acceptance_criteria": [
            {"given": "condição inicial", "when": "ação do usuário", "then": "resultado esperado"},
            {"given": "condição inicial", "when": "ação do usuário", "then": "resultado esperado"}
          ],
          "tasks": [
            {"title": "Título da tarefa", "description": "Descrição detalhada com ações específicas", "examples": ["exemplo 1", "exemplo 2"]},
            {"title": "Título da tarefa", "description": "Descrição detalhada com ações específicas", "examples": []}
          ],
          "priority": "alta",
          "justificativa_prioridade": "Explicação do por que essa prioridade foi atribuída",
          "estimation": 8,
          "justificativa_estimativa": "Explicação da complexidade e fatores considerados na estimativa"
        }
        """
        
        # Prompt humano com o contexto
        human_prompt = f"""
        Contexto da funcionalidade:
        {request.context}
        
        Tipo de história desejada: {request.story_type}
        Incluir critérios de aceitação: {request.include_acceptance_criteria}
        Idioma: {request.language}
        
        {f"Requisitos adicionais: {', '.join(request.additional_requirements)}" if request.additional_requirements else ""}
        
        Gere uma história de usuário completa e detalhada baseada neste contexto.
        """
        
        try:
            # Executar prompt no LLM
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ]
            
            response = self.llm.invoke(messages)
            
            # Parsear resposta JSON
            story_data = json.loads(response.content)
            
            # Criar história estruturada
            story_id = str(uuid.uuid4())
            
            acceptance_criteria = []
            if story_data.get('acceptance_criteria') and request.include_acceptance_criteria:
                for criteria in story_data['acceptance_criteria']:
                    acceptance_criteria.append(AcceptanceCriteria(
                        given=criteria.get('given', ''),
                        when=criteria.get('when', ''),
                        then=criteria.get('then', '')
                    ))
            
            # Processar tarefas detalhadas
            detailed_tasks = []
            for task_data in story_data.get('tasks', []):
                if isinstance(task_data, dict):
                    detailed_tasks.append(DetailedTask(
                        title=task_data.get('title', ''),
                        description=task_data.get('description', ''),
                        examples=task_data.get('examples', [])
                    ))
                elif isinstance(task_data, str):
                    detailed_tasks.append(DetailedTask(
                        title=task_data,
                        description="Tarefa gerada pelo LLM",
                        examples=[]
                    ))
            
            # Mapear prioridade corretamente
            priority_mapping = {
                'baixa': Priority.BAIXA,
                'media': Priority.MEDIA,
                'média': Priority.MEDIA,
                'alta': Priority.ALTA,
                'urgente': Priority.URGENTE
            }
            priority_str = story_data.get('priority', 'media').lower()
            priority = priority_mapping.get(priority_str, Priority.MEDIA)
            
            generated_story = GeneratedStory(
                id=story_id,
                title=story_data.get('title', 'História Gerada'),
                description=story_data.get('description', ''),
                story_type=request.story_type,
                acceptance_criteria=acceptance_criteria,
                tasks=detailed_tasks,
                priority=priority,
                justificativa_prioridade=story_data.get('justificativa_prioridade', 'Prioridade atribuída com base na análise do contexto'),
                estimation=story_data.get('estimation', 5),
                justificativa_estimativa=story_data.get('justificativa_estimativa', 'Estimativa baseada na complexidade identificada')
            )
            
            return [generated_story]
            
        except Exception as e:
            print(f"Erro ao gerar história com LLM: {e}")
            # Fallback para implementação mock
            return await self._generate_stories_mock(request)
    
    async def _generate_stories_mock(self, request: StoryRequest) -> List[GeneratedStory]:
        """
        Gera histórias usando implementação mock (fallback).
        
        Args:
            request: Dados da requisição de geração
            
        Returns:
            List[GeneratedStory]: Lista de histórias geradas
        """
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
        Gera uma única história baseada no contexto real fornecido.
        
        Args:
            request: Dados da requisição
            
        Returns:
            GeneratedStory: História gerada
        """
        story_id = str(uuid.uuid4())
        
        # Extrair informações relevantes do contexto fornecido
        context_lower = request.context.lower()
        
        # Identificar se é sobre o "Ideia no Bolso" ou outro contexto
        if "ideia no bolso" in context_lower or "inovação" in context_lower:
            return self._generate_innovation_story(request, story_id)
        
        # Para outros contextos, gerar baseado no conteúdo real
        feature_keywords = self._extract_feature_keywords(request.context)
        
        # Gerar título baseado no contexto real
        if request.story_type == StoryType.EPIC:
            title = f"Épico: {feature_keywords['main_feature']}"
        elif request.story_type == StoryType.USER_STORY:
            title = f"Como {feature_keywords['user_type']}, eu quero {feature_keywords['action']} para {feature_keywords['benefit']}"
        else:
            title = f"Implementar {feature_keywords['main_feature']}"
        
        # Gerar critérios de aceitação baseados no contexto
        acceptance_criteria = []
        if request.include_acceptance_criteria:
            acceptance_criteria = self._generate_contextual_criteria(request.context)
        
        # Gerar tarefas baseadas no contexto
        tasks = self._generate_contextual_detailed_tasks(request.context)
        
        return GeneratedStory(
            id=story_id,
            title=title,
            description=f"Baseado no contexto fornecido: {request.context[:200]}...",
            story_type=request.story_type,
            acceptance_criteria=acceptance_criteria,
            tasks=tasks,
            priority=Priority.MEDIA,
            justificativa_prioridade="Prioridade média baseada na análise do contexto fornecido",
            estimation=5,
            justificativa_estimativa="Estimativa baseada na complexidade média identificada no contexto"
        )
        
    async def _generate_related_stories(self, request: StoryRequest, main_story: GeneratedStory) -> List[GeneratedStory]:
        """
        Gera histórias relacionadas a um épico baseado no contexto.
        
        Args:
            request: Dados da requisição
            main_story: História principal
            
        Returns:
            List[GeneratedStory]: Histórias relacionadas
        """
        related_stories = []
        context_lower = request.context.lower()
        
        # Se for sobre "Ideia no Bolso", gerar histórias específicas
        if "ideia no bolso" in context_lower or "inovação" in context_lower:
            related_stories = self._generate_innovation_related_stories(request)
        else:
            # Para outros contextos, gerar histórias relacionadas baseadas no contexto
            feature_keywords = self._extract_feature_keywords(request.context)
            related_stories = self._generate_contextual_related_stories(request, feature_keywords)
        
        return related_stories
    
    def _extract_feature_keywords(self, context: str) -> Dict[str, str]:
        """
        Extrai palavras-chave do contexto para gerar histórias mais precisas.
        
        Args:
            context: Contexto fornecido pelo usuário
            
        Returns:
            Dict[str, str]: Dicionário com palavras-chave extraídas
        """
        context_lower = context.lower()
        
        # Extrair funcionalidade principal
        main_feature = "funcionalidade"
        if "login" in context_lower or "autenticação" in context_lower:
            main_feature = "sistema de autenticação"
        elif "cadastro" in context_lower or "registro" in context_lower:
            main_feature = "sistema de cadastro"
        elif "relatório" in context_lower or "dashboard" in context_lower:
            main_feature = "sistema de relatórios"
        elif "pagamento" in context_lower or "transação" in context_lower:
            main_feature = "sistema de pagamentos"
        else:
            # Tentar extrair da primeira frase
            sentences = context.split('.')[0].split()
            if len(sentences) > 2:
                main_feature = ' '.join(sentences[:3])
        
        # Identificar tipo de usuário
        user_type = "usuário"
        if "administrador" in context_lower or "admin" in context_lower:
            user_type = "administrador"
        elif "cliente" in context_lower:
            user_type = "cliente"
        elif "colaborador" in context_lower:
            user_type = "colaborador"
        elif "gerente" in context_lower or "gestor" in context_lower:
            user_type = "gestor"
        
        # Identificar ação principal
        action = "utilizar a funcionalidade"
        if "criar" in context_lower or "cadastrar" in context_lower:
            action = "criar/cadastrar informações"
        elif "visualizar" in context_lower or "consultar" in context_lower:
            action = "visualizar/consultar dados"
        elif "editar" in context_lower or "alterar" in context_lower:
            action = "editar/alterar informações"
        elif "excluir" in context_lower or "remover" in context_lower:
            action = "excluir/remover dados"
        
        # Identificar benefício
        benefit = "atender aos requisitos do sistema"
        if "segurança" in context_lower:
            benefit = "garantir segurança do sistema"
        elif "eficiência" in context_lower or "produtividade" in context_lower:
            benefit = "melhorar eficiência e produtividade"
        elif "controle" in context_lower:
            benefit = "ter maior controle sobre as operações"
        
        return {
            "main_feature": main_feature,
            "user_type": user_type,
            "action": action,
            "benefit": benefit
        }
    
    def _generate_innovation_story(self, request: StoryRequest, story_id: str) -> GeneratedStory:
        """
        Gera história específica para o contexto "Ideia no Bolso".
        
        Args:
            request: Dados da requisição
            story_id: ID da história
            
        Returns:
            GeneratedStory: História gerada para inovação
        """
        if request.story_type == StoryType.EPIC:
            title = "Épico: Funcionalidade Ideia no Bolso"
            description = "Como banco digital inovador, queremos implementar a funcionalidade 'Ideia no Bolso' para permitir que colaboradores submetam ideias inovadoras, acompanhem seu status e interajam com outras ideias, promovendo uma cultura de inovação interna."
        elif request.story_type == StoryType.USER_STORY:
            title = "Como colaborador, eu quero submeter ideias inovadoras para contribuir com a inovação do banco"
            description = "Como colaborador do banco digital, eu quero poder submeter minhas ideias inovadoras através do app corporativo para que elas sejam avaliadas pelo time de inovação e possam contribuir para melhorias de produtos, serviços ou processos internos."
        else:
            title = "Implementar submissão de ideias no app corporativo"
            description = "Desenvolver a funcionalidade que permite aos colaboradores submeterem suas ideias através do aplicativo corporativo, incluindo formulário de submissão e validação inicial."
        
        # Critérios específicos para Ideia no Bolso
        acceptance_criteria = []
        if request.include_acceptance_criteria:
            acceptance_criteria = [
                AcceptanceCriteria(
                    given="Que o colaborador está autenticado no app corporativo",
                    when="Ele acessa a funcionalidade 'Ideia no Bolso'",
                    then="Ele deve conseguir visualizar o formulário de submissão de ideias"
                ),
                AcceptanceCriteria(
                    given="Que o colaborador preencheu todos os campos obrigatórios da ideia",
                    when="Ele clica em 'Submeter Ideia'",
                    then="O sistema deve salvar a ideia com status 'em análise' e enviar confirmação"
                ),
                AcceptanceCriteria(
                    given="Que a ideia foi submetida",
                    when="O status da ideia é alterado pelo time de inovação",
                    then="O colaborador deve receber notificação em tempo real sobre a mudança"
                )
            ]
        
        # Tarefas específicas para Ideia no Bolso com DetailedTask
        tasks = [
            DetailedTask(
                title="Criar interface de submissão de ideias",
                description="Desenvolver interface responsiva (web e mobile) para submissão de ideias pelos colaboradores",
                examples=["Formulário com campos: título, descrição, categoria, anexos", "Validação de campos obrigatórios"]
            ),
            DetailedTask(
                title="Implementar sistema de categorização",
                description="Criar sistema para categorizar ideias por tipo, área de negócio e impacto",
                examples=["Categorias: Produto, Processo, Tecnologia, Atendimento", "Tags personalizáveis"]
            ),
            DetailedTask(
                title="Desenvolver fluxo de validação",
                description="Implementar workflow de aprovação pelo time de inovação com comentários e feedbacks",
                examples=["Estados: Submetida, Em análise, Aprovada, Rejeitada", "Sistema de comentários"]
            ),
            DetailedTask(
                title="Criar sistema de notificações",
                description="Implementar notificações em tempo real para mudanças de status das ideias",
                examples=["Push notifications", "E-mail notifications", "Notificações in-app"]
            )
        ]
        
        return GeneratedStory(
            id=story_id,
            title=title,
            description=description,
            story_type=request.story_type,
            acceptance_criteria=acceptance_criteria,
            tasks=tasks,
            priority=Priority.ALTA,
            justificativa_prioridade="Alta prioridade devido ao impacto direto na cultura de inovação da empresa e engajamento dos colaboradores",
            estimation=8,
            justificativa_estimativa="Complexidade alta devido à necessidade de implementar múltiplas interfaces, integrações com sistemas existentes e workflow de aprovação"
        )
    
    def _generate_contextual_criteria(self, context: str) -> List[AcceptanceCriteria]:
        """
        Gera critérios de aceitação baseados no contexto fornecido.
        
        Args:
            context: Contexto da funcionalidade
            
        Returns:
            List[AcceptanceCriteria]: Lista de critérios contextuais
        """
        context_lower = context.lower()
        criteria = []
        
        # Critério básico de autenticação
        criteria.append(AcceptanceCriteria(
            given="Que o usuário possui credenciais válidas",
            when="Ele acessa a funcionalidade",
            then="Ele deve ser autenticado com sucesso"
        ))
        
        # Critérios específicos baseados no contexto
        if "formulário" in context_lower or "cadastro" in context_lower:
            criteria.append(AcceptanceCriteria(
                given="Que todos os campos obrigatórios foram preenchidos",
                when="O usuário submete o formulário",
                then="Os dados devem ser validados e salvos no sistema"
            ))
        
        if "notificação" in context_lower or "alerta" in context_lower:
            criteria.append(AcceptanceCriteria(
                given="Que uma ação relevante foi executada",
                when="O sistema processa a ação",
                then="Uma notificação deve ser enviada ao usuário apropriado"
            ))
        
        if "relatório" in context_lower or "dashboard" in context_lower:
            criteria.append(AcceptanceCriteria(
                given="Que existem dados disponíveis no sistema",
                when="O usuário solicita visualização de relatórios",
                then="Os dados devem ser apresentados de forma clara e organizada"
            ))
        
        return criteria
    
    def _generate_contextual_tasks(self, context: str) -> List[str]:
        """
        Gera tarefas baseadas no contexto fornecido.
        
        Args:
            context: Contexto da funcionalidade
            
        Returns:
            List[str]: Lista de tarefas contextuais
        """
        context_lower = context.lower()
        tasks = []
        
        # Tarefas básicas
        tasks.append("Criar interface de usuário responsiva")
        tasks.append("Implementar validações de entrada")
        tasks.append("Desenvolver lógica de negócio backend")
        tasks.append("Criar testes unitários e de integração")
        
        # Tarefas específicas baseadas no contexto
        if "banco de dados" in context_lower or "persistência" in context_lower:
            tasks.append("Modelar e criar estruturas no banco de dados")
            tasks.append("Implementar camada de acesso a dados")
        
        if "api" in context_lower or "integração" in context_lower:
            tasks.append("Desenvolver endpoints REST")
            tasks.append("Implementar integração com sistemas externos")
        
        if "autenticação" in context_lower or "segurança" in context_lower:
            tasks.append("Implementar sistema de autenticação e autorização")
            tasks.append("Configurar políticas de segurança")
        
        if "mobile" in context_lower:
            tasks.append("Adaptar interface para dispositivos móveis")
            tasks.append("Implementar funcionalidades específicas mobile")
        
        if "relatório" in context_lower or "dashboard" in context_lower:
            tasks.append("Criar visualizações de dados")
            tasks.append("Implementar filtros e exportação")
        
        return tasks
    
    def _generate_contextual_detailed_tasks(self, context: str) -> List[DetailedTask]:
        """
        Gera tarefas detalhadas baseadas no contexto fornecido.
        
        Args:
            context: Contexto da funcionalidade
            
        Returns:
            List[DetailedTask]: Lista de tarefas detalhadas contextuais
        """
        context_lower = context.lower()
        tasks = []
        
        # Tarefas básicas
        tasks.append(DetailedTask(
            title="Criar interface de usuário",
            description="Desenvolver interface responsiva e acessível para a funcionalidade",
            examples=["Design system consistente", "Responsividade mobile-first", "Acessibilidade WCAG"]
        ))
        
        tasks.append(DetailedTask(
            title="Implementar validações",
            description="Desenvolver validações de entrada e regras de negócio",
            examples=["Validação de campos obrigatórios", "Sanitização de dados", "Feedback de erro"]
        ))
        
        # Tarefas específicas baseadas no contexto
        if "banco de dados" in context_lower or "persistência" in context_lower:
            tasks.append(DetailedTask(
                title="Modelar estruturas de dados",
                description="Criar modelos de dados e estruturas no banco de dados",
                examples=["Diagrama ER", "Scripts de migração", "Índices para performance"]
            ))
        
        if "api" in context_lower or "integração" in context_lower:
            tasks.append(DetailedTask(
                title="Desenvolver endpoints REST",
                description="Implementar APIs RESTful para comunicação entre sistemas",
                examples=["Documentação OpenAPI", "Versionamento de API", "Rate limiting"]
            ))
        
        if "autenticação" in context_lower or "segurança" in context_lower:
            tasks.append(DetailedTask(
                title="Implementar segurança",
                description="Configurar autenticação, autorização e políticas de segurança",
                examples=["JWT tokens", "RBAC permissions", "Audit logs"]
            ))
        
        return tasks
    
    def _generate_innovation_related_stories(self, request: StoryRequest) -> List[GeneratedStory]:
        """
        Gera histórias relacionadas específicas para o contexto "Ideia no Bolso".
        
        Args:
            request: Dados da requisição
            
        Returns:
            List[GeneratedStory]: Histórias relacionadas para inovação
        """
        related_stories = []
        
        # História 1: Validação pelo time de inovação
        story1 = GeneratedStory(
            id=str(uuid.uuid4()),
            title="Como membro do time de inovação, eu quero validar ideias submetidas para garantir qualidade e alinhamento estratégico",
            description="Como membro do time de inovação, eu quero ter acesso a um painel para revisar, comentar e aprovar/reprovar ideias submetidas pelos colaboradores, para garantir que apenas ideias viáveis e alinhadas com a estratégia sejam encaminhadas para desenvolvimento.",
            story_type=StoryType.USER_STORY,
            acceptance_criteria=[
                AcceptanceCriteria(
                    given="Que existem ideias aguardando validação",
                    when="Eu acesso o painel de validação",
                    then="Devo visualizar todas as ideias pendentes com seus detalhes"
                ),
                AcceptanceCriteria(
                    given="Que estou analisando uma ideia",
                    when="Eu aprovar ou reprovar a ideia",
                    then="O sistema deve atualizar o status e notificar o colaborador"
                )
            ],
            tasks=[
                DetailedTask(
                    title="Criar painel de validação",
                    description="Desenvolver interface para o time de inovação revisar e validar ideias submetidas",
                    examples=["Lista de ideias pendentes", "Formulário de feedback", "Sistema de aprovação/reprovação"]
                ),
                DetailedTask(
                    title="Implementar sistema de comentários",
                    description="Criar funcionalidade para adicionar comentários e feedback nas ideias",
                    examples=["Editor de texto rico", "Histórico de comentários", "Notificações de novos comentários"]
                )
            ],
            priority=Priority.ALTA,
            justificativa_prioridade="Alta prioridade para garantir qualidade das ideias aprovadas",
            estimation=5,
            justificativa_estimativa="Complexidade média considerando interface administrativa e workflow de aprovação"
        )
        
        # História 2: Dashboard administrativo
        story2 = GeneratedStory(
            id=str(uuid.uuid4()),
            title="Como gestor de inovação, eu quero visualizar métricas das ideias para tomar decisões estratégicas",
            description="Como gestor de inovação, eu quero ter acesso a um dashboard com métricas como número de ideias por mês, áreas mais ativas, taxa de aprovação e outros indicadores, para poder tomar decisões estratégicas sobre o programa de inovação.",
            story_type=StoryType.USER_STORY,
            acceptance_criteria=[
                AcceptanceCriteria(
                    given="Que existem dados de ideias no sistema",
                    when="Eu acesso o dashboard administrativo",
                    then="Devo visualizar métricas consolidadas com filtros por período e categoria"
                ),
                AcceptanceCriteria(
                    given="Que quero analisar dados específicos",
                    when="Eu aplico filtros no dashboard",
                    then="Os dados devem ser atualizados em tempo real conforme os filtros"
                )
            ],
            tasks=[
                DetailedTask(
                    title="Criar dashboard com visualizações de dados",
                    description="Desenvolver interface gráfica com charts e métricas visuais para o dashboard administrativo",
                    examples=["Gráficos de barras", "Charts de pizza", "Tabelas interativas"]
                ),
                DetailedTask(
                    title="Implementar métricas de engajamento e aprovação",
                    description="Desenvolver cálculos e indicadores de performance do programa de inovação",
                    examples=["Taxa de aprovação por categoria", "Tempo médio de análise", "Ranking de colaboradores"]
                ),
                DetailedTask(
                    title="Desenvolver sistema de filtros",
                    description="Implementar filtros dinâmicos por categoria, período, área e status das ideias",
                    examples=["Filtro por data range", "Filtro por departamento", "Filtro por status"]
                ),
                DetailedTask(
                    title="Implementar funcionalidade de exportação",
                    description="Desenvolver exportação de dados em múltiplos formatos (Excel, PDF, CSV)",
                    examples=["Export to Excel", "Export to PDF", "Scheduled reports"]
                )
            ],
            priority=Priority.MEDIA,
            justificativa_prioridade="Prioridade média devido à importância para gestão, mas não é crítica para o funcionamento básico",
            estimation=8,
            justificativa_estimativa="8 story points devido à complexidade de implementar dashboards com múltiplas visualizações e sistema de filtros avançados"
        )
        
        related_stories.extend([story1, story2])
        return related_stories
    
    def _generate_contextual_related_stories(self, request: StoryRequest, feature_keywords: Dict[str, str]) -> List[GeneratedStory]:
        """
        Gera histórias relacionadas baseadas no contexto geral.
        
        Args:
            request: Dados da requisição
            feature_keywords: Palavras-chave extraídas do contexto
            
        Returns:
            List[GeneratedStory]: Histórias relacionadas contextuais
        """
        related_stories = []
        
        # História relacionada 1: Interface administrativa
        story1 = GeneratedStory(
            id=str(uuid.uuid4()),
            title=f"Como administrador, eu quero gerenciar {feature_keywords['main_feature']} para manter o controle do sistema",
            description=f"Como administrador do sistema, eu quero ter uma interface para gerenciar e configurar {feature_keywords['main_feature']}, incluindo permissões, configurações e monitoramento.",
            story_type=StoryType.USER_STORY,
            acceptance_criteria=[
                AcceptanceCriteria(
                    given="Que tenho permissões de administrador",
                    when="Acesso o painel administrativo",
                    then="Devo ter acesso a todas as configurações do sistema"
                )
            ],
            tasks=[
                "Criar interface administrativa",
                "Implementar controle de permissões",
                "Desenvolver funcionalidades de configuração"
            ],
            priority="Média",
            estimation="5 Story Points"
        )
        
        # História relacionada 2: Relatórios e monitoramento
        story2 = GeneratedStory(
            id=str(uuid.uuid4()),
            title=f"Como {feature_keywords['user_type']}, eu quero visualizar relatórios sobre {feature_keywords['main_feature']} para acompanhar o desempenho",
            description=f"Como {feature_keywords['user_type']}, eu quero ter acesso a relatórios e métricas sobre o uso de {feature_keywords['main_feature']} para poder acompanhar o desempenho e tomar decisões informadas.",
            story_type=StoryType.USER_STORY,
            acceptance_criteria=[
                AcceptanceCriteria(
                    given="Que existem dados no sistema",
                    when="Solicito relatórios",
                    then="Devo visualizar dados organizados e filtráveis"
                )
            ],
            tasks=[
                "Implementar geração de relatórios",
                "Criar visualizações de dados",
                "Desenvolver filtros e exportação"
            ],
            priority="Baixa",
            estimation="3 Story Points"
        )
        
        related_stories.extend([story1, story2])
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
