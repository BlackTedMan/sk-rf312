@echo off
echo === СК РП — сборка сервера в exe ===

if not exist venv (
    echo Создаю виртуальное окружение...
    python -m venv venv
)

call venv\Scripts\activate.bat

echo Устанавливаю зависимости...
pip install -r requirements.txt
pip install pyinstaller

echo Собираю exe...
pyinstaller --noconfirm --onefile --console --name "SK-Server" ^
    --hidden-import=bcrypt ^
    --collect-submodules=uvicorn ^
    --collect-submodules=fastapi ^
    --collect-submodules=starlette ^
    main.py

echo.
echo Готово! Файл лежит в dist\SK-Server.exe
echo (база sk_app.db создастся рядом с exe при первом запуске)
pause
