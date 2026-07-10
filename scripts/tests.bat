@ECHO OFF

SET "TARGET_FOLDER=C:\Users\%USERNAME%\AppData\Local\gittextconvmdd"

PUSHD ..

ECHO - prepare python env
python -m venv .venv
if %ERRORLEVEL% NEQ 0 ( echo ERROR: Failure && pause && exit /b %errorlevel% )
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 ( echo ERROR: Failure && pause && exit /b %errorlevel% )
.\.venv\Scripts\python.exe -m pip install pytest pytest-html
if %ERRORLEVEL% NEQ 0 ( echo ERROR: Failure && pause && exit /b %errorlevel% )

ECHO - run tests
.\.venv\Scripts\python.exe -m pytest --html=report.html
if %ERRORLEVEL% NEQ 0 ( echo ERROR: Failure && pause && exit /b %errorlevel% )

POPD
