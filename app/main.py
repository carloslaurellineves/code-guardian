"""
Servidor FastAPI principal para a aplicação Code Guardian.

Este módulo configura o servidor FastAPI e registra as rotas da API.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from api.routers import health, story_creator, code_tester, code_fixer


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerenciador de contexto para o ciclo de vida da aplicação.
    
    Args:
        app: Instância do FastAPI
    """
    # Inicialização
    print("🚀 Code Guardian API iniciando...")
    yield
    # Finalização
    print("🛑 Code Guardian API finalizando...")


def create_app() -> FastAPI:
    """
    Cria e configura a aplicação FastAPI.
    
    Returns:
        FastAPI: Instância configurada da aplicação
    """
    app = FastAPI(
        title="Code Guardian API",
        description="API para geração automatizada de testes unitários e correção de código",
        version="0.1.0",
        lifespan=lifespan
    )
    
    # Configuração CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Em produção, especificar origens permitidas
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Registro das rotas
    app.include_router(health.router, prefix="/api/v1", tags=["health"])
    app.include_router(story_creator.router, prefix="/api/v1", tags=["story-creator"])
    app.include_router(code_tester.router, prefix="/api/v1", tags=["code-tester"])
    app.include_router(code_fixer.router, prefix="/api/v1", tags=["code-fixer"])
    
    return app


# Instância da aplicação
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
