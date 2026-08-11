@echo off

if "%~1"=="-rf" goto frontend
if "%~1"=="-b" goto backend
if "%~1"=="-if" goto install_frontend

echo Invalid or missing argument.
echo Usage: setup [option]
echo   -rf   : Go to frontend and Run frontend (npm run dev)
echo   -b   : Go to backend and Activate Python venv for backend
echo   -if  : Go to frontend and Install node modules and run frontend
goto :eof

:frontend
echo Changing directory to frontend......
cd frontend
echo Dirctory changed to frontend!!
echo Starting frontend development server...
REM Using 'call' prevents the batch script from exiting after running npm
call npm run dev
goto :eof

:install_frontend
cd frontend
echo Installing node modules...
call npm install
echo Starting frontend development server...
call npm run dev
goto :eof

:backend
REM Change 'venv' to your actual virtual environment folder name if it is different (e.g., .venv)
if exist "backend\.venv\Scripts\activate.bat" (
    echo Changing directory to backend......
    cd backend
    echo Dirctory changed to backend!!
    echo Activating Python virtual environment...
    call .venv\Scripts\activate
    echo Virtual environment activated!
    
    REM Optional: Add your backend run command here so it starts automatically
    REM For example: python manage.py runserver 
    REM Or: fastapi dev main.py
) else (
    echo Error: Virtual environment not found at .venv\Scripts\activate.bat
)
goto :eof