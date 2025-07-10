## 🧠 Code Guardian - Seu assistente para criação de testes unitários com IA Generativa

### 📌 Visão Geral

Esta aplicação corporativa tem como objetivo **auxiliar desenvolvedores na criação automatizada de testes unitários** com o uso de IA generativa. A ferramenta foi idealizada para apoiar a evolução da cultura de qualidade de software na organização, onde ainda não há um padrão consolidado para testes unitários.

A aplicação, que será acessada em ambiente autenticado via Active Directory (AD) da Azure, permitirá que os desenvolvedores submetam trechos de código-fonte por três diferentes métodos e, a partir disso, um agente baseado em LLM (hospedado na Azure) irá gerar o código de testes unitários correspondente.

---

## 🧩 Tecnologias Utilizadas

| Camada       | Tecnologia                        |
| ------------ | --------------------------------- |
| Autenticação | Azure Active Directory (AD)       |
| Front-end    | React + TailwindCSS               |
| Back-end     | FastAPI                           |
| Orquestração | LangChain + LangGraph (Python)    |
| LLM          | Azure OpenAI                      |
| CI/CD        | GitLab                            |
| Hosting/API  | Interno (infraestrutura do banco) |

---

## ⚙️ Componentes Principais

### 1. **Autenticação: login corporativo via Azure AD**

### 2. **Interface do Usuário (React + Tailwind)**

* Caixa de texto para input manual de código
* Upload de arquivos
* Campo para inserção da URL do repositório GitLab
* Área de exibição do código gerado
* Botão para exportação do código de teste

### 3. **Back-end (FastAPI)**

* Recebe requisições do front-end
* Normaliza os inputs (texto, arquivo, URL)
* Aciona o pipeline de orquestração do agente

### 4. **Agente Orquestrador (LangChain + LangGraph)**

* Valida linguagem do código
* Acessa e interpreta o repositório (via GitLab API)
* Envia contexto para o LLM
* Recebe e trata a resposta com o teste gerado

### 5. **LLM da Azure**

* Gera os testes unitários com base no código fornecido
* Responde de forma estruturada e pronta para ser executada ou adaptada

---

## 🔁 Fluxo de Dados

1. Autenticação via Azure Active Directory
2. **Input** do código (texto, arquivo ou URL do GitLab)
3. Envio ao **Back-end (FastAPI)**
4. Encaminhamento para **LangGraph/LangChain**
5. Preparação do contexto e consulta ao **LLM da Azure**
6. Retorno com os testes unitários gerados
7. Renderização da resposta no **front-end**
8. **Exportação opcional** como arquivo para uso local ou versionamento

---

## 🧭 Diagrama de Arquitetura

```mermaid
graph TD
    Z[Azure AD\n(Autenticação Corporativa)] --> A[Frontend (React + Tailwind)]
    A -->|Input (código / arquivo / URL)| B[FastAPI Backend]
    B --> C[LangGraph + LangChain]
    C --> D[LLM Azure OpenAI]
    D --> C
    C --> E[Resposta formatada\n(Testes Unitários)]
    E --> B
    B --> A
    B -->|Exportação| F[Arquivo de Teste\n(.py / .js / .java)]
    C -->|Se URL GitLab| G[API GitLab]
```

---

