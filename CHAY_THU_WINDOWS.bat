@echo off
setlocal EnableExtensions
chcp 65001 >nul
cd /d "%~dp0"
if exist ".build-venv\Scripts\python.exe" (
 set "PY_CMD=.build-venv\Scripts\python.exe"
) else (
 where py >nul 2>nul
 if not errorlevel 1 (set "PY_CMD=py -3") else (set "PY_CMD=python")
)
%PY_CMD% -c "import sys;assert sys.version_info >= (3,10)"
if errorlevel 1 goto failed
%PY_CMD% -m pip show openpyxl >nul 2>nul
if errorlevel 1 (
 echo Openpyxl missing. Use TAO_EXE_WINDOWS.bat to create the complete EXE.
 goto failed
)
%PY_CMD% "app.py"
if errorlevel 1 goto failed
exit /b 0
:failed
pause
exit /b 1
