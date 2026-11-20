@echo off
setlocal EnableExtensions EnableDelayedExpansion

:: ============================================================
:: FENNIX 2 - Instalador portable
:: Crea un entorno Python portable con todas las dependencias.
:: Necesita conexion a internet (solo esta vez).
:: NO requiere Python preinstalado en el sistema.
:: Despues de setup, la carpeta es 100%% offline y portable.
:: ============================================================

set "ROOT=%~dp0"
set "PYEMB=%ROOT%Python"
set "EMB_PY=%PYEMB%\python.exe"
set "PTH=%PYEMB%\python312._pth"
set "REQ=%ROOT%requirements.txt"
set "WHEELS=%ROOT%wheels"
set "GETPIP=%ROOT%Tools\get-pip.py"
set "RAR=%ROOT%Rar.exe"

echo ============================================================
echo   FENNIX 2 - Instalador portable
echo ============================================================
echo.

:: --- 1/7. Extraer Python embebido si no existe ---
if not exist "%EMB_PY%" (
    if exist "%ROOT%Python.rar" (
        if not exist "%RAR%" (
            echo [ERROR] No se encontro Rar.exe para extraer el Python embebido.
            pause
            exit /b 1
        )
        echo [1/7] Descomprimiendo Python embebido...
        "%RAR%" x -y "%ROOT%Python.rar" "%ROOT%"
        if errorlevel 1 (
            echo [ERROR] Fallo la extraccion del Python embebido.
            pause
            exit /b 1
        )
    ) else (
        echo [ERROR] No existe el Python embebido ni Python.rar.
        pause
        exit /b 1
    )
) else (
    echo [1/7] Python embebido ya descomprimido.
)

:: --- 2/7. Verificar python312._pth ---
echo [2/7] Verificando configuracion del Python embebido...
if not exist "%PTH%" (
    echo [ERROR] No se encontro "%PTH%"
    pause
    exit /b 1
)

:: --- 3/7. Descargar get-pip.py ---
echo [3/7] Obteniendo get-pip.py...
if not exist "%GETPIP%" (
    if not exist "%ROOT%Tools" mkdir "%ROOT%Tools"
    powershell -Command "Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile '%GETPIP%'"
    if errorlevel 1 (
        echo [ERROR] No se pudo descargar get-pip.py
        pause
        exit /b 1
    )
) else (
    echo       get-pip.py ya existe.
)

:: --- 4/7. Instalar pip en el Python embebido ---
echo [4/7] Instalando pip en el Python embebido...
if not exist "%PYEMB%\Scripts\pip.exe" (
    "%EMB_PY%" "%GETPIP%" --no-warn-script-location
    if errorlevel 1 (
        echo [ERROR] Fallo la instalacion de pip en el embebido.
        pause
        exit /b 1
    )
) else (
    echo       pip ya instalado.
)

:: --- 4b/7. Instalar setuptools (necesario para construir sdists en pip download) ---
echo [4b/7] Instalando setuptools...
"%EMB_PY%" -m pip install --upgrade setuptools --no-warn-script-location
if errorlevel 1 (
    echo [ERROR] Fallo la instalacion de setuptools.
    pause
    exit /b 1
)

:: --- 5/7. Descargar dependencias como wheels ---
echo [5/7] Descargando dependencias a %WHEELS%...
if not exist "%WHEELS%" mkdir "%WHEELS%"
"%EMB_PY%" -m pip download -r "%REQ%" -d "%WHEELS%" --no-cache-dir
if errorlevel 1 (
    echo [ERROR] Fallo la descarga de dependencias.
    pause
    exit /b 1
)

:: --- 6/7. Instalar dependencias en el Python embebido (offline) ---
echo [6/7] Instalando dependencias en el Python embebido (offline)...
"%EMB_PY%" -m pip install --no-index --find-links="%WHEELS%" -r "%REQ%" --no-warn-script-location
if errorlevel 1 (
    echo [ERROR] Fallo la instalacion de dependencias en el embebido.
    pause
    exit /b 1
)

:: --- 7/7. Pre-descargar modelos PaddleOCR (portable) ---
echo [7/7] Descargando modelos PaddleOCR/PaddleX (portable)...
set "PADDLE_PDX_CACHE_HOME=%ROOT%models\paddlex"
if not exist "%ROOT%models" mkdir "%ROOT%models"
"%EMB_PY%" -c "from paddleocr import PaddleOCR; PaddleOCR(lang='es', use_doc_orientation_classify=False, use_doc_unwarping=False, use_textline_orientation=False)"
if errorlevel 1 (
    echo [ERROR] Fallo la descarga de modelos PaddleOCR.
    pause
    exit /b 1
)

:: --- Limpiar wheels temporales ---
echo.
echo [Limpieza] Eliminando wheels temporales...
if exist "%WHEELS%" rmdir /S /Q "%WHEELS%"

:: --- Limpiar __pycache__ ---
echo [Limpieza] Eliminando cache de Python...
for /d /r "%PYEMB%" %%d in (__pycache__) do (
    if exist "%%d" rmdir /S /Q "%%d"
)


