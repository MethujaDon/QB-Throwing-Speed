#!/bin/bash
# Run this on a Mac that has Python installed:   bash build_exe_mac.sh
# It makes  dist/QB-Throw-Speed.app  (takes 2-3 minutes).
python3 -m pip install numpy pandas matplotlib openpyxl pillow pyinstaller
python3 -m PyInstaller --windowed --name QB-Throw-Speed --add-data "data/throws.xlsx:data" --hidden-import PIL._tkinter_finder app.py
echo "Done! Your app is dist/QB-Throw-Speed.app"
