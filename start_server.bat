@echo off
chcp 65001 >nul
echo === CK RP - zapusk servera ===

if not exist venv (
    echo Sozdayu virtualnoe okruzhenie...
    python -m venv venv
)

call venv\Scripts\activate.bat

echo Proveryayu zavisimosti...
pip install -r requirements.txt

echo.
echo Server zapuskaetsya na http://localhost:8000
echo (ne zakryvayte eto okno, poka server dolzhen rabotat)
echo.
uvicorn main:app --host 0.0.0.0 --port 8000
pause
