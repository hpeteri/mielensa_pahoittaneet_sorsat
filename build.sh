#! /bin/bash
pyinstaller --onefile "src/main.py"

mv "dist/main" "main"
