@echo off
REM Script para ejecutar Audio Cloner Pro

echo Iniciando Audio Cloner Pro...
python audio_cloner.py

if %errorlevel% neq 0 (
    echo.
    echo Error al ejecutar la aplicación.
    echo Por favor, asegúrate de que:
    echo 1. Python está instalado
    echo 2. Las dependencias están instaladas (ejecuta instalar.bat)
    echo 3. El archivo audio_cloner.py existe en esta carpeta
    echo.
    pause
)
