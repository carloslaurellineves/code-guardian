#!/usr/bin/env pwsh

Write-Host "🚀 Iniciando Code Guardian Frontend..." -ForegroundColor Green
Write-Host ""

# Verificar se o ambiente virtual existe
if (-not (Test-Path ".venv")) {
    Write-Host "❌ Ambiente virtual não encontrado!" -ForegroundColor Red
    Write-Host "Por favor, crie o ambiente virtual primeiro:" -ForegroundColor Yellow
    Write-Host "   python -m venv .venv" -ForegroundColor Yellow
    Write-Host "   .venv\Scripts\activate" -ForegroundColor Yellow
    Write-Host "   pip install -r requirements.txt" -ForegroundColor Yellow
    Read-Host "Pressione Enter para continuar..."
    exit 1
}

# Ativar ambiente virtual e executar Streamlit
Write-Host "✅ Ativando ambiente virtual..." -ForegroundColor Green
& .venv\Scripts\activate.ps1

Write-Host "✅ Executando aplicação Streamlit..." -ForegroundColor Green
Write-Host ""
Write-Host "🌐 A aplicação será aberta em: http://localhost:8501" -ForegroundColor Cyan
Write-Host "🛡️  Para parar a aplicação, pressione Ctrl+C" -ForegroundColor Yellow
Write-Host ""

# Executar Streamlit
& .venv\Scripts\streamlit run app/streamlit_app.py --server.headless=false --server.port=8501

Read-Host "Pressione Enter para continuar..."
