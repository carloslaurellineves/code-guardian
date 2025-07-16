"""
Configuração de logging para a aplicação Code Guardian.

Este módulo implementa a configuração estruturada de logs
seguindo os padrões corporativos da instituição.
"""

import logging
import logging.config
import os
from datetime import datetime
from typing import Dict, Any


def setup_logging(level: str = "INFO", log_dir: str = "logs") -> None:
    """
    Configura o sistema de logging da aplicação.
    
    Args:
        level: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Diretório para armazenar os arquivos de log
    """
    # Criar diretório de logs se não existir
    os.makedirs(log_dir, exist_ok=True)
    
    # Configuração do logging
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(lineno)d - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": level,
                "formatter": "standard",
                "stream": "ext://sys.stdout"
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": level,
                "formatter": "detailed",
                "filename": os.path.join(log_dir, "code_guardian.log"),
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "ERROR",
                "formatter": "detailed",
                "filename": os.path.join(log_dir, "code_guardian_errors.log"),
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5
            }
        },
        "loggers": {
            "": {
                "handlers": ["console", "file", "error_file"],
                "level": level,
                "propagate": False
            },
            "uvicorn": {
                "handlers": ["console", "file"],
                "level": "INFO",
                "propagate": False
            },
            "fastapi": {
                "handlers": ["console", "file"],
                "level": "INFO",
                "propagate": False
            }
        }
    }
    
    logging.config.dictConfig(logging_config)
    
    # Log inicial
    logger = logging.getLogger(__name__)
    logger.info("Sistema de logging configurado com sucesso")
    logger.info(f"Nível de log: {level}")
    logger.info(f"Diretório de logs: {log_dir}")


def get_logger(name: str) -> logging.Logger:
    """
    Obtém um logger configurado.
    
    Args:
        name: Nome do logger
        
    Returns:
        logging.Logger: Logger configurado
    """
    return logging.getLogger(name)


def log_api_request(method: str, endpoint: str, status_code: int, 
                   processing_time: float, user_id: str = None) -> None:
    """
    Registra informações de requisições da API.
    
    Args:
        method: Método HTTP
        endpoint: Endpoint acessado
        status_code: Código de status da resposta
        processing_time: Tempo de processamento
        user_id: ID do usuário (opcional)
    """
    logger = get_logger("api_requests")
    
    log_data = {
        "method": method,
        "endpoint": endpoint,
        "status_code": status_code,
        "processing_time": processing_time,
        "timestamp": datetime.now().isoformat()
    }
    
    if user_id:
        log_data["user_id"] = user_id
    
    logger.info(f"API Request: {log_data}")


def log_agent_execution(agent_name: str, operation: str, 
                       success: bool, processing_time: float,
                       metadata: Dict[str, Any] = None) -> None:
    """
    Registra informações de execução de agentes.
    
    Args:
        agent_name: Nome do agente
        operation: Operação executada
        success: Se a operação foi bem-sucedida
        processing_time: Tempo de processamento
        metadata: Metadados adicionais
    """
    logger = get_logger("agent_execution")
    
    log_data = {
        "agent_name": agent_name,
        "operation": operation,
        "success": success,
        "processing_time": processing_time,
        "timestamp": datetime.now().isoformat()
    }
    
    if metadata:
        log_data["metadata"] = metadata
    
    level = logging.INFO if success else logging.ERROR
    logger.log(level, f"Agent Execution: {log_data}")
