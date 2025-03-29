@echo off
cd %~dp0
echo Activating virtual environment venv and upgrading pip...
call "venv\Scripts\activate"
python -m pip install --upgrade pip
echo Pip has been upgraded in the virtual environment venv.
echo To deactivate, manually type 'deactivate'.
call "venv\Scripts\activate"
