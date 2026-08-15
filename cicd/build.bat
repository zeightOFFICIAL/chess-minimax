@echo off
call .venv\Scripts\activate
pyinstaller --onefile --noconsole --icon "resources/icons/icon.ico" --add-data "resources;resources" --add-data "config.txt;." main.py
if %errorlevel% neq 0 exit /b %errorlevel%
copy /y config.txt dist\
echo Build complete. Exe and config.txt are in dist\