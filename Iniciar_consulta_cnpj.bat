@echo off
setlocal EnableExtensions
chcp 65001 >nul

REM ============================================================
REM CONSULTA DE CNPJ - INICIALIZADOR
REM Este arquivo deve ficar na mesma pasta do rodar.py
REM ============================================================

cd /d "%~dp0"
title Consulta de CNPJ

echo.
echo ============================================================
echo              CONSULTA DE CNPJ
echo ============================================================
echo.

REM Verifica se o arquivo principal existe
if not exist "%~dp0rodar.py" (
    echo ERRO: O arquivo rodar.py nao foi encontrado.
    echo.
    echo Mantenha estes arquivos na mesma pasta:
    echo   - Iniciar_Consulta_CNPJ.bat
    echo   - rodar.py
    echo.
    pause
    exit /b 1
)

REM Tenta localizar o inicializador py do Windows
where py >nul 2>&1

if not errorlevel 1 (
    set "PYTHON_CMD=py"
    goto :python_encontrado
)

REM Se nao encontrar py, tenta localizar python
where python >nul 2>&1

if not errorlevel 1 (
    set "PYTHON_CMD=python"
    goto :python_encontrado
)

REM Verifica o caminho utilizado no seu computador
if exist "C:\Program Files\Python313\python.exe" (
    set "PYTHON_CMD=C:\Program Files\Python313\python.exe"
    goto :python_encontrado
)

echo ERRO: O Python nao foi encontrado neste computador.
echo.
echo Instale o Python 3 ou solicite a instalacao ao suporte de TI.
echo Durante a instalacao, marque a opcao:
echo Add Python to PATH
echo.
pause
exit /b 1


:python_encontrado

REM Verifica se o Python localizado funciona
"%PYTHON_CMD%" --version >nul 2>&1

if errorlevel 1 (
    REM py e python normalmente nao precisam de aspas desta forma
    %PYTHON_CMD% --version >nul 2>&1
)

if errorlevel 1 (
    echo ERRO: O Python foi localizado, mas nao pode ser executado.
    echo.
    pause
    exit /b 1
)

echo Python encontrado.
echo Arquivo: %~dp0rodar.py
echo.
echo Verificando as bibliotecas e iniciando o aplicativo...
echo.

REM O rodar.py instala as bibliotecas ausentes e inicia o Streamlit
if "%PYTHON_CMD%"=="py" (
    py "%~dp0rodar.py"
) else if "%PYTHON_CMD%"=="python" (
    python "%~dp0rodar.py"
) else (
    "%PYTHON_CMD%" "%~dp0rodar.py"
)

set "CODIGO_SAIDA=%ERRORLEVEL%"

if not "%CODIGO_SAIDA%"=="0" (
    echo.
    echo ============================================================
    echo O APLICATIVO FOI ENCERRADO COM ERRO
    echo ============================================================
    echo.
    echo Codigo retornado: %CODIGO_SAIDA%
    echo.
    echo Verifique as mensagens apresentadas acima.
    echo Caso seja um computador corporativo, verifique tambem:
    echo   - conexao com a internet;
    echo   - VPN;
    echo   - proxy corporativo;
    echo   - permissao para instalar bibliotecas Python.
    echo.
    pause
    exit /b %CODIGO_SAIDA%
)

echo.
echo Aplicativo encerrado.
echo.

endlocal
exit /b 0