"""
Módulo de routers para a API Code Guardian.

Este módulo organiza as rotas da API em diferentes módulos
para melhor organização e manutenibilidade.
"""

from . import health
from . import story_creator
from . import code_tester
from . import code_fixer

__all__ = [
    "health",
    "story_creator", 
    "code_tester",
    "code_fixer"
]
