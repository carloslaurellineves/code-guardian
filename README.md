# CodeGuardian

CodeGuardian é uma aplicação corporativa baseada em Inteligência Artificial Generativa desenvolvida para apoiar, padronizar e escalar práticas de **qualidade de software** no ciclo de desenvolvimento da nossa instituição.

## 🔍 Contexto e Motivação

O desenvolvimento de software dentro da instituição ainda carece de uma **cultura sólida de qualidade**. A área de Governança de Tecnologia, especificamente o time de Qualidade de Software, identificou a necessidade de prover **ferramentas práticas e acessíveis** para apoiar os desenvolvedores, Product Owners (POs) e demais stakeholders ao longo da esteira de CI/CD.

Para suprir essa demanda, surge o **CodeGuardian**, uma aplicação modular e escalável que utiliza **IA Generativa** para automatizar tarefas críticas que hoje são realizadas de forma pouco padronizada (ou mesmo inexistentes), como:

- Escrita de histórias e critérios de aceite;
- Geração de testes unitários;
- Identificação e correção de bugs de código.

---

## 🎯 Objetivos

- **Padronizar** a escrita de histórias de usuário com linguagem Gherkin;
- **Apoiar desenvolvedores** na geração de testes unitários a partir de diferentes entradas;
- **Reduzir retrabalho e acelerar o ciclo de entrega** por meio da identificação e correção automatizada de bugs;
- **Incentivar uma cultura de qualidade** com suporte acessível, integrado e escalável.

---

## 🧩 Estrutura da Aplicação

A aplicação está dividida em quatro páginas principais:

### 1. 🏠 Home
Página inicial com explicação geral sobre a aplicação, suas funcionalidades e como utilizar cada uma das ferramentas disponíveis.

---

### 2. 🧱 Story Creator
Ferramenta voltada à construção de **épicos, histórias e tarefas** com base em metodologias ágeis. Os artefatos gerados seguem padrão de escrita em **linguagem Gherkin**, conforme as diretrizes de qualidade esperadas pela instituição.

📌 Funcionalidades:
- Entrada textual para contexto do produto ou funcionalidade;
- Geração automática de histórias em formato padronizado;
- Sugestões de critérios de aceitação e desdobramento de tarefas.

---

### 3. 🧪 Code Tester
Subpágina dedicada à **geração automatizada de testes unitários**, visando incentivar e facilitar a adoção dessa prática essencial.

🛠️ Modos de uso:
- **Colar código manualmente** na interface;
- **Fazer upload de arquivo** com código-fonte (.py, .js, etc.);
- **Informar a URL de um repositório GitLab**, para leitura automática do código e geração dos testes.

📌 Saída:
- Testes unitários prontos para uso, alinhados às boas práticas da linguagem de origem do código.

---

### 4. 🛠️ Code Fixer
Ferramenta voltada à **identificação e correção de bugs** a partir da entrada do erro e do trecho de código relacionado.

📌 Funcionalidades:
- Diagnóstico de falhas com sugestão de correção;
- Explicação contextual da mudança sugerida;
- Geração do código corrigido com base em boas práticas.

---

## 🧱 Arquitetura da Solução

A aplicação será construída com **foco em modularidade, escalabilidade e integração com o ecossistema já validado pela instituição**.

### 🔗 Tecnologias e Componentes Principais

| Componente     | Tecnologia                             | Finalidade                                                                 |
|----------------|-----------------------------------------|---------------------------------------------------------------------------|
| Front-end      | [Streamlit](https://streamlit.io)       | Construção das interfaces e subpáginas interativas                       |
| Back-end       | [Python](https://www.python.org)        | Lógica de negócios, manipulação de inputs e integração com agentes       |
| Orquestração   | [LangChain](https://www.langchain.com) + [LangGraph](https://docs.langchain.com/langgraph) | Coordenação entre agentes, fluxo de prompts e controle de contexto |
| LLM            | Azure OpenAI (modelo homologado)        | Processamento de linguagem natural e geração de conteúdo técnico         |
| Repositório    | GitLab                                  | Fonte de código para geração de testes unitários                         |
| CI/CD          | Pipeline institucional                  | Futuramente, integração para automações dentro da esteira de deploy      |

---

## 🚀 Benefícios Esperados

- **Aumento da cobertura de testes unitários**;
- **Melhoria da rastreabilidade** entre requisito e implementação;
- **Redução de falhas em produção**;
- **Padronização de histórias e critérios de aceite**;
- **Agilidade no diagnóstico e correção de bugs**;
- **Apoio à transformação cultural na área de desenvolvimento**.

---

## 📁 Estrutura Inicial do Projeto

```plaintext
codeguardian/
├── README.md
├── app/
│   ├── main.py                 # App principal (Streamlit)
│   ├── pages/
│   │   ├── Home.py
│   │   ├── StoryCreator.py
│   │   ├── CodeTester.py
│   │   └── CodeFixer.py
│   ├── agents/
│   │   ├── story_agent.py
│   │   ├── test_generator_agent.py
│   │   └── bug_fixer_agent.py
│   └── utils/
│       └── gitlab_connector.py
└── requirements.txt
```

## 📲 Fluxograma da aplicação

```mermaid
flowchart TD
    A[Usuário acessa a Home] --> B{Escolhe subpágina}
    B --> C[Story Creator]
    B --> D[Code Tester]
    B --> E[Code Fixer]
    C --> C1[Input: contexto da funcionalidade]
    C1 --> C2[Orquestração LangChain/LangGraph]
    C2 --> C3[Agente de Escrita de Histórias]
    C3 --> C4[LLM Azure: Geração Gherkin]
    C4 --> C5[Output: Épico, Histórias, Tarefas]
    D --> D1{Escolhe forma de input}
    D1 --> D1a[Cola o código]
    D1 --> D1b[Faz upload de arquivo]
    D1 --> D1c[Informa URL do GitLab]
    D1a --> D2
    D1b --> D2
    D1c --> D2
    D2[Orquestração LangChain/LangGraph]
    D2 --> D3[Agente Gerador de Testes]
    D3 --> D4[LLM Azure: Criação de testes unitários]
    D4 --> D5[Output: Código de Teste]
    E --> E1[Input: código com bug + descrição do erro]
    E1 --> E2[Orquestração LangChain/LangGraph]
    E2 --> E3[Agente de Correção de Código]
    E3 --> E4[LLM Azure: Sugestão de correção]
    E4 --> E5[Output: Código corrigido + explicação]
    classDef agent fill:#e0f7fa,stroke:#00acc1,color:#006064;
    class C3,D3,E3 agent;
    classDef llm fill:#f3e5f5,stroke:#8e24aa,color:#4a148c;
    class C4,D4,E4 llm;

