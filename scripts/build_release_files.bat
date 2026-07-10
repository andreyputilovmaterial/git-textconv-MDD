@ECHO OFF

ECHO Clear up dist\...
IF EXIST ..\dist (
    RD /S /Q ..\dist
)
MKDIR ..\dist



ECHO - re-build program version
CALL gen_ver_file.bat
if %ERRORLEVEL% NEQ 0 ( echo ERROR: Failure && pause && exit /b %errorlevel% )


@REM ECHO - Copy program files
@REM COPY ..\src\setup.py ..\dist\
@REM COPY ..\src\setup_files_data.py ..\dist\
@REM MKDIR ..\dist\GENERATED
@REM COPY ..\src\GENERATED\* ..\dist\GENERATED\

PUSHD ..
ECHO - Deliver program through pinliner
ECHO Produce distributable .py bundle - calling pinliner...
REM REM :: comment: please delete .pyc files before every call of the setup - this is implemented in my fork of the pinliner
@REM python src_dev_build\lib\pinliner\pinliner\pinliner.py src -o dist\setup.py --verbose
python src_dev_build\lib\pinliner\pinliner\pinliner.py src -o dist\setup.py
if %ERRORLEVEL% NEQ 0 ( echo ERROR: Failure && pause && exit /b %errorlevel% )
ECHO Done

ECHO -
ECHO -
ECHO Patching setup.py...
ECHO # ... >> dist\setup.py
ECHO # print('within setup') >> dist\setup.py
REM REM :: no need for this, the root package is loaded automatically
@REM ECHO # import setup >> dist\setup.py
ECHO from src import setup >> dist\setup.py
ECHO setup.main() >> dist\setup.py
ECHO # print('out of setup') >> dist\setup.py
ECHO Done
POPD


ECHO - Copy all other files - README, LICENSE, etc
COPY ..\README.md ..\dist\
COPY ..\LICENSE ..\dist\
ECHO # > ..\dist\requirements.txt

ECHO - Copy scripts
COPY .\setup.bat ..\dist\
powershell -NoProfile -Command ^
  "(Get-Content '..\dist\setup.bat') -Replace 'PUSHD ..', 'PUSHD .' | Set-Content '..\dist\setup.bat'"
COPY .\uninstall.bat ..\dist\
powershell -NoProfile -Command ^
  "(Get-Content '..\dist\uninstall.bat') -Replace 'PUSHD ..', 'PUSHD .' | Set-Content '..\dist\uninstall.bat'"


