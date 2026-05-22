@echo off
setlocal enabledelayedexpansion
title Nash Energy IT — Production Setup

:: ================================================================
::  Nash Energy IT Ticketing System — Production Setup Script
::  Run ONCE on the server as Administrator.
::
::  BEFORE RUNNING:
::    1. Fill in your settings in the CONFIGURATION section below
::    2. Right-click this file and select "Run as administrator"
:: ================================================================


:: ================================================================
::  CONFIGURATION — Edit these values before running
:: ================================================================

:: PostgreSQL superuser password (the 'postgres' account password)
set PG_SUPERPASS=your_postgres_superuser_password_here

:: New database credentials (will be created fresh)
:: NOTE: Do not use @ or ! in DB_PASS — they break the PostgreSQL connection URL
set DB_NAME=nash_energy_db
set DB_USER=nash_db_user
set DB_PASS=NashProd2025Secure
set DB_PORT=5432

:: Admin account that gets seeded into the app on first run
set ADMIN_EMAIL=admin@nashenergy.com
set ADMIN_PASS=Admin@NashIT2025!

:: ================================================================
::  DO NOT EDIT BELOW THIS LINE
:: ================================================================

set APP_DIR=%~dp0
set APP_DIR=%APP_DIR:~0,-1%
set VENV_DIR=%APP_DIR%\venv
set VENV_PYTHON=%VENV_DIR%\Scripts\python.exe
set VENV_PYTHONW=%VENV_DIR%\Scripts\pythonw.exe
set VENV_PIP=%VENV_DIR%\Scripts\pip.exe
set TASK_NAME=NashEnergyIT
set APP_PORT=5008

echo.
echo  ==========================================
echo   Nash Energy IT ^| Production Setup
echo  ==========================================
echo.

:: --- Check: Running as Administrator ---
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ERROR] This script must be run as Administrator.
    echo          Right-click setup.bat and choose "Run as administrator".
    pause
    exit /b 1
)
echo  [OK] Running as Administrator

:: --- Check: Python is available ---
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ERROR] Python is not installed or not in PATH.
    echo          Install Python 3.11+ from https://python.org and try again.
    pause
    exit /b 1
)
echo  [OK] Python found

:: --- Find psql — check PATH first, then search common install locations ---
set PSQL_EXE=psql
psql --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  psql not in PATH — searching common PostgreSQL install locations...
    set PSQL_EXE=
    for /d %%V in ("C:\Program Files\PostgreSQL\*") do (
        if exist "%%V\bin\psql.exe" (
            set PSQL_EXE=%%V\bin\psql.exe
            set PATH=%%V\bin;!PATH!
        )
    )
    if not defined PSQL_EXE (
        echo  [ERROR] Could not find psql.exe anywhere under C:\Program Files\PostgreSQL\
        echo          Make sure PostgreSQL is installed and try again.
        pause
        exit /b 1
    )
    echo  [OK] PostgreSQL found at: !PSQL_EXE!
) else (
    echo  [OK] PostgreSQL psql found in PATH
)

echo.
echo  [1/6] Setting up PostgreSQL database...
echo  ----------------------------------------

set PGPASSWORD=%PG_SUPERPASS%

echo  Dropping existing database and user (if any)...
"!PSQL_EXE!" -U postgres -h localhost -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '%DB_NAME%';" >nul 2>&1
"!PSQL_EXE!" -U postgres -h localhost -c "DROP DATABASE IF EXISTS %DB_NAME%;" >nul 2>&1
"!PSQL_EXE!" -U postgres -h localhost -c "DROP USER IF EXISTS %DB_USER%;" >nul 2>&1

echo  Creating fresh database user and database...
"!PSQL_EXE!" -U postgres -h localhost -c "CREATE USER %DB_USER% WITH PASSWORD '%DB_PASS%';"
if %errorlevel% neq 0 (
    echo  [ERROR] Failed to create database user. Check your PG_SUPERPASS setting.
    pause
    exit /b 1
)
"!PSQL_EXE!" -U postgres -h localhost -c "CREATE DATABASE %DB_NAME% OWNER %DB_USER% ENCODING 'UTF8';"
"!PSQL_EXE!" -U postgres -h localhost -c "GRANT ALL PRIVILEGES ON DATABASE %DB_NAME% TO %DB_USER%;"
echo  [OK] Database %DB_NAME% created and ready

echo.
echo  [2/6] Setting up Python virtual environment...
echo  ------------------------------------------------

echo  Removing old virtual environment (if any)...
if exist "%VENV_DIR%" rmdir /s /q "%VENV_DIR%"

echo  Creating fresh virtual environment...
python -m venv "%VENV_DIR%"
if %errorlevel% neq 0 (
    echo  [ERROR] Failed to create virtual environment.
    pause
    exit /b 1
)
echo  [OK] Virtual environment ready

echo.
echo  [3/6] Installing Python dependencies...
echo  -----------------------------------------
"%VENV_PYTHON%" -m pip install --upgrade pip setuptools wheel --quiet
"%VENV_PYTHON%" -m pip install -r "%APP_DIR%\requirements.txt" --quiet
if %errorlevel% neq 0 (
    echo  [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)
echo  [OK] All dependencies installed

echo.
echo  [4/6] Writing production .env file...
echo  ---------------------------------------

:: Generate a random 64-character secret key using Python
for /f %%i in ('"%VENV_PYTHON%" -c "import secrets; print(secrets.token_hex(32))"') do set SECRET_KEY=%%i

(
echo FLASK_ENV=production
echo SECRET_KEY=!SECRET_KEY!
echo.
echo DATABASE_URL=postgresql://%DB_USER%:%DB_PASS%@localhost:%DB_PORT%/%DB_NAME%
echo.
echo # Microsoft Graph API ^(Email^)
echo AZURE_TENANT_ID=388c9e20-2597-4b8d-bbbc-ebbf53bce879
echo AZURE_CLIENT_ID=f1efdd2d-0504-4a3d-99cb-36e9f150ef7c
echo AZURE_CLIENT_SECRET=your-azure-client-secret-here
echo MAIL_SENDER_EMAIL=ppc@nashenergy.in
echo MAIL_SENDER_NAME=Nash Energy
echo.
echo UPLOAD_FOLDER=app/static/uploads
echo MAX_CONTENT_LENGTH=5242880
echo.
echo ADMIN_EMAIL=%ADMIN_EMAIL%
echo ADMIN_PASSWORD=%ADMIN_PASS%
) > "%APP_DIR%\.env"

echo  [OK] .env written with fresh secret key

echo.
echo  [5/6] Creating logs and uploads directories...
echo  -------------------------------------------------
if not exist "%APP_DIR%\logs" mkdir "%APP_DIR%\logs"
if not exist "%APP_DIR%\app\static\uploads" mkdir "%APP_DIR%\app\static\uploads"
echo  [OK] Directories ready

echo.
echo  [5b/6] Opening firewall port %APP_PORT%...
echo  ------------------------------------------
netsh advfirewall firewall delete rule name="Nash Energy IT - Port %APP_PORT%" >nul 2>&1
netsh advfirewall firewall add rule name="Nash Energy IT - Port %APP_PORT%" dir=in action=allow protocol=TCP localport=%APP_PORT%
echo  [OK] Firewall rule added for port %APP_PORT%

echo.
echo  [6/6] Registering auto-start Windows Task...
echo  ----------------------------------------------

:: Remove old task if exists
schtasks /delete /tn "%TASK_NAME%" /f >nul 2>&1

:: Register task: runs pythonw.exe (no console window) on system startup, as SYSTEM
schtasks /create ^
    /tn "%TASK_NAME%" ^
    /tr "\"%VENV_PYTHONW%\" \"%APP_DIR%\serve.py\"" ^
    /sc onstart ^
    /ru SYSTEM ^
    /rl HIGHEST ^
    /delay 0001:00 ^
    /f

if %errorlevel% neq 0 (
    echo  [ERROR] Failed to register scheduled task.
    pause
    exit /b 1
)
echo  [OK] Task "%TASK_NAME%" registered — app will start automatically on every boot

echo.
echo  Starting the app now for the first time...
echo  (This initialises the database schema and seeds the admin account)
echo.
schtasks /run /tn "%TASK_NAME%"

:: Wait a few seconds for the server to boot
timeout /t 5 /nobreak >nul

echo.
echo  =====================================================
echo   Setup Complete!
echo  =====================================================
echo.
echo   App URL   :  http://%COMPUTERNAME%:%APP_PORT%
echo   Admin     :  %ADMIN_EMAIL%
echo   Password  :  %ADMIN_PASS%
echo.
echo   Database  :  %DB_NAME%
echo   DB User   :  %DB_USER%
echo.
echo   Logs      :  %APP_DIR%\logs\
echo.
echo   IMPORTANT: Change the admin password after first login!
echo  =====================================================
echo.

pause
endlocal
