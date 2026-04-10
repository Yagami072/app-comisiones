@echo off
REM Script de instalación rápida para Audio Cloner Pro
echo.
echo ============================================
echo   Audio Cloner Pro - Instalador
echo ============================================
echo.

REM Verificar si Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python no está instalado o no está en el PATH
    echo Descarga Python desde: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/3] Actualizando pip...
python -m pip install --upgrade pip

echo.
echo [2/3] Instalando dependencias...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo Error al instalar algunas dependencias.
    echo Intentando instalar PyAudio con pipwin...
    pip install pipwin
    pipwin install pyaudio
)

echo.
echo [3/3] Verificando instalación...
python -c "import PyQt5; import pyaudio; import numpy; import matplotlib; print('✓ Todas las dependencias están instaladas correctamente')"

if %errorlevel% neq 0 (
    echo.
    echo Error: Falló la verificación de algunos paquetes
    echo Por favor, intenta instalar manualmente con: pip install -r requirements.txt
    pause
    exit /b 1
)

echo.
echo ============================================
echo   ✓ Instalación completada exitosamente
echo ============================================
echo.
echo Para ejecutar la aplicación, usa:
echo   python audio_cloner.py
echo.
pause
