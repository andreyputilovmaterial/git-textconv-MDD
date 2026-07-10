@ECHO OFF

SET "TARGET_FOLDER=C:\Users\%USERNAME%\AppData\Local\gittextconvmdd"

PUSHD ..

ECHO Update program version
IF NOT EXIST "src\GENERATED" (
    MKDIR "src\GENERATED"
)
ECHO '''For auto-generated files''' > src\GENERATED\__init__.py
ECHO # THIS IS AUTO-GENERATED > src\GENERATED\_VERSION.py
python -c "from datetime import datetime; print(f'# {datetime.now()}')" >> src\GENERATED\_VERSION.py
ECHO _VERSION = ''' >> src\GENERATED\_VERSION.py
git describe --tags --dirty >> src\GENERATED\_VERSION.py
ECHO ''' >> src\GENERATED\_VERSION.py
ECHO Done

POPD
