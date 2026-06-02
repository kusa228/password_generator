@echo off
title Генератор паролей
echo ========================================
echo    ЗАПУСК ГЕНЕРАТОРА ПАРОЛЕЙ
echo ========================================
echo.
echo Устанавливаю зависимости...
pip install -r requirements.txt
echo.
echo Запускаю сервер...
python main.py
pause