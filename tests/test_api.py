"""
Testes básicos da API Code Guardian.

Este módulo contém testes para validar o funcionamento
básico dos endpoints da API.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    """
    Testa o endpoint de health check.
    """
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert data["version"] == "0.1.0"


def test_detailed_health_check():
    """
    Testa o endpoint de health check detalhado.
    """
    response = client.get("/api/v1/health/detailed")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"
    assert "components" in data
    assert "api" in data["components"]
    assert data["components"]["api"]["status"] == "healthy"


def test_story_templates():
    """
    Testa o endpoint de templates de histórias.
    """
    response = client.get("/api/v1/stories/templates")
    assert response.status_code == 200
    
    data = response.json()
    assert "templates" in data
    assert "epic" in data["templates"]
    assert "user_story" in data["templates"]
    assert "task" in data["templates"]


def test_generate_story():
    """
    Testa a geração de histórias.
    """
    story_request = {
        "context": "Sistema de autenticação para aplicação web",
        "story_type": "user_story",
        "include_acceptance_criteria": True,
        "language": "pt-BR"
    }
    
    response = client.post("/api/v1/stories/generate", json=story_request)
    assert response.status_code == 201
    
    data = response.json()
    assert data["success"] is True
    assert "stories" in data
    assert len(data["stories"]) > 0
    assert "processing_time" in data


def test_generate_tests():
    """
    Testa a geração de testes unitários.
    """
    test_request = {
        "input_type": "direct",
        "code_content": "def soma(a, b):\n    return a + b",
        "language": "python",
        "test_framework": "pytest"
    }
    
    response = client.post("/api/v1/code/tests/generate", json=test_request)
    assert response.status_code == 201
    
    data = response.json()
    assert data["success"] is True
    assert "tests" in data
    assert len(data["tests"]) > 0
    assert "analysis" in data


def test_fix_bugs():
    """
    Testa a correção de bugs.
    """
    bug_request = {
        "code_with_bug": "def divide(a, b):\n    return a / b",
        "error_description": "Division by zero error",
        "language": "python"
    }
    
    response = client.post("/api/v1/fix/bugs", json=bug_request)
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    assert "fixed_code" in data
    assert "explanation" in data
    assert "changes_made" in data


def test_fix_suggestions():
    """
    Testa o endpoint de sugestões de correção.
    """
    response = client.get("/api/v1/fix/suggestions")
    assert response.status_code == 200
    
    data = response.json()
    assert "common_fixes" in data
    assert "best_practices" in data
    assert "performance_tips" in data


def test_invalid_story_request():
    """
    Testa requisição inválida para geração de histórias.
    """
    invalid_request = {
        "context": "abc",  # Contexto muito curto
        "story_type": "invalid_type"
    }
    
    response = client.post("/api/v1/stories/generate", json=invalid_request)
    assert response.status_code == 422  # Validation error


def test_invalid_test_request():
    """
    Testa requisição inválida para geração de testes.
    """
    invalid_request = {
        "input_type": "direct",
        # Falta code_content
        "language": "python"
    }
    
    response = client.post("/api/v1/code/tests/generate", json=invalid_request)
    assert response.status_code == 422  # Validation error
