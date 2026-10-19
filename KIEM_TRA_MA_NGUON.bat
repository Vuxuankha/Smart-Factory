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
%PY_CMD% -m unittest discover -s tests -p "test_*.py" -v >"KET_QUA_TEST_V16.txt" 2>&1
if errorlevel 1 (
 echo TEST FAILED. See KET_QUA_TEST_V16.txt
 type "KET_QUA_TEST_V16.txt"
 pause
 exit /b 1
)
echo ALL LOCAL MOCK TESTS PASSED
pause
exit /b 0
