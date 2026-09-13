@echo off
setlocal EnableExtensions
pushd "%~dp0.." || exit /b 1
set "CDU_ARTIST_PYTHON="
if "%~1"=="setup" goto find_python
if exist ".venv\Scripts\python.exe" set "CDU_ARTIST_PYTHON=%CD%\.venv\Scripts\python.exe"
if defined CDU_ARTIST_PYTHON goto run
echo Run Setup Artist Tools.cmd once before building.
goto failure

:find_python
if defined PYTHON_EXE call :candidate "%PYTHON_EXE%"
if exist ".venv\Scripts\python.exe" call :candidate "%CD%\.venv\Scripts\python.exe"
for /f "delims=" %%P in ('py -3.12 -c "import sys; print(sys.executable)" 2^>nul') do call :candidate "%%P"
for /f "delims=" %%P in ('where python.exe 2^>nul') do call :candidate "%%P"
call :candidate "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
call :candidate "%ProgramFiles%\Python312\python.exe"
call :candidate "%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if defined CDU_ARTIST_PYTHON goto run
echo Python 3.12 was not found. Install Python 3.12 for Windows, then rerun this file.
echo Official downloads: https://www.python.org/downloads/windows/
echo Or set PYTHON_EXE to the full path of an existing Python 3.12 interpreter.
goto failure

:candidate
if defined CDU_ARTIST_PYTHON exit /b 0
if not exist "%~1" exit /b 0
echo "%~1" | findstr /i "WindowsApps" >nul && exit /b 0
"%~1" -c "import sys; raise SystemExit(0 if sys.version_info[:2] == (3,12) else 1)" >nul 2>nul
if not errorlevel 1 set "CDU_ARTIST_PYTHON=%~1"
exit /b 0

:run
"%CDU_ARTIST_PYTHON%" "tools\artist.py" "%~1"
set "CDU_ARTIST_RESULT=%errorlevel%"
if not "%CDU_ARTIST_RESULT%"=="0" goto failure
echo.
echo Completed. Press any key to close this window.
if not defined CDU_ARTIST_NO_PAUSE pause >nul
popd
exit /b 0

:failure
echo.
echo Artist tools did not finish. Read the message above; source artwork was not changed by setup.
if not defined CDU_ARTIST_NO_PAUSE pause
popd
exit /b 1
