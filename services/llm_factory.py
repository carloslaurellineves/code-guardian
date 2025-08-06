"""
Factory para inicialização de LLM com fallback inteligente.

Este módulo implementa a lógica de fallback que prioriza Azure OpenAI
se disponível, e utiliza OpenAI padrão como fallback. Garante que a
aplicação funcione tanto em ambiente corporativo quanto pessoal.
"""

import os
import logging
from typing import Optional
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

try:
    from langchain_openai import ChatOpenAI, AzureChatOpenAI
    from langchain_core.language_models.chat_models import BaseChatModel
except ImportError:
    raise ImportError(
        "LangChain OpenAI não está instalado. Execute: pip install langchain-openai"
    )


class LLMInitializationError(Exception):
    """Exceção levantada quando não é possível inicializar nenhum provedor LLM."""
    pass


class LLMFactory:
    """
    Factory responsável pela criação de instâncias LLM com fallback automático.
    
    Implementa a lógica de verificação de credenciais e inicialização
    do provedor adequado com prioridade para Azure OpenAI em ambiente corporativo.

    Lógica de fallback:
    1. Tenta Azure OpenAI se credenciais estiverem disponíveis
    2. Tenta OpenAI padrão como fallback
    3. Falha apenas se nenhum dos dois estiver configurado
    """
    
    def __init__(self):
        """Inicializa o factory com logger configurado."""
        self.logger = logging.getLogger(__name__)
    
    def _check_azure_credentials(self) -> bool:
        """
        Verifica se todas as credenciais necessárias do Azure OpenAI estão presentes.
        
        Suporta tanto AZURE_OPENAI_ENDPOINT quanto AZURE_OPENAI_API_BASE para
        compatibilidade com diferentes configurações.
        
        Returns:
            bool: True se todas as credenciais estão disponíveis, False caso contrário
        """
        # Variáveis obrigatórias
        required_vars = [
            "AZURE_OPENAI_API_KEY",
            "AZURE_OPENAI_DEPLOYMENT_NAME",
            "AZURE_OPENAI_API_VERSION"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        # Verificar se pelo menos um dos endpoints está configurado
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT") or os.getenv("AZURE_OPENAI_API_BASE")
        if not endpoint:
            missing_vars.append("AZURE_OPENAI_ENDPOINT ou AZURE_OPENAI_API_BASE")
        
        if missing_vars:
            self.logger.debug(
                f"Credenciais do Azure OpenAI ausentes: {', '.join(missing_vars)}. "
                "Tentando fallback para OpenAI padrão."
            )
            return False
        
        return True
    
    def _check_openai_credentials(self) -> bool:
        """
        Verifica se as credenciais necessárias da OpenAI padrão estão presentes.
        
        Returns:
            bool: True se as credenciais estão disponíveis, False caso contrário
        """
        required_vars = ["OPENAI_API_KEY", "OPENAI_MODEL_NAME"]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            self.logger.debug(
                f"Credenciais da OpenAI padrão ausentes: {', '.join(missing_vars)}."
            )
            return False
        
        return True
    
    def _create_azure_llm(self) -> AzureChatOpenAI:
        """
        Cria uma instância do Azure OpenAI LLM.
        
        Returns:
            AzureChatOpenAI: Instância configurada do Azure OpenAI
        """
        try:
            # Suportar tanto AZURE_OPENAI_ENDPOINT quanto AZURE_OPENAI_API_BASE
            endpoint = os.getenv("AZURE_OPENAI_ENDPOINT") or os.getenv("AZURE_OPENAI_API_BASE")
            
            azure_llm = AzureChatOpenAI(
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                azure_endpoint=endpoint,
                deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
                api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
                temperature=0.7,
                max_tokens=15000,
                timeout=120,  # 2 minutos de timeout para chamadas LLM
                max_retries=3
            )
            
            self.logger.info(
                f"✅ Azure OpenAI inicializado com sucesso - "
                f"Endpoint: {endpoint} | "
                f"Deployment: {os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')}"
            )
            
            return azure_llm
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao inicializar Azure OpenAI: {e}")
            raise LLMInitializationError(f"Falha na inicialização do Azure OpenAI: {e}")
    
    def _create_openai_llm(self) -> ChatOpenAI:
        """
        Cria uma instância do OpenAI padrão LLM.
        
        Returns:
            ChatOpenAI: Instância configurada da OpenAI padrão
        """
        try:
            openai_llm = ChatOpenAI(
                api_key=os.getenv("OPENAI_API_KEY"),
                model=os.getenv("OPENAI_MODEL_NAME", "gpt-4"),
                temperature=0.7,
                max_tokens=15000,
                timeout=120,  # 2 minutos de timeout para chamadas LLM
                max_retries=3
            )
            
            self.logger.info(
                f"✅ OpenAI padrão inicializado com sucesso - "
                f"Modelo: {os.getenv('OPENAI_MODEL_NAME', 'gpt-4')}"
            )
            
            return openai_llm
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao inicializar OpenAI padrão: {e}")
            raise LLMInitializationError(f"Falha na inicialização da OpenAI padrão: {e}")
    
    def initialize_llm_provider(self) -> BaseChatModel:
        """
        Inicializa um provedor LLM adequado com lógica de fallback inteligente.
        
        A função tenta primeiro utilizar Azure OpenAI se estiver configurado.
        Se o Azure não estiver disponível, utiliza OpenAI padrão como fallback.
        Apenas emite erro se nenhum dos dois estiver configurado corretamente.
        
        Returns:
            BaseChatModel: Instância configurada do LLM (Azure ou OpenAI padrão)
            
        Raises:
            LLMInitializationError: Quando nenhum provedor pode ser inicializado
        """
        self.logger.info("🔄 Iniciando processo de inicialização do LLM...")
        
        # Verificar e tentar Azure OpenAI primeiro
        azure_available = self._check_azure_credentials()
        if azure_available:
            try:
                self.logger.info("✅ Credenciais Azure OpenAI detectadas, inicializando...")
                return self._create_azure_llm()
            except LLMInitializationError as e:
                self.logger.warning(f"⚠️ Falha no Azure OpenAI: {e}, tentando fallback...")
        
        # Tentar OpenAI padrão como fallback
        openai_available = self._check_openai_credentials()
        if openai_available:
            try:
                self.logger.info("✅ Credenciais OpenAI padrão detectadas, inicializando...")
                return self._create_openai_llm()
            except LLMInitializationError as e:
                self.logger.error(f"❌ Falha também na OpenAI padrão: {e}")
        
        # Nenhum provedor disponível - gerar mensagem de erro apropriada
        error_parts = ["❌ Nenhum provedor LLM pode ser inicializado."]
        
        if not azure_available and not openai_available:
            error_parts.append("Nenhuma credencial de LLM configurada no ambiente.")
        elif not azure_available:
            error_parts.append("Credenciais Azure OpenAI ausentes ou incompletas.")
        elif not openai_available:
            error_parts.append("Credenciais OpenAI padrão ausentes ou incompletas.")
        
        error_parts.append(
            "Configure pelo menos um dos seguintes conjuntos de variáveis no arquivo .env:\n"
            "- Azure OpenAI: AZURE_OPENAI_API_KEY, AZURE_OPENAI_API_BASE, "
            "AZURE_OPENAI_DEPLOYMENT_NAME, AZURE_OPENAI_API_VERSION\n"
            "- OpenAI padrão: OPENAI_API_KEY, OPENAI_MODEL_NAME"
        )
        
        error_msg = " ".join(error_parts)
        self.logger.error(error_msg)
        raise LLMInitializationError(error_msg)
        
    def load_llm(self) -> BaseChatModel:
        """
        Carrega uma instância de LLM com fallback automático.
        
        Mantido por compatibilidade com código existente.
        Redireciona para o novo método initialize_llm_provider().
        
        Returns:
            BaseChatModel: Instância configurada do LLM (Azure ou OpenAI padrão)
            
        Raises:
            LLMInitializationError: Quando nenhum provedor pode ser inicializado
        """
        return self.initialize_llm_provider()


# Novos prompts integrados para StoryCreator
# O LLM agora deve gerar histórias mais detalhadas, incluindo explicações para prioridade e estimativa.


# Instância global do factory
llm_factory = LLMFactory()


def load_llm() -> BaseChatModel:
    """
    Função de conveniência para carregar o LLM.
    
    Returns:
        BaseChatModel: Instância configurada do LLM
        
    Raises:
        LLMInitializationError: Quando nenhum provedor pode ser inicializado
    """
    return llm_factory.load_llm()
