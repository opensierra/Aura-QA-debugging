@echo off
setlocal EnableExtensions EnableDelayedExpansion

:: ============================================================
:: AURA QA - Configuracion del entorno Python portable
:: Necesita internet (solo esta vez). No requiere Python instalado.
:: Uso manual:        setup.bat
:: Desde el instalador: setup.bat /installer   (sin pausas)
:: ============================================================

set "PAUSE_CMD=pause"
if /I "%~1"=="/installer" set "PAUSE_CMD=rem"

:: salida en tiempo real y sin barras de progreso (se ven mal en el log)
set "PYTHONUNBUFFERED=1"
set "PIP_PROGRESS_BAR=off"
set "PIP_DISABLE_PIP_VERSION_CHECK=1"

set "ROOT=%~dp0"
set "PYEMB=%ROOT%Python"
set "EMB_PY=%PYEMB%\python.exe"
set "PTH=%PYEMB%\python312._pth"
set "REQ=%ROOT%requirements.txt"
set "GETPIP=%ROOT%Tools\get-pip.py"
set "RAR=%ROOT%Rar.exe"

echo ============================================================
echo   AURA QA - Configuracion del entorno
echo ============================================================
echo.

:: --- 1/5. Extraer Python embebido ---
if not exist "%EMB_PY%" (
    if not exist "%ROOT%Python.rar" (
        echo [ERROR] No existe el Python embebido ni Python.rar.
        %PAUSE_CMD%
        exit /b 1
    )
    if not exist "%RAR%" (
        echo [ERROR] No se encontro Rar.exe.
        %PAUSE_CMD%
        exit /b 1
    )
    echo [1/5] Descomprimiendo Python embebido...
    "%RAR%" x -y "%ROOT%Python.rar" "%ROOT%"
    if errorlevel 1 (
        echo [ERROR] Fallo la extraccion del Python embebido.
        %PAUSE_CMD%
        exit /b 1
    )
) else (
    echo [1/5] Python embebido ya descomprimido.
)

:: --- 2/5. Verificar python312._pth ---
:: Importante: dentro de este archivo la linea "import site" debe estar SIN '#', si no pip no funciona.
echo [2/5] Verificando configuracion del Python embebido...
if not exist "%PTH%" (
    echo [ERROR] No se encontro "%PTH%"
    %PAUSE_CMD%
    exit /b 1
)

:: --- 3/5. get-pip.py ---
echo [3/5] Obteniendo get-pip.py...
if not exist "%GETPIP%" (
    if not exist "%ROOT%Tools" mkdir "%ROOT%Tools"
    powershell -NoProfile -Command "Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile '%GETPIP%'"
    if errorlevel 1 (
        echo [ERROR] No se pudo descargar get-pip.py. Revisa tu conexion a internet.
        %PAUSE_CMD%
        exit /b 1
    )
) else (
    echo       get-pip.py ya existe.
)

:: --- 4/5. pip + dependencias (instalacion directa, sin paso intermedio de wheels) ---
echo [4/5] Instalando pip y dependencias...
if not exist "%PYEMB%\Scripts\pip.exe" (
    "%EMB_PY%" "%GETPIP%" --no-warn-script-location
    if errorlevel 1 (
        echo [ERROR] Fallo la instalacion de pip.
        %PAUSE_CMD%
        exit /b 1
    )
)
"%EMB_PY%" -m pip install --upgrade setuptools --no-warn-script-location
if errorlevel 1 (
    echo [ERROR] Fallo la instalacion de setuptools.
    %PAUSE_CMD%
    exit /b 1
)
"%EMB_PY%" -m pip install -r "%REQ%" --no-warn-script-location
if errorlevel 1 (
    echo [ERROR] Fallo la instalacion de dependencias.
    %PAUSE_CMD%
    exit /b 1
)

:: --- 5/5. Modelos PaddleOCR ---
echo [5/5] Descargando modelos PaddleOCR/PaddleX...
set "PADDLE_PDX_CACHE_HOME=%ROOT%models\paddlex"
if not exist "%ROOT%models" mkdir "%ROOT%models"
"%EMB_PY%" -c "from paddleocr import PaddleOCR; PaddleOCR(lang='es', use_doc_orientation_classify=False, use_doc_unwarping=False, use_textline_orientation=False)"
if errorlevel 1 (
    echo [ERROR] Fallo la descarga de modelos PaddleOCR.
    %PAUSE_CMD%
    exit /b 1
)

:: --- Limpieza ---
echo.
echo [Limpieza] Eliminando cache de Python...
for /d /r "%PYEMB%" %%d in (__pycache__) do (
    if exist "%%d" rmdir /S /Q "%%d"
)

echo.
echo Configuracion completada.
%PAUSE_CMD%
exit /b 0
