@echo off
echo Attempting to find python...
for /f "delims=" %%i in ('where python') do set "PYTHON_PATH=%%i" & goto :found
:found
echo Found Python at: %PYTHON_PATH%

echo Removing old venv...
if exist "venv" rmdir /s /q venv

echo Creating new venv...
"%PYTHON_PATH%" -m venv venv

echo Installing requirements...
call venv\Scripts\activate.bat
pip install -r requirements.txt

echo Done! Run "venv\Scripts\activate" and then "uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload"
