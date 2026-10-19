@echo off
setlocal EnableExtensions
chcp 65001 >nul
cd /d "%~dp0"
title Tao Alibaba Operations Center V16.0.14 EXE

echo ===============================
echo Alibaba Operations Center V16.0.14 Builder
 echo ===============================
if not exist "app.py" goto missing
if not exist "SaoLuuAlibabaMailV16.spec" goto missing
if not exist "requirements-build.txt" goto missing

where py >nul 2>nul
if not errorlevel 1 (
  set "PY_CMD=py -3"
) else (
  set "PY_CMD=python"
)
%PY_CMD% -c "import sys;assert sys.version_info >= (3,10), 'Python 3.10+ required';print(sys.version)"
if errorlevel 1 goto no_python

if not exist ".build-venv\Scripts\python.exe" (
  %PY_CMD% -m venv ".build-venv"
  if errorlevel 1 goto venv_error
)
set "BUILD_PY=.build-venv\Scripts\python.exe"
set "PIP_DISABLE_PIP_VERSION_CHECK=1"
echo Installing isolated build dependencies. See BUILD_V16.log
"%BUILD_PY%" -m pip install --no-cache-dir -r "requirements-build.txt" >"BUILD_V16.log" 2>&1
if errorlevel 1 goto build_error
"%BUILD_PY%" -m PyInstaller --clean --noconfirm "SaoLuuAlibabaMailV16.spec" >>"BUILD_V16.log" 2>&1
if errorlevel 1 goto build_error
if not exist "dist\AlibabaOperationsCenter.exe" goto build_error
echo Verifying portable executable...
"dist\AlibabaOperationsCenter.exe" --self-test
if errorlevel 1 goto test_error

echo.
echo THANH CONG:
echo "%CD%\dist\AlibabaOperationsCenter.exe"
echo Copy ONLY this EXE to other Windows computers. They do not need Python.
echo Build log: "%CD%\BUILD_V16.log"
where certutil >nul 2>nul
if not errorlevel 1 certutil -hashfile "dist\AlibabaOperationsCenter.exe" SHA256
pause
exit /b 0
:missing
echo ERROR: Source files missing. Extract the entire ZIP first.
goto failed
:no_python
echo ERROR: Python 3.10+ is required ONLY on the building machine.
goto failed
:venv_error
echo ERROR: Could not create isolated virtual environment.
goto failed
:build_error
echo ERROR: Build failed. Open BUILD_V16.log for details.
goto failed
:test_error
echo ERROR: EXE self-test failed; do not distribute this build.
goto failed
:failed
pause
exit /b 1
