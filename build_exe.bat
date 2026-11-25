@echo off
rem Double-click this on a Windows computer that has Python installed.
rem It makes  dist\QB-Throw-Speed.exe  (takes 2-3 minutes).
python -m pip install numpy pandas matplotlib openpyxl pillow pyinstaller
python -m PyInstaller --onefile --windowed --name QB-Throw-Speed --add-data "data\throws.xlsx;data" --hidden-import PIL._tkinter_finder app.py
echo.
echo Done! Your app is dist\QB-Throw-Speed.exe
pause
