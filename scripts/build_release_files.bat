@ECHO OFF

ECHO Clear up dist\...
IF EXIST ..\dist (
    REM -
) ELSE (
    MKDIR ..\dist
)
DEL /F /Q ..\dist\*



ECHO - re-build program version
CALL gen_ver_file.bat
if %ERRORLEVEL% NEQ 0 ( echo ERROR: Failure && pause && exit /b %errorlevel% )



COPY ..\src\setup.py ..\dist\
COPY ..\README.md ..\dist\
COPY ..\LICENSE ..\dist\
ECHO # > ..\dist\requirements.txt
COPY .\setup.bat ..\dist\
powershell -NoProfile -Command ^
  "(Get-Content '..\dist\setup.bat') -Replace 'PUSHD ..', 'PUSHD .' | Set-Content '..\dist\setup.bat'"
COPY .\uninstall.bat ..\dist\
powershell -NoProfile -Command ^
  "(Get-Content '..\dist\uninstall.bat') -Replace 'PUSHD ..', 'PUSHD .' | Set-Content '..\dist\uninstall.bat'"
COPY ..\src\setup_files_data.py ..\dist\
MKDIR ..\dist\GENERATED
COPY ..\src\GENERATED\* ..\dist\GENERATED\


