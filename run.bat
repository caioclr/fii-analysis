@echo off
title Analisys - Carteira de Investimentos
echo ========================================================
echo   Iniciando o Dashboard de Analise de Investimentos...
echo ========================================================
echo.

if not exist venv (
    echo [INFO] Criando ambiente virtual venv...
    python -m venv venv
    call .\venv\Scripts\activate.bat
    echo [INFO] Instalando dependencias...
    pip install -r requirements.txt
) else (
    call .\venv\Scripts\activate.bat
)

echo [INFO] Abrindo o dashboard interativo no seu navegador...
streamlit run app.py

pause
