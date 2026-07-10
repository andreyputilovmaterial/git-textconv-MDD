@ECHO OFF

SET "TARGET_FOLDER=C:\Users\%USERNAME%\AppData\Local\gittextconvmdd"

PUSHD ..

ECHO - prepare python env
python -m venv .venv
if %ERRORLEVEL% NEQ 0 ( echo ERROR: Failure && pause && exit /b %errorlevel% )
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 ( echo ERROR: Failure && pause && exit /b %errorlevel% )

ECHO - copy files to %TARGET_FOLDER%
.\.venv\Scripts\python.exe setup.py --program install --action copy-program-files --path "%TARGET_FOLDER%"
if %ERRORLEVEL% NEQ 0 ( echo ERROR: Failure && pause && exit /b %errorlevel% )

ECHO - register in git
.\.venv\Scripts\python.exe setup.py --program install --action git-register --path "%TARGET_FOLDER%"
if %ERRORLEVEL% NEQ 0 ( echo ERROR: Failure && pause && exit /b %errorlevel% )

.\.venv\Scripts\python.exe setup.py --program done
if %ERRORLEVEL% NEQ 0 ( echo ERROR: Failure && pause && exit /b %errorlevel% )

POPD
