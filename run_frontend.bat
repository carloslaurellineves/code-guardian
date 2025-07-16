@echo off
echo 🚀 Iniciando Code Guardian Frontend...
echo.

REM Verificar se o ambiente virtual existe
if not exist ".venv" (
    echo ❌ Ambiente virtual não encontrado!
    echo Por favor, crie o ambiente virtual primeiro:
    echo    python -m venv .venv
    echo    .venv\Scripts\activate
    echo    pip install -r requirements.txt
    pause
    exit /b 1
)

REM Ativar ambiente virtual e executar Streamlit
echo ✅ Ativando ambiente virtual...
call .venv\Scripts\activate

echo ✅ Executando aplicação Streamlit...
echo.
echo 🌐 A aplicação será aberta em: http://localhost:8501
echo 🛡️  Para parar a aplicação, pressione Ctrl+C
echo.

streamlit run app/streamlit_app.py --server.headless=false --server.port=8501

pause
