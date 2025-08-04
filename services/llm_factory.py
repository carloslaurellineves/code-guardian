"""
Factory para inicialização de LLM com fallback para ambiente local.

Este módulo implementa a lógica de fallback que verifica primeiro
se há credenciais do Azure OpenAI disponíveis. Caso não existam,
utiliza automaticamente o LLM da OpenAI padrão via LangChain.
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
    do provedor adequado (Azure OpenAI ou OpenAI padrão).

    Atualizado para incluir geração de histórias com detalhes e justificativas.
    """
    
    def __init__(self):
        """Inicializa o factory com logger configurado."""
        self.logger = logging.getLogger(__name__)
    
    def _check_azure_credentials(self) -> bool:
        """
        Verifica se todas as credenciais necessárias do Azure OpenAI estão presentes.
        
        Returns:
            bool: True se todas as credenciais estão disponíveis, False caso contrário
        """
        required_vars = [
            "AZURE_OPENAI_API_KEY",
            "AZURE_OPENAI_API_BASE", 
            "AZURE_OPENAI_DEPLOYMENT_NAME",
            "AZURE_OPENAI_API_VERSION"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            self.logger.info(
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
            self.logger.error(
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
            azure_llm = AzureChatOpenAI(
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                azure_endpoint=os.getenv("AZURE_OPENAI_API_BASE"),
                deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
                api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
                temperature=0.7,
                max_tokens=15000,
                timeout=120,  # 2 minutos de timeout para chamadas LLM
                max_retries=3
            )
            
            self.logger.info(
                f"✅ Azure OpenAI inicializado com sucesso - "
                f"Endpoint: {os.getenv('AZURE_OPENAI_API_BASE')} | "
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
    
    def load_llm(self) -> BaseChatModel:
        """
        Carrega uma instância de LLM com fallback automático.
        
        Verifica primeiro se as credenciais do Azure OpenAI estão disponíveis.
        Caso não estejam, tenta utilizar a OpenAI padrão.
        Se nenhuma estiver disponível, levanta uma exceção.
        
        Returns:
            BaseChatModel: Instância configurada do LLM (Azure ou OpenAI padrão)
            
        Raises:
            LLMInitializationError: Quando nenhum provedor pode ser inicializado
        """
        self.logger.info("🔄 Iniciando processo de carregamento do LLM...")
        
        # Primeira tentativa: Azure OpenAI
        if self._check_azure_credentials():
            try:
                return self._create_azure_llm()
            except LLMInitializationError:
                self.logger.warning("⚠️ Falha no Azure OpenAI, tentando fallback...")
        
        # Segunda tentativa: OpenAI padrão
        if self._check_openai_credentials():
            try:
                return self._create_openai_llm()
            except LLMInitializationError:
                self.logger.error("❌ Falha também na OpenAI padrão")
        
        # Nenhum provedor disponível
        error_msg = (
            "❌ Nenhum provedor LLM pode ser inicializado. "
            "Verifique as variáveis de ambiente:\n"
            "Para Azure OpenAI: AZURE_OPENAI_API_KEY, AZURE_OPENAI_API_BASE, "
            "AZURE_OPENAI_DEPLOYMENT_NAME, AZURE_OPENAI_API_VERSION\n"
            "Para OpenAI padrão: OPENAI_API_KEY, OPENAI_MODEL_NAME"
        )
        
        self.logger.error(error_msg)
        raise LLMInitializationError(error_msg)


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
