@echo off
call .venv\Scripts\activate
pyinstaller -y --onefile --noconsole --icon "resources/icons/icon.ico" --add-data "resources;resources" --add-data "config.txt;." --exclude-module numpy --exclude-module tkinter main.py
if %errorlevel% neq 0 exit /b %errorlevel%
copy /y config.txt dist\
echo Build complete. Exe and config.txt are in dist\