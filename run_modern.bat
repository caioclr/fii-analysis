@echo off
chcp 65001 > nul
echo ========================================================
echo    ANALISYS PRO - Modern FII Intelligence Terminal
echo ========================================================
echo.

:: 1. Iniciar API FastAPI em background
echo [1/2] Iniciando Servidor Backend FastAPI (Porta 8000)...
start "Analisys API Backend" cmd /k ".\venv\Scripts\python.exe -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000 --reload"

:: Aguardar 2 segundos para o backend subir
timeout /t 2 /nobreak > nul

:: 2. Iniciar Frontend SPA com Vite
echo [2/2] Iniciando Frontend SPA Vite + React (Porta 5533)...
cd frontend
start "Analisys Frontend SPA" cmd /k "npm.cmd run dev"

:: Aguardar 3 segundos e abrir navegador
timeout /t 3 /nobreak > nul
echo.
echo Abrindo o Terminal no navegador: http://localhost:5533
start http://localhost:5533

echo.
echo ========================================================
echo Terminal em execucao! Pressione qualquer tecla para fechar este script.
echo (Os servidores continuarao rodando em suas proprias janelas)
echo ========================================================
pause > nul
