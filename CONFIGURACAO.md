# Configuração do Ambiente - Code Guardian

## 📋 Pré-requisitos

- Python 3.13+
- Acesso ao Azure OpenAI
- Acesso ao GitLab (opcional)

## 🔧 Configuração Inicial

### 1. Configurar Variáveis de Ambiente

O projeto usa um arquivo `.env` para configurações sensíveis. Siga estes passos:

1. **Copie o arquivo de exemplo**:
   ```bash
   cp .env.example .env
   ```

2. **Edite o arquivo `.env`** com seus dados reais:

#### Configurações Obrigatórias do Azure OpenAI:
```env
AZURE_OPENAI_ENDPOINT=https://seu-recurso.openai.azure.com/
AZURE_OPENAI_API_KEY=sua-chave-api-aqui
AZURE_OPENAI_DEPLOYMENT_NAME=nome-do-seu-deployment
```

#### Configurações Opcionais:
```env
AZURE_OPENAI_API_VERSION=2023-12-01-preview
AZURE_OPENAI_MODEL_NAME=gpt-4
```

### 2. Configurações do GitLab (Opcional)

Se você planeja usar a integração com GitLab:

```env
GITLAB_API_URL=https://gitlab.sua-empresa.com/api/v4
GITLAB_ACCESS_TOKEN=seu-token-gitlab
GITLAB_PROJECT_ID=id-do-projeto
```

### 3. Outras Configurações

```env
# Ambiente de execução
APP_ENVIRONMENT=development  # ou production
APP_DEBUG=true              # ou false para produção

# Configurações do servidor
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
SERVER_RELOAD=true          # apenas para desenvolvimento

# Configurações de segurança
SECRET_KEY=sua-chave-secreta-aqui
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8501
```

## 🚀 Inicialização

### 1. Instalar Dependências
```bash
# Usando uv (recomendado)
uv install

# Ou usando pip
pip install -r requirements.txt
```

### 2. Verificar Configuração
```bash
python main.py info
```

### 3. Iniciar a API
```bash
python main.py api
```

A API estará disponível em: http://localhost:8000

### 4. Documentação da API
Acesse: http://localhost:8000/docs

## 🔍 Validação da Configuração

### Verificar Health Check
```bash
curl http://localhost:8000/api/v1/health
```

### Verificar Health Check Detalhado
```bash
curl http://localhost:8000/api/v1/health/detailed
```

## 🧪 Executar Testes

```bash
python main.py test
```

## ⚠️ Importante

- **NUNCA** commite o arquivo `.env` no repositório
- O arquivo `.env.example` serve como template
- Use valores diferentes para desenvolvimento e produção
- Mantenha suas chaves de API seguras

## 🔐 Segurança

1. **Desenvolvimento**: Use dados mock no `.env`
2. **Produção**: Use variáveis de ambiente do sistema ou serviço de secrets
3. **Testes**: Use o arquivo `.env.test` ou variáveis específicas

## 📖 Estrutura do Projeto

```
code-guardian/
├── .env.example          # Template de configuração
├── .env                  # Configurações locais (não versionado)
├── .gitignore           # Arquivos ignorados pelo Git
├── config/
│   ├── __init__.py
│   └── settings.py      # Configurações centralizadas
├── main.py              # Script principal
└── ...
```

## 🆘 Solução de Problemas

### Erro: "Configurações obrigatórias do Azure OpenAI ausentes"

1. Verifique se o arquivo `.env` existe
2. Confirme se as variáveis obrigatórias estão definidas:
   - `AZURE_OPENAI_ENDPOINT`
   - `AZURE_OPENAI_API_KEY`
   - `AZURE_OPENAI_DEPLOYMENT_NAME`

### Erro: "Chave da API do Azure OpenAI não configurada"

1. Verifique se a variável `AZURE_OPENAI_API_KEY` está definida no `.env`
2. Confirme se o valor não está vazio

### Problemas de Conexão

1. Verifique se o endpoint está correto
2. Teste a conectividade com o Azure OpenAI
3. Confirme se a chave da API tem as permissões necessárias

## 📞 Suporte

Para problemas com configuração, verifique:
1. Os logs da aplicação em `logs/`
2. A documentação da API em `/docs`
3. Os testes automatizados
