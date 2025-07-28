"""
Demonstração das funcionalidades Code Tester e Code Fixer com dados mockados.

Este script permite fazer uma demonstração completa das funcionalidades
sem depender da API backend estar rodando.
"""

import sys
from pathlib import Path
import streamlit as st

# Adicionar diretório raiz ao path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from app.utils.session_state import set_session_value


class MockDemo:
    """Classe para demonstração com dados mockados."""
    
    def __init__(self):
        self.code_samples = self._get_code_samples()
        self.mock_tests = self._get_mock_tests()
        self.mock_fixes = self._get_mock_fixes()
    
    def _get_code_samples(self):
        """Retorna amostras de código para demonstração."""
        return {
            "calculator": {
                "description": "Calculadora simples com operações básicas",
                "code": '''def calculadora(operacao, num1, num2):
    if operacao == "soma":
        return num1 + num2
    elif operacao == "subtracao":
        return num1 - num2
    elif operacao == "multiplicacao":
        return num1 * num2
    elif operacao == "divisao":
        if num2 == 0:
            raise ValueError("Divisão por zero não permitida")
        return num1 / num2
    else:
        raise ValueError("Operação não suportada")

def validar_entrada(numero):
    if not isinstance(numero, (int, float)):
        raise TypeError("Entrada deve ser um número")
    return True''',
                "language": "python"
            },
            "user_manager": {
                "description": "Gerenciador de usuários com validações",
                "code": '''class UserManager:
    def __init__(self):
        self.users = {}
    
    def create_user(self, username, email):
        if not username or not email:
            raise ValueError("Username e email são obrigatórios")
        
        if "@" not in email:
            raise ValueError("Email inválido")
        
        if username in self.users:
            raise ValueError("Usuário já existe")
        
        self.users[username] = {
            "email": email,
            "active": True,
            "created_at": datetime.now()
        }
        return self.users[username]
    
    def get_user(self, username):
        return self.users.get(username)
    
    def delete_user(self, username):
        if username not in self.users:
            raise ValueError("Usuário não encontrado")
        del self.users[username]''',
                "language": "python"
            },
            "api_client": {
                "description": "Cliente de API com tratamento de erros",
                "code": '''import requests
import json

class APIClient:
    def __init__(self, base_url, timeout=30):
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
    
    def get(self, endpoint, params=None):
        url = f"{self.base_url}/{endpoint}"
        response = self.session.get(url, params=params, timeout=self.timeout)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return None
        else:
            raise Exception(f"API Error: {response.status_code}")
    
    def post(self, endpoint, data):
        url = f"{self.base_url}/{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        response = self.session.post(
            url, 
            data=json.dumps(data), 
            headers=headers,
            timeout=self.timeout
        )
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            raise Exception(f"API Error: {response.status_code}")''',
                "language": "python"
            }
        }
    
    def _get_mock_tests(self):
        """Retorna testes unitários mockados para cada amostra de código."""
        return {
            "calculator": {
                "unittest": '''import unittest
from unittest.mock import patch
from calculator import calculadora, validar_entrada

class TestCalculadora(unittest.TestCase):
    
    def test_soma(self):
        """Testa operação de soma."""
        resultado = calculadora("soma", 5, 3)
        self.assertEqual(resultado, 8)
    
    def test_subtracao(self):
        """Testa operação de subtração."""
        resultado = calculadora("subtracao", 10, 4)
        self.assertEqual(resultado, 6)
    
    def test_multiplicacao(self):
        """Testa operação de multiplicação."""
        resultado = calculadora("multiplicacao", 3, 7)
        self.assertEqual(resultado, 21)
    
    def test_divisao(self):
        """Testa operação de divisão."""
        resultado = calculadora("divisao", 15, 3)
        self.assertEqual(resultado, 5.0)
    
    def test_divisao_por_zero(self):
        """Testa divisão por zero."""
        with self.assertRaises(ValueError) as context:
            calculadora("divisao", 10, 0)
        self.assertEqual(str(context.exception), "Divisão por zero não permitida")
    
    def test_operacao_invalida(self):
        """Testa operação não suportada."""
        with self.assertRaises(ValueError) as context:
            calculadora("potencia", 2, 3)
        self.assertEqual(str(context.exception), "Operação não suportada")

class TestValidarEntrada(unittest.TestCase):
    
    def test_validar_entrada_numero_inteiro(self):
        """Testa validação com número inteiro."""
        self.assertTrue(validar_entrada(10))
    
    def test_validar_entrada_numero_float(self):
        """Testa validação com número float."""
        self.assertTrue(validar_entrada(10.5))
    
    def test_validar_entrada_string(self):
        """Testa validação com string."""
        with self.assertRaises(TypeError) as context:
            validar_entrada("10")
        self.assertEqual(str(context.exception), "Entrada deve ser um número")
    
    def test_validar_entrada_none(self):
        """Testa validação com None."""
        with self.assertRaises(TypeError):
            validar_entrada(None)

if __name__ == '__main__':
    unittest.main()''',
                
                "pytest": '''import pytest
from calculator import calculadora, validar_entrada

class TestCalculadora:
    
    @pytest.mark.parametrize("operacao,num1,num2,esperado", [
        ("soma", 5, 3, 8),
        ("subtracao", 10, 4, 6),
        ("multiplicacao", 3, 7, 21),
        ("divisao", 15, 3, 5.0),
    ])
    def test_operacoes_basicas(self, operacao, num1, num2, esperado):
        """Testa operações básicas da calculadora."""
        resultado = calculadora(operacao, num1, num2)
        assert resultado == esperado
    
    def test_divisao_por_zero(self):
        """Testa divisão por zero."""
        with pytest.raises(ValueError, match="Divisão por zero não permitida"):
            calculadora("divisao", 10, 0)
    
    def test_operacao_invalida(self):
        """Testa operação não suportada."""
        with pytest.raises(ValueError, match="Operação não suportada"):
            calculadora("potencia", 2, 3)

class TestValidarEntrada:
    
    @pytest.mark.parametrize("entrada", [10, 10.5, -5, 0, 3.14159])
    def test_validar_entrada_numeros_validos(self, entrada):
        """Testa validação com diferentes tipos de números válidos."""
        assert validar_entrada(entrada) is True
    
    @pytest.mark.parametrize("entrada", ["10", None, [], {}, True])
    def test_validar_entrada_tipos_invalidos(self, entrada):
        """Testa validação com tipos inválidos."""
        with pytest.raises(TypeError, match="Entrada deve ser um número"):
            validar_entrada(entrada)'''
            },
            
            "user_manager": {
                "unittest": '''import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from user_manager import UserManager

class TestUserManager(unittest.TestCase):
    
    def setUp(self):
        """Configura o ambiente de teste."""
        self.user_manager = UserManager()
    
    def test_create_user_sucesso(self):
        """Testa criação de usuário com sucesso."""
        with patch('user_manager.datetime') as mock_datetime:
            mock_now = datetime(2023, 1, 1, 12, 0, 0)
            mock_datetime.now.return_value = mock_now
            
            result = self.user_manager.create_user("joao", "joao@email.com")
            
            expected = {
                "email": "joao@email.com",
                "active": True,
                "created_at": mock_now
            }
            self.assertEqual(result, expected)
            self.assertIn("joao", self.user_manager.users)
    
    def test_create_user_username_vazio(self):
        """Testa criação de usuário com username vazio."""
        with self.assertRaises(ValueError) as context:
            self.user_manager.create_user("", "test@email.com")
        self.assertEqual(str(context.exception), "Username e email são obrigatórios")
    
    def test_create_user_email_vazio(self):
        """Testa criação de usuário com email vazio."""
        with self.assertRaises(ValueError) as context:
            self.user_manager.create_user("joao", "")
        self.assertEqual(str(context.exception), "Username e email são obrigatórios")
    
    def test_create_user_email_invalido(self):
        """Testa criação de usuário com email inválido."""
        with self.assertRaises(ValueError) as context:
            self.user_manager.create_user("joao", "email_invalido")
        self.assertEqual(str(context.exception), "Email inválido")
    
    def test_create_user_duplicado(self):
        """Testa criação de usuário duplicado."""
        self.user_manager.create_user("joao", "joao@email.com")
        
        with self.assertRaises(ValueError) as context:
            self.user_manager.create_user("joao", "joao2@email.com")
        self.assertEqual(str(context.exception), "Usuário já existe")
    
    def test_get_user_existente(self):
        """Testa busca de usuário existente."""
        created_user = self.user_manager.create_user("maria", "maria@email.com")
        found_user = self.user_manager.get_user("maria")
        self.assertEqual(found_user, created_user)
    
    def test_get_user_inexistente(self):
        """Testa busca de usuário inexistente."""
        result = self.user_manager.get_user("inexistente")
        self.assertIsNone(result)
    
    def test_delete_user_existente(self):
        """Testa exclusão de usuário existente."""
        self.user_manager.create_user("carlos", "carlos@email.com")
        self.user_manager.delete_user("carlos")
        self.assertNotIn("carlos", self.user_manager.users)
    
    def test_delete_user_inexistente(self):
        """Testa exclusão de usuário inexistente."""
        with self.assertRaises(ValueError) as context:
            self.user_manager.delete_user("inexistente")
        self.assertEqual(str(context.exception), "Usuário não encontrado")

if __name__ == '__main__':
    unittest.main()''',
                
                "pytest": '''import pytest
from unittest.mock import patch
from datetime import datetime
from user_manager import UserManager

@pytest.fixture
def user_manager():
    """Fixture que fornece uma instância limpa do UserManager."""
    return UserManager()

@pytest.fixture
def sample_user_data():
    """Fixture com dados de usuário de exemplo."""
    return {
        "username": "testuser",
        "email": "test@example.com"
    }

class TestUserManager:
    
    def test_create_user_success(self, user_manager, sample_user_data):
        """Testa criação de usuário com sucesso."""
        with patch('user_manager.datetime') as mock_datetime:
            mock_now = datetime(2023, 1, 1, 12, 0, 0)
            mock_datetime.now.return_value = mock_now
            
            result = user_manager.create_user(
                sample_user_data["username"], 
                sample_user_data["email"]
            )
            
            assert result["email"] == sample_user_data["email"]
            assert result["active"] is True
            assert result["created_at"] == mock_now
            assert sample_user_data["username"] in user_manager.users
    
    @pytest.mark.parametrize("username,email,expected_error", [
        ("", "test@email.com", "Username e email são obrigatórios"),
        ("user", "", "Username e email são obrigatórios"),
        ("user", "email_sem_arroba", "Email inválido"),
    ])
    def test_create_user_validation_errors(self, user_manager, username, email, expected_error):
        """Testa erros de validação na criação de usuário."""
        with pytest.raises(ValueError, match=expected_error):
            user_manager.create_user(username, email)
    
    def test_create_duplicate_user(self, user_manager):
        """Testa criação de usuário duplicado."""
        user_manager.create_user("duplicate", "duplicate@email.com")
        
        with pytest.raises(ValueError, match="Usuário já existe"):
            user_manager.create_user("duplicate", "another@email.com")
    
    def test_get_existing_user(self, user_manager):
        """Testa busca de usuário existente."""
        created_user = user_manager.create_user("found", "found@email.com")
        found_user = user_manager.get_user("found")
        assert found_user == created_user
    
    def test_get_nonexistent_user(self, user_manager):
        """Testa busca de usuário inexistente."""
        result = user_manager.get_user("nonexistent")
        assert result is None
        
    def test_delete_existing_user(self, user_manager):
        """Testa exclusão de usuário existente."""
        user_manager.create_user("todelete", "delete@email.com")
        user_manager.delete_user("todelete")
        assert "todelete" not in user_manager.users
    
    def test_delete_nonexistent_user(self, user_manager):
        """Testa exclusão de usuário inexistente."""
        with pytest.raises(ValueError, match="Usuário não encontrado"):
            user_manager.delete_user("nonexistent")'''
            },
            
            "api_client": {
                "unittest": '''import unittest
from unittest.mock import Mock, patch, MagicMock
import json
from api_client import APIClient

class TestAPIClient(unittest.TestCase):
    
    def setUp(self):
        """Configura o ambiente de teste."""
        self.base_url = "https://api.example.com"
        self.client = APIClient(self.base_url)
    
    @patch('api_client.requests.Session')
    def test_get_success(self, mock_session_class):
        """Testa GET request com sucesso."""
        # Arrange
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "success"}
        mock_session.get.return_value = mock_response
        
        client = APIClient(self.base_url)
        
        # Act
        result = client.get("users", {"page": 1})
        
        # Assert
        self.assertEqual(result, {"data": "success"})
        mock_session.get.assert_called_once_with(
            f"{self.base_url}/users",
            params={"page": 1},
            timeout=30
        )
    
    @patch('api_client.requests.Session')
    def test_get_not_found(self, mock_session_class):
        """Testa GET request com 404."""
        # Arrange
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        mock_response = Mock()
        mock_response.status_code = 404
        mock_session.get.return_value = mock_response
        
        client = APIClient(self.base_url)
        
        # Act
        result = client.get("users/999")
        
        # Assert
        self.assertIsNone(result)
    
    @patch('api_client.requests.Session')
    def test_get_server_error(self, mock_session_class):
        """Testa GET request com erro de servidor."""
        # Arrange
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        mock_response = Mock()
        mock_response.status_code = 500
        mock_session.get.return_value = mock_response
        
        client = APIClient(self.base_url)
        
        # Act & Assert
        with self.assertRaises(Exception) as context:
            client.get("users")
        self.assertEqual(str(context.exception), "API Error: 500")
    
    @patch('api_client.requests.Session')
    def test_post_success(self, mock_session_class):
        """Testa POST request com sucesso."""
        # Arrange
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": 1, "created": True}
        mock_session.post.return_value = mock_response
        
        client = APIClient(self.base_url)
        data = {"name": "Test User", "email": "test@example.com"}
        
        # Act
        result = client.post("users", data)
        
        # Assert
        self.assertEqual(result, {"id": 1, "created": True})
        mock_session.post.assert_called_once_with(
            f"{self.base_url}/users",
            data=json.dumps(data),
            headers={"Content-Type": "application/json"},
            timeout=30
        )
    
    @patch('api_client.requests.Session')
    def test_post_error(self, mock_session_class):
        """Testa POST request com erro."""
        # Arrange
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        mock_response = Mock()
        mock_response.status_code = 400
        mock_session.post.return_value = mock_response
        
        client = APIClient(self.base_url)
        
        # Act & Assert
        with self.assertRaises(Exception) as context:
            client.post("users", {"invalid": "data"})
        self.assertEqual(str(context.exception), "API Error: 400")

if __name__ == '__main__':
    unittest.main()''',
                
                "pytest": '''import pytest
from unittest.mock import Mock, patch
import json
from api_client import APIClient

@pytest.fixture
def api_client():
    """Fixture que fornece uma instância do APIClient."""
    return APIClient("https://api.example.com")

@pytest.fixture
def mock_session():
    """Fixture que fornece uma sessão mockada."""
    with patch('api_client.requests.Session') as mock_session_class:
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        yield mock_session

class TestAPIClient:
    
    def test_get_success(self, api_client, mock_session):
        """Testa GET request com sucesso."""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"users": [{"id": 1, "name": "Test"}]}
        mock_session.get.return_value = mock_response
        
        # Act
        result = api_client.get("users", {"active": True})
        
        # Assert
        assert result == {"users": [{"id": 1, "name": "Test"}]}
        mock_session.get.assert_called_once_with(
            "https://api.example.com/users",
            params={"active": True},
            timeout=30
        )
    
    @pytest.mark.parametrize("status_code,expected_result", [
        (404, None),
        (500, "exception"),
        (403, "exception"),
    ])
    def test_get_error_cases(self, api_client, mock_session, status_code, expected_result):
        """Testa diferentes casos de erro no GET."""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = status_code
        mock_session.get.return_value = mock_response
        
        # Act & Assert
        if expected_result == "exception":
            with pytest.raises(Exception, match=f"API Error: {status_code}"):
                api_client.get("users")
        else:
            result = api_client.get("users")
            assert result == expected_result
    
    @pytest.mark.parametrize("status_code", [200, 201])
    def test_post_success_cases(self, api_client, mock_session, status_code):
        """Testa POST com diferentes códigos de sucesso."""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = status_code
        mock_response.json.return_value = {"success": True, "id": 123}
        mock_session.post.return_value = mock_response
        
        data = {"name": "New User", "email": "new@example.com"}
        
        # Act
        result = api_client.post("users", data)
        
        # Assert
        assert result == {"success": True, "id": 123}
        mock_session.post.assert_called_once_with(
            "https://api.example.com/users",
            data=json.dumps(data),
            headers={"Content-Type": "application/json"},
            timeout=30
        )
    
    def test_post_error(self, api_client, mock_session):
        """Testa POST com erro."""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 422
        mock_session.post.return_value = mock_response
        
        # Act & Assert
        with pytest.raises(Exception, match="API Error: 422"):
            api_client.post("users", {"invalid": "data"})
    
    def test_custom_timeout(self):
        """Testa criação do cliente com timeout customizado."""
        client = APIClient("https://api.example.com", timeout=60)
        assert client.timeout == 60'''
            }
        }
    
    def _get_mock_fixes(self):
        """Retorna correções de código mockadas."""
        return {
            "name_error": {
                "error": "NameError: name 'variavel' is not defined",
                "buggy_code": '''def processar_dados():
    dados = [1, 2, 3, 4, 5]
    for item in dados:
        print(item)
    return variavel  # Erro: variável não definida''',
                "fixed_code": '''def processar_dados():
    dados = [1, 2, 3, 4, 5]
    resultado = []  # Definindo a variável
    for item in dados:
        print(item)
        resultado.append(item * 2)  # Exemplo de processamento
    return resultado  # Retornando a variável definida''',
                "explanation": '''**Problema identificado:**
O erro `NameError` indica que a variável `variavel` não foi definida no escopo da função.

**Correção aplicada:**
1. **Definição da variável**: Criada a variável `resultado` como uma lista vazia
2. **Processamento dos dados**: Adicionado exemplo de processamento (multiplicação por 2)
3. **Retorno correto**: A função agora retorna a variável definida

**Boas práticas implementadas:**
- Inicialização de variáveis antes do uso
- Nomenclatura descritiva para variáveis
- Processamento lógico dos dados''',
                "changes": [
                    "Criada variável 'resultado' inicializada como lista vazia",
                    "Adicionado processamento dos itens dentro do loop",
                    "Alterado retorno para usar a variável definida",
                    "Melhorada a legibilidade do código"
                ],
                "prevention_tips": [
                    "Sempre declare variáveis antes de usá-las",
                    "Use nomes descritivos para variáveis",
                    "Inicialize variáveis com valores apropriados",
                    "Teste o código com dados de exemplo"
                ]
            },
            
            "index_error": {
                "error": "IndexError: list index out of range",
                "buggy_code": '''def obter_elemento(lista, indice):
    return lista[indice]

# Uso problemático
numeros = [1, 2, 3]
resultado = obter_elemento(numeros, 5)  # Índice fora do range''',
                "fixed_code": '''def obter_elemento(lista, indice):
    """
    Obtém elemento da lista no índice especificado com validação.
    
    Args:
        lista: Lista de elementos
        indice: Índice do elemento desejado
        
    Returns:
        Elemento no índice ou None se inválido
        
    Raises:
        TypeError: Se lista não for uma lista
        ValueError: Se índice for negativo
    """
    if not isinstance(lista, list):
        raise TypeError("Primeiro parâmetro deve ser uma lista")
    
    if indice < 0:
        raise ValueError("Índice deve ser um número positivo")
    
    if indice >= len(lista):
        return None  # Ou raise IndexError com mensagem personalizada
    
    return lista[indice]

# Uso correto com validação
numeros = [1, 2, 3]
resultado = obter_elemento(numeros, 5)  # Retorna None ao invés de erro
if resultado is not None:
    print(f"Elemento encontrado: {resultado}")
else:
    print("Índice fora do range da lista")''',
                "explanation": '''**Problema identificado:**
O erro `IndexError` ocorre quando tentamos acessar um índice que não existe na lista.

**Correção aplicada:**
1. **Validação de tipo**: Verifica se o primeiro parâmetro é uma lista
2. **Validação de índice**: Verifica se o índice é positivo
3. **Verificação de bounds**: Verifica se o índice está dentro do tamanho da lista
4. **Tratamento gracioso**: Retorna None ao invés de gerar erro
5. **Documentação**: Adicionada docstring completa

**Alternativas de implementação:**
- Retornar None (implementado)
- Lançar IndexError com mensagem customizada
- Retornar valor padrão configurável''',
                "changes": [
                    "Adicionada validação de tipo para o parâmetro lista",
                    "Implementada verificação de índice negativo",
                    "Adicionada verificação de bounds da lista",
                    "Criado tratamento gracioso retornando None",
                    "Incluída documentação completa da função",
                    "Melhorado exemplo de uso com verificação do resultado"
                ],
                "prevention_tips": [
                    "Sempre validar índices antes de acessar elementos",
                    "Usar len() para verificar o tamanho da lista",
                    "Implementar tratamento de erros apropriado",
                    "Considerar usar métodos seguros como .get() para dicionários",
                    "Testar com casos extremos (listas vazias, índices grandes)"
                ]
            },
            
            "type_error": {
                "error": "TypeError: unsupported operand type(s) for +: 'int' and 'str'",
                "buggy_code": '''def somar_valores(a, b):
    return a + b

# Uso problemático
resultado = somar_valores(10, "20")  # Tentando somar int com str''',
                "fixed_code": '''def somar_valores(a, b):
    """
    Soma dois valores com conversão automática de tipos.
    
    Args:
        a: Primeiro valor (int, float ou str numérica)
        b: Segundo valor (int, float ou str numérica)
        
    Returns:
        float: Soma dos valores convertidos
        
    Raises:
        ValueError: Se algum valor não puder ser convertido para número
        TypeError: Se algum valor for None
    """
    if a is None or b is None:
        raise TypeError("Valores não podem ser None")
    
    try:
        # Converte para float para suportar números decimais
        num_a = float(a)
        num_b = float(b)
        return num_a + num_b
    except (ValueError, TypeError) as e:
        raise ValueError(f"Não foi possível converter os valores para números: {e}")

# Versão alternativa com type hints
from typing import Union

def somar_valores_tipada(a: Union[int, float, str], b: Union[int, float, str]) -> float:
    """Versão com type hints para melhor documentação."""
    return somar_valores(a, b)

# Uso correto
try:
    resultado1 = somar_valores(10, "20")    # Funciona: 30.0
    resultado2 = somar_valores(5.5, 2.3)   # Funciona: 7.8
    resultado3 = somar_valores("15", "25") # Funciona: 40.0
    print(f"Resultados: {resultado1}, {resultado2}, {resultado3}")
except ValueError as e:
    print(f"Erro de conversão: {e}")
except TypeError as e:
    print(f"Erro de tipo: {e}")''',
                "explanation": '''**Problema identificado:**
O erro `TypeError` ocorre porque Python não pode somar diretamente um inteiro com uma string.

**Correção aplicada:**
1. **Conversão de tipos**: Converte ambos os valores para float
2. **Tratamento de erros**: Captura erros de conversão
3. **Validação de None**: Verifica valores nulos
4. **Type hints**: Versão alternativa com anotações de tipo
5. **Documentação**: Docstring completa com exemplos

**Estratégias de conversão:**
- `float()`: Suporta inteiros, floats e strings numéricas
- Tratamento de exceções para valores inválidos
- Mensagens de erro descritivas''',
                "changes": [
                    "Implementada conversão automática para float",
                    "Adicionada validação para valores None",
                    "Criado tratamento de exceções específicas",
                    "Incluída versão com type hints",
                    "Melhorada documentação da função",
                    "Adicionados exemplos de uso com diferentes tipos",
                    "Implementado tratamento de erros no código de uso"
                ],
                "prevention_tips": [
                    "Usar type hints para documentar tipos esperados",
                    "Implementar conversão de tipos quando necessário",
                    "Validar entradas da função",
                    "Usar isinstance() para verificar tipos",
                    "Tratar exceções de conversão adequadamente",
                    "Testar com diferentes tipos de dados"
                ]
            }
        }
    
    def run_code_tester_demo(self, sample_key="calculator"):
        """
        Executa demonstração do Code Tester.
        
        Args:
            sample_key: Chave da amostra de código a ser usada
        """
        print("🧪 === DEMONSTRAÇÃO CODE TESTER ===\n")
        
        if sample_key not in self.code_samples:
            print(f"❌ Amostra '{sample_key}' não encontrada!")
            return
        
        sample = self.code_samples[sample_key]
        tests = self.mock_tests.get(sample_key, {})
        
        print(f"📝 **Código de Exemplo: {sample['description']}**")
        print("\n```python")
        print(sample['code'])
        print("```\n")
        
        print("🔄 Processando geração de testes...")
        print("⚙️ Analisando código...")
        print("🤖 Gerando testes com IA...")
        print("✅ Testes gerados com sucesso!\n")
        
        print("📊 **Resultados:**")
        print(f"- Total de testes: {len(tests)}")
        print(f"- Frameworks: unittest, pytest")
        print(f"- Método usado: Entrada Manual\n")
        
        for framework, test_code in tests.items():
            print(f"🧪 **Teste {framework.upper()}:**")
            print("```python")
            print(test_code)
            print("```\n")
        
        print("💡 **Próximos passos:**")
        print("1. Revisar os testes gerados")
        print("2. Adaptar aos padrões do projeto")
        print("3. Executar os testes no ambiente de desenvolvimento")
        print("4. Ajustar cobertura conforme necessário\n")
    
    def run_code_fixer_demo(self, error_key="name_error"):
        """
        Executa demonstração do Code Fixer.
        
        Args:
            error_key: Chave do erro a ser usado na demonstração
        """
        print("🛠️ === DEMONSTRAÇÃO CODE FIXER ===\n")
        
        if error_key not in self.mock_fixes:
            print(f"❌ Erro '{error_key}' não encontrado!")
            return
        
        fix_data = self.mock_fixes[error_key]
        
        print(f"🚨 **Erro Reportado:**")
        print(f"`{fix_data['error']}`\n")
        
        print("📝 **Código Problemático:**")
        print("```python")
        print(fix_data['buggy_code'])
        print("```\n")
        
        print("🔄 Processando correção...")
        print("🤖 Analisando erro...")
        print("🔍 Identificando causa raiz...")
        print("⚡ Gerando correção...")
        print("✅ Código corrigido com sucesso!\n")
        
        print("🔧 **Código Corrigido:**")
        print("```python")
        print(fix_data['fixed_code'])
        print("```\n")
        
        print("📖 **Explicação da Correção:**")
        print(fix_data['explanation'])
        print()
        
        print("📋 **Mudanças Aplicadas:**")
        for i, change in enumerate(fix_data['changes'], 1):
            print(f"{i}. {change}")
        print()
        
        print("💡 **Dicas de Prevenção:**")
        for i, tip in enumerate(fix_data['prevention_tips'], 1):
            print(f"{i}. {tip}")
        print()
        
        print("🎯 **Próximos passos:**")
        print("1. Revisar a correção sugerida")
        print("2. Testar o código corrigido")
        print("3. Aplicar as dicas de prevenção")
        print("4. Atualizar testes unitários se necessário\n")
    
    def run_full_demo(self):
        """Executa demonstração completa de ambas as funcionalidades."""
        print("🛡️ === DEMONSTRAÇÃO COMPLETA CODEGUARDIAN ===\n")
        
        # Demo Code Tester
        self.run_code_tester_demo("calculator")
        print("="*60 + "\n")
        
        # Demo Code Fixer  
        self.run_code_fixer_demo("name_error")
        print("="*60 + "\n")
        
        print("🎉 **Demonstração Concluída!**")
        print("\n🚀 **CodeGuardian - Recursos Demonstrados:**")
        print("✅ Code Tester: Geração automática de testes unitários")
        print("✅ Code Fixer: Identificação e correção de bugs")
        print("\n💼 **Desenvolvido pela Governança de Tecnologia**")
        print("👥 **Time de Qualidade de Software**")
    
    def get_available_samples(self):
        """Retorna lista de amostras disponíveis."""
        return list(self.code_samples.keys())
    
    def get_available_errors(self):
        """Retorna lista de erros disponíveis."""
        return list(self.mock_fixes.keys())


def main():
    """Função principal para executar a demonstração."""
    demo = MockDemo()
    
    print("Escolha o tipo de demonstração:")
    print("1. Code Tester")
    print("2. Code Fixer") 
    print("3. Demonstração Completa")
    
    choice = input("\nEscolha (1-3): ").strip()
    
    if choice == "1":
        print("\nAmostras disponíveis:")
        samples = demo.get_available_samples()
        for i, sample in enumerate(samples, 1):
            print(f"{i}. {sample}")
        
        sample_choice = input(f"\nEscolha a amostra (1-{len(samples)}): ").strip()
        try:
            sample_idx = int(sample_choice) - 1
            sample_key = samples[sample_idx]
            demo.run_code_tester_demo(sample_key)
        except (ValueError, IndexError):
            print("Escolha inválida, usando amostra padrão...")
            demo.run_code_tester_demo()
    
    elif choice == "2":
        print("\nTipos de erro disponíveis:")
        errors = demo.get_available_errors()
        for i, error in enumerate(errors, 1):
            print(f"{i}. {error}")
        
        error_choice = input(f"\nEscolha o tipo de erro (1-{len(errors)}): ").strip()
        try:
            error_idx = int(error_choice) - 1
            error_key = errors[error_idx]
            demo.run_code_fixer_demo(error_key)
        except (ValueError, IndexError):
            print("Escolha inválida, usando erro padrão...")
            demo.run_code_fixer_demo()
    
    elif choice == "3":
        demo.run_full_demo()
    
    else:
        print("Escolha inválida, executando demonstração completa...")
        demo.run_full_demo()


if __name__ == "__main__":
    main()
