@echo off

cd /d "%~dp0"

:: AÃ±adir la carpeta tools al inicio del PATH para esta sesiÃ³n
set "PATH=%~dp0tools;%PATH%"

:: Ejecutar el Python embebido
"%~dp0python\python.exe" %*