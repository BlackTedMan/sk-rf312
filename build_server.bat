@echo off
chcp 65001 >nul
echo === CK RP - sborka servera v exe ===

if not exist venv (
    echo Sozdayu virtualnoe okruzhenie...
    python -m venv venv
)

call venv\Scripts\activate.bat

echo Ustanavlivayu zavisimosti...
pip install -r requirements.txt
pip install pyinstaller

echo Sobirayu exe...
pyinstaller --noconfirm --onefile --console --name "SK-Server" ^
    --hidden-import=bcrypt ^
    --collect-submodules=uvicorn ^
    --collect-submodules=fastapi ^
    --collect-submodules=starlette ^
    main.py

echo.
echo Gotovo! Fayl lezhit v dist\SK-Server.exe
echo (baza sk_app.db sozdastsya ryadom s exe pri pervom zapuske)
pause
