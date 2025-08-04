"""
Funções auxiliares para a aplicação Code Guardian.

Este módulo contém funções utilitárias utilizadas
em toda a aplicação para tarefas comuns.
"""

import uuid
import hashlib
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def generate_uuid() -> str:
    """
    Gera um UUID único.
    
    Returns:
        str: UUID gerado
    """
    return str(uuid.uuid4())


def generate_hash(content: str) -> str:
    """
    Gera um hash SHA-256 do conteúdo.
    
    Args:
        content: Conteúdo a ser hasheado
        
    Returns:
        str: Hash SHA-256
    """
    return hashlib.sha256(content.encode()).hexdigest()


def format_datetime(dt: datetime) -> str:
    """
    Formata uma data/hora para string ISO.
    
    Args:
        dt: Data/hora a ser formatada
        
    Returns:
        str: Data/hora formatada
    """
    return dt.isoformat()


def get_current_timestamp() -> datetime:
    """
    Obtém o timestamp atual em UTC.
    
    Returns:
        datetime: Timestamp atual
    """
    return datetime.now(timezone.utc)


def sanitize_filename(filename: str) -> str:
    """
    Sanitiza um nome de arquivo removendo caracteres perigosos.
    
    Args:
        filename: Nome do arquivo
        
    Returns:
        str: Nome do arquivo sanitizado
    """
    # Remover caracteres perigosos
    dangerous_chars = '<>:"/\\|?*'
    for char in dangerous_chars:
        filename = filename.replace(char, '_')
    
    # Remover espaços duplos
    filename = ' '.join(filename.split())
    
    # Limitar tamanho
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:255 - len(ext) - 1] + '.' + ext if ext else name[:255]
    
    return filename


def extract_file_extension(filename: str) -> str:
    """
    Extrai a extensão de um arquivo.
    
    Args:
        filename: Nome do arquivo
        
    Returns:
        str: Extensão do arquivo (com o ponto)
    """
    return '.' + filename.split('.')[-1] if '.' in filename else ''


def calculate_file_size_mb(content: str) -> float:
    """
    Calcula o tamanho do conteúdo em MB.
    
    Args:
        content: Conteúdo do arquivo
        
    Returns:
        float: Tamanho em MB
    """
    return len(content.encode()) / (1024 * 1024)


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Trunca um texto para um tamanho máximo, se necessário.
    
    Args:
        text: Texto a ser truncado
        max_length: Tamanho máximo
        suffix: Sufixo a ser adicionado
        
    Returns:
        str: Texto truncado ou original se dentro do limite
    """
    if len(text) <= max_length or max_length < 0:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def deep_merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Faz merge profundo de dois dicionários.
    
    Args:
        dict1: Primeiro dicionário
        dict2: Segundo dicionário
        
    Returns:
        Dict[str, Any]: Dicionário resultante do merge
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result


def filter_dict_by_keys(data: Dict[str, Any], keys: List[str]) -> Dict[str, Any]:
    """
    Filtra um dicionário mantendo apenas as chaves especificadas.
    
    Args:
        data: Dicionário original
        keys: Lista de chaves a manter
        
    Returns:
        Dict[str, Any]: Dicionário filtrado
    """
    return {key: data[key] for key in keys if key in data}


def remove_empty_values(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Remove valores vazios de um dicionário.
    
    Args:
        data: Dicionário original
        
    Returns:
        Dict[str, Any]: Dicionário sem valores vazios
    """
    return {
        key: value for key, value in data.items()
        if value is not None and value != "" and value != [] and value != {}
    }


def format_processing_time(seconds: float) -> str:
    """
    Formata tempo de processamento para exibição.
    
    Args:
        seconds: Tempo em segundos
        
    Returns:
        str: Tempo formatado
    """
    if seconds < 1:
        return f"{seconds * 1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.2f}s"
    else:
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds:.2f}s"


def validate_environment_variables(required_vars: List[str]) -> Dict[str, Any]:
    """
    Valida se as variáveis de ambiente necessárias estão definidas.
    
    Args:
        required_vars: Lista de variáveis obrigatórias
        
    Returns:
        Dict[str, Any]: Resultado da validação
    """
    import os
    
    missing_vars = []
    present_vars = []
    
    for var in required_vars:
        if os.getenv(var):
            present_vars.append(var)
        else:
            missing_vars.append(var)
    
    return {
        "valid": len(missing_vars) == 0,
        "missing_vars": missing_vars,
        "present_vars": present_vars
    }
