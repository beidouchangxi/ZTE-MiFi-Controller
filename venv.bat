@echo off

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM For the input filename handling
set filename=%~n1
set extension=%~x1
set option=%2

if "%option:~0,1%" == "d" (
    if exist "%filename%.exe" (
        goto NO_VENV
    )
)

REM Check if ntlm proxy is detected
netstat -ano | findstr "3128" > nul
set use_proxy=%errorlevel%

if exist .venv (
    REM echo Python venv detected, activating...
    call .venv\Scripts\activate.bat
) else (
    echo No python venv detected, creating...

    python -m venv .venv
    call .venv\Scripts\activate.bat

    echo *> .venv\.gitignore

    if exist requirements.txt (
        echo Detected requirements.txt...
        if %use_proxy% == 0 (
            echo GoNTLM-Proxy is detected
            .venv\Scripts\pip install -r requirements.txt --proxy=127.0.0.1:3128
        ) else (
            .venv\Scripts\pip install -r requirements.txt
        )
    ) 
)

:NO_VENV

if "%1" == "" (
    REM no argument, enter venv and leave the window to user
    cmd /k
) else (
    if "%2" == "" (
        REM only one argument, assume it's a python script
        if exist "%1" (
            if /i "%extension%" == ".py" (
                REM echo Starting %1 in venv...
                .venv\Scripts\python "%1"
            ) else (
                echo Invalid file extension. Only .py files are supported.
            )
        ) else (
            echo File %1 not found.
        )
    ) else (
        if /i "%option:~0,1%" == "d" (
            REM echo Divert enabled, look for exe file
            if exist "%filename%.exe" (
                REM echo Starting %filename%.exe...
                start "" "%filename%.exe"
            ) else (
                echo %filename%.exe not found, starting %1 in venv...
                .venv\Scripts\python "%1"
            )
        ) else (
            echo Invalid second argument. Only 'divert' is supported.
        )
    )
)
pause
