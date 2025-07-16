"""
Página inicial do CodeGuardian usando Streamlit.

Esta página oferece uma visão geral das funcionalidades
e boas práticas do aplicativo.
"""

import streamlit as st
from pathlib import Path
import sys

# Adicionar diretório raiz ao path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

class HomePage:
    """
    Classe representando a página inicial da aplicação.
    """
    def render(self):
        """
        Renderiza a página inicial no Streamlit.
        """
        # Cabeçalho principal
        st.title("🛡️ Bem-vindo ao CodeGuardian")
        st.markdown("### *Qualidade de Software com Inteligência Artificial*")
        
        # Introdução contextualizada
        st.markdown("---")
        st.markdown("## 🎯 Sobre o CodeGuardian")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            O **CodeGuardian** é uma aplicação corporativa baseada em **Inteligência Artificial Generativa** 
            desenvolvida para apoiar, padronizar e escalar práticas de **qualidade de software** no ciclo de 
            desenvolvimento da nossa instituição.
            
            Esta ferramenta utiliza **agentes especializados** integrados ao **Azure OpenAI** para automatizar 
            tarefas críticas que hoje são realizadas de forma pouco padronizada, promovendo uma **cultura sólida 
            de qualidade** no desenvolvimento.
            """)
        
        with col2:
            st.info("""
            **🏢 Desenvolvido por:**
            
            **Governança de Tecnologia**
            
            *Time de Qualidade de Software*
            """)
        
        # Funcionalidades detalhadas
        st.markdown("---")
        st.markdown("## 🚀 Funcionalidades Principais")
        
        # Story Creator
        with st.expander("🧱 **Story Creator** - Geração de Histórias Ágeis", expanded=True):
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.markdown("""
                **📝 O que faz:**
                - Gera épicos, histórias e tarefas
                - Segue metodologias ágeis
                - Formato Gherkin (Given-When-Then)
                - Critérios de aceite automáticos
                """)
            
            with col2:
                st.markdown("""
                **🎯 Como usar:**
                1. Descreva o contexto do produto/funcionalidade
                2. Seja específico sobre objetivos e usuários
                3. Clique em "Gerar Histórias"
                4. Revise e ajuste as histórias geradas
                
                **💡 Dica:** Quanto mais contexto você fornecer, melhor será a qualidade das histórias!
                """)
        
        # Code Tester
        with st.expander("🧪 **Code Tester** - Geração de Testes Unitários"):
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.markdown("""
                **⚙️ O que faz:**
                - Gera testes unitários automaticamente
                - Suporta múltiplas linguagens
                - Três formas de entrada de código
                - Segue boas práticas de teste
                """)
            
            with col2:
                st.markdown("""
                **🔧 Formas de uso:**
                1. **Código manual**: Cole o código diretamente
                2. **Upload de arquivo**: Envie arquivos .py, .js, etc.
                3. **URL do GitLab**: Informe o link do repositório
                
                **✅ Saída:** Testes prontos para uso, alinhados às boas práticas
                """)
        
        # Code Fixer
        with st.expander("🛠️ **Code Fixer** - Correção de Bugs"):
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.markdown("""
                **🔧 O que faz:**
                - Identifica e corrige bugs
                - Analisa mensagens de erro
                - Sugere correções com explicações
                - Gera código corrigido
                """)
            
            with col2:
                st.markdown("""
                **🚨 Como usar:**
                1. Cole a mensagem de erro recebida
                2. Insira o código problemático
                3. Clique em "Corrigir Código"
                4. Analise a correção sugerida
                
                **🎯 Resultado:** Código corrigido com explicação contextual
                """)
        
        # Navegação e interação
        st.markdown("---")
        st.markdown("## 🧭 Como Navegar na Aplicação")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.success("""
            **📋 Navegação:**
            
            • Use o **menu lateral** para alternar entre páginas \n
            • Cada página tem instruções específicas \n
            • Resultados são mantidos durante a sessão \n
            • Histórico de operações disponível
            """)
        
        with col2:
            st.info("""
            **💡 Dicas de Interação:**
            
            • Forneça contexto detalhado para melhores resultados \n
            • Revise sempre as saídas geradas \n
            • Experimente diferentes inputs \n 
            • Use os botões de "Copiar" para facilitar o uso
            """)
        
        # Boas práticas
        st.markdown("---")
        st.markdown("## 📚 Boas Práticas de Uso")
        
        # Práticas em cards
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **🎯 Entrada de Dados**
            
            • Seja específico e detalhado \n
            • Use exemplos quando possível \n
            • Informe o contexto completo \n
            • Descreva o objetivo claramente \n
            """)
        
        with col2:
            st.markdown("""
            **🔍 Validação de Resultados**
            
            • Revise sempre as saídas geradas \n
            • Adapte aos padrões da instituição \n
            • Teste os códigos sugeridos \n
            • Valide a aderência aos requisitos \n
            """)
        
        with col3:
            st.markdown("""
            **📈 Otimização**
            
            • Experimente diferentes abordagens \n
            • Use o histórico para comparar resultados\n
            • Combine diferentes funcionalidades \n
            • Documente as melhores práticas \n
            """)
        
        # Benefícios esperados
        st.markdown("---")
        st.markdown("## 🎁 Benefícios Esperados")
        
        benefits_cols = st.columns(2)
        
        with benefits_cols[0]:
            st.markdown("""
            **📊 Melhorias Quantitativas:**
            - ⬆️ Aumento da cobertura de testes unitários
            - ⬇️ Redução de falhas em produção
            - ⏱️ Agilidade no diagnóstico de bugs
            - 📈 Padronização de histórias e critérios
            """)
        
        with benefits_cols[1]:
            st.markdown("""
            **🎯 Melhorias Qualitativas:**
            - 🔗 Melhoria da rastreabilidade
            - 🏗️ Apoio à transformação cultural
            - 🛡️ Fortalecimento da qualidade
            - 🚀 Escalabilidade das práticas
            """)
        
        # Stack tecnológica
        st.markdown("---")
        st.markdown("## 🔧 Tecnologias Utilizadas")
        
        with st.expander("🛠️ Stack Tecnológica Completa"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                **Frontend:**
                - 🎨 Streamlit (Interface interativa)
                - 🐍 Python (Lógica de apresentação)
                
                **Backend:**
                - ⚡ FastAPI (API REST)
                - 🔗 LangChain (Orquestração de agentes)
                - 📊 LangGraph (Fluxo de prompts)
                """)
            
            with col2:
                st.markdown("""
                **IA & Integração:**
                - 🧠 Azure OpenAI (Modelos LLM)
                - 🏢 Active Directory (Autenticação)
                - 📚 GitLab (Repositório de código)
                
                **Infraestrutura:**
                - 🐳 Docker (Containerização)
                - 🔄 CI/CD Pipeline (Automação)
                """)
        
        # Call to action
        st.markdown("---")
        st.markdown("## 🚀 Pronto para Começar?")
        
        st.success("""
        **Escolha uma funcionalidade no menu lateral e comece a explorar o CodeGuardian!**
        
        Cada página possui instruções detalhadas e exemplos práticos para ajudá-lo a obter os melhores resultados.
        """)
        
        # Footer com informações adicionais
        st.markdown("---")
        
        footer_cols = st.columns(3)
        
        with footer_cols[0]:
            st.markdown("""
            **📞 Suporte:**
            
            Time de Qualidade de Software
            
            Governança de Tecnologia
            """)
        
        with footer_cols[1]:
            st.markdown("""
            **📖 Documentação:**
            
            Consulte o README.md do projeto
            
            para informações técnicas
            """)
        
        with footer_cols[2]:
            st.markdown("""
            **🔗 Links Úteis:**
            
            API Docs: /docs
            
            Status: Verificar na sidebar
            """)
