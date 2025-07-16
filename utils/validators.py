"""
Validadores de entrada para a aplicação Code Guardian.

Este módulo implementa validações customizadas para
diferentes tipos de entrada utilizados na aplicação.
"""

import re
from typing import Dict, Any, List
from urllib.parse import urlparse


def validate_code(code: str, language: str = "python") -> Dict[str, Any]:
    """
    Valida um código fornecido.
    
    Args:
        code: Código a ser validado
        language: Linguagem de programação
        
    Returns:
        Dict[str, Any]: Resultado da validação
    """
    issues = []
    
    # Validações básicas
    if not code or not code.strip():
        issues.append("Código não pode estar vazio")
        
    if len(code) < 10:
        issues.append("Código muito curto para análise")
        
    if len(code) > 100000:  # 100KB
        issues.append("Código muito longo para processamento")
        
    # Validações específicas por linguagem
    if language == "python":
        issues.extend(_validate_python_code(code))
    elif language == "javascript":
        issues.extend(_validate_javascript_code(code))
    elif language == "java":
        issues.extend(_validate_java_code(code))
        
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "language": language,
        "size": len(code)
    }


def _validate_python_code(code: str) -> List[str]:
    """
    Valida código Python específico.
    
    Args:
        code: Código Python
        
    Returns:
        List[str]: Lista de problemas encontrados
    """
    issues = []
    
    # Verificar sintaxe básica
    try:
        compile(code, '<string>', 'exec')
    except SyntaxError as e:
        issues.append(f"Erro de sintaxe: {str(e)}")
        
    # Verificar padrões perigosos
    dangerous_patterns = [
        r'\beval\s*\(',
        r'\bexec\s*\(',
        r'\b__import__\s*\(',
        r'\bopen\s*\(',
        r'\bfile\s*\('
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, code):
            issues.append(f"Padrão perigoso detectado: {pattern}")
            
    return issues


def _validate_javascript_code(code: str) -> List[str]:
    """
    Valida código JavaScript específico.
    
    Args:
        code: Código JavaScript
        
    Returns:
        List[str]: Lista de problemas encontrados
    """
    issues = []
    
    # Verificar padrões perigosos
    dangerous_patterns = [
        r'\beval\s*\(',
        r'\bFunction\s*\(',
        r'\bdocument\.write\s*\(',
        r'\binnerHTML\s*='
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, code):
            issues.append(f"Padrão perigoso detectado: {pattern}")
            
    return issues


def _validate_java_code(code: str) -> List[str]:
    """
    Valida código Java específico.
    
    Args:
        code: Código Java
        
    Returns:
        List[str]: Lista de problemas encontrados
    """
    issues = []
    
    # Verificar padrões perigosos
    dangerous_patterns = [
        r'\bRuntime\.getRuntime\(\)',
        r'\bProcessBuilder\s*\(',
        r'\bSystem\.exit\s*\(',
        r'\bReflection\.'
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, code):
            issues.append(f"Padrão perigoso detectado: {pattern}")
            
    return issues


def validate_repository_url(url: str) -> Dict[str, Any]:
    """
    Valida uma URL de repositório.
    
    Args:
        url: URL do repositório
        
    Returns:
        Dict[str, Any]: Resultado da validação
    """
    issues = []
    
    if not url or not url.strip():
        issues.append("URL não pode estar vazia")
        return {"valid": False, "issues": issues}
        
    try:
        parsed = urlparse(url)
        
        # Verificar se tem esquema
        if not parsed.scheme:
            issues.append("URL deve ter esquema (http/https)")
            
        # Verificar se tem host
        if not parsed.netloc:
            issues.append("URL deve ter um host válido")
            
        # Verificar se é GitLab
        if "gitlab" not in parsed.netloc.lower():
            issues.append("URL deve ser de um repositório GitLab")
            
        # Verificar se termina com .git ou tem formato válido
        if not (url.endswith('.git') or '/tree/' in url or '/blob/' in url):
            issues.append("URL deve ser um repositório Git válido")
            
    except Exception as e:
        issues.append(f"Erro ao validar URL: {str(e)}")
        
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "parsed_url": parsed._asdict() if 'parsed' in locals() else None
    }


def validate_file_upload(file_name: str, file_content: str, max_size: int = 1024 * 1024) -> Dict[str, Any]:
    """
    Valida um arquivo enviado.
    
    Args:
        file_name: Nome do arquivo
        file_content: Conteúdo do arquivo
        max_size: Tamanho máximo em bytes
        
    Returns:
        Dict[str, Any]: Resultado da validação
    """
    issues = []
    
    if not file_name:
        issues.append("Nome do arquivo é obrigatório")
        
    if not file_content:
        issues.append("Conteúdo do arquivo é obrigatório")
        
    if len(file_content) > max_size:
        issues.append(f"Arquivo muito grande (máximo: {max_size} bytes)")
        
    # Verificar extensão
    allowed_extensions = ['.py', '.js', '.ts', '.java', '.cs', '.go', '.php', '.rb', '.cpp', '.c', '.h']
    if not any(file_name.endswith(ext) for ext in allowed_extensions):
        issues.append("Extensão de arquivo não suportada")
        
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "file_name": file_name,
        "file_size": len(file_content)
    }
