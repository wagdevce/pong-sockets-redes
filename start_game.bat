@echo off
echo --- Invocando o Mestre (Servidor) ---
:: Damos um nome exato para a janela: "SERVER_MASTER"
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
:: Espera 1 segundo antes de checar de novo (para nao gastar CPU)
timeout /t 1 >nul

:: Verifica se existe uma janela com o titulo "SERVER_MASTER"
tasklist /FI "WINDOWTITLE eq SERVER_MASTER" 2>NUL | find /I /N "cmd.exe">NUL

:: Se o ERRORLEVEL for 1, significa que nao achou a janela (Servidor fechou)
if "%ERRORLEVEL%"=="1" (
    echo.
    echo O Mestre partiu. Encerrando a sessao...
    
    :: Mata as janelas dos clientes pelo titulo
    taskkill /FI "WINDOWTITLE eq CLIENTE_P1" /IM cmd.exe /F >nul 2>&1
    taskkill /FI "WINDOWTITLE eq CLIENTE_P2" /IM cmd.exe /F >nul 2>&1
    
    echo Limpeza concluida.
    timeout /t 2 >nul
    exit
)

:: Se o servidor ainda esta la, volta para o inicio do loop
goto MONITOR