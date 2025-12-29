@echo off
setlocal

echo ==========================================
echo      VERIFICANDO SISTEMA DE BATALHA
echo ==========================================

:: 1. Verifica se o Python esta instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python nao encontrado!
    echo Por favor, instale o Python em python.org e marque "Add to PATH".
    pause
    exit /b
)

:: 2. Verifica se o Pygame existe
echo Checando municao (Bibliotecas)...
python -c "import pygame" >nul 2>&1

if %errorlevel% neq 0 (
    echo.
    echo [AVISO] Pygame nao detectado.
    echo Iniciando protocolo de instalacao automatica...
    echo.
    pip install pygame
    
    if %errorlevel% neq 0 (
        echo [ERRO CRITICO] Falha ao instalar Pygame. Verifique sua internet.
        pause
        exit /b
    )
    echo.
    echo [SUCESSO] Pygame instalado! Pronto para o combate.
) else (
    echo [OK] Sistema pronto.
)

echo.
echo ==========================================
echo        INICIANDO PONG MULTIPLAYER
echo ==========================================
echo.

:: --- AQUI COMEÇA A ABERTURA DAS JANELAS 
echo --- Invocando o Mestre (Servidor) ---
start "SERVER_MASTER" cmd /k "python server.py"

echo Aguardando o despertar do Mestre...
timeout /t 2 >nul

echo --- Invocando o Guerreiro 1 (Cliente) ---
start "CLIENTE_P1" cmd /k "python client.py"

echo --- Invocando o Guerreiro 2 (Cliente) ---
start "CLIENTE_P2" cmd /k "python client.py"

echo.
echo ========================================================
echo  MODO VIGILIA ATIVO:
echo  Mantenha esta janela aberta.
echo  Se voce fechar a janela do SERVER_MASTER,
echo  os clientes fecharao automaticamente.
echo ========================================================

:MONITOR
timeout /t 1 >nul
tasklist /FI "WINDOWTITLE eq SERVER_MASTER" 2>NUL | find /I /N "cmd.exe">NUL
if "%ERRORLEVEL%"=="1" (
    echo.
    echo O Mestre partiu. Encerrando a sessao...
    taskkill /FI "WINDOWTITLE eq CLIENTE_P1" /IM cmd.exe /F >nul 2>&1
    taskkill /FI "WINDOWTITLE eq CLIENTE_P2" /IM cmd.exe /F >nul 2>&1
    echo Limpeza concluida.
    timeout /t 2 >nul
    exit
)
goto MONITOR