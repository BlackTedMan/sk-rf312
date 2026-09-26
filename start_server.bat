@echo off
echo === СК РП — запуск сервера ===

if not exist venv (
    echo Первый запуск: создаю окружение и ставлю зависимости...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

echo.
echo Сервер запускается на http://localhost:8000
echo (не закрывайте это окно, пока сервер должен работать)
echo.
uvicorn main:app --host 0.0.0.0 --port 8000
pause
