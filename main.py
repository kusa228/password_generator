from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
import secrets
import random
import uvicorn
import os
from database import init_db, save_password, get_recent_passwords

PASSWORD_LENGTH = 14


def make_first_letter_uppercase(password: str) -> str:
    for i, ch in enumerate(password):
        if ch.isalpha():
            return password[:i] + ch.upper() + password[i + 1:]
    return password


def generate_password(use_numbers: bool, use_special: bool, use_uppercase: bool, use_capital: bool) -> str:
    lower = 'abcdefghijklmnopqrstuvwxyz'
    numbers = '0123456789' if use_numbers else ''
    special = '!@#$%^&*()_+-=[]{}|;:,.<>?/~`' if use_special else ''
    upper = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' if use_uppercase else ''

    all_chars = lower + numbers + special + upper
    if not all_chars:
        all_chars = lower

    required = []
    if use_numbers and numbers:
        required.append(secrets.choice(numbers))
    if use_special and special:
        required.append(secrets.choice(special))
    if use_uppercase and upper:
        required.append(secrets.choice(upper))
    required.append(secrets.choice(lower))

    if PASSWORD_LENGTH < len(required):
        password_list = required[:PASSWORD_LENGTH]
    else:
        remaining = PASSWORD_LENGTH - len(required)
        password_list = required + [secrets.choice(all_chars) for _ in range(remaining)]

    rng = random.SystemRandom()
    rng.shuffle(password_list)

    password = ''.join(password_list)

    if use_capital:
        password = make_first_letter_uppercase(password)

    return password


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Запуск приложения: инициализация базы данных...")
    await init_db()
    print("✅ База данных готова")
    yield
    print("🛑 Завершение приложения")


app = FastAPI(title="Password Generator", lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/generate", response_class=HTMLResponse)
async def generate(
        request: Request,
        numbers: bool = Form(True),
        uppercase: bool = Form(True),
        special: bool = Form(True),
        capital: bool = Form(False)
):
    password = generate_password(numbers, special, uppercase, capital)
    await save_password(password, numbers, special, uppercase, capital)
    return templates.TemplateResponse("result.html", {"request": request, "password": password})


@app.get("/history", response_class=HTMLResponse)
async def history(request: Request):
    passwords = await get_recent_passwords(50)
    return templates.TemplateResponse("history.html", {"request": request, "passwords": passwords})


if __name__ == "__main__":
    import socket

    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
    except:
        local_ip = "127.0.0.1"

    print("\n" + "=" * 50)
    print("🔐 ГЕНЕРАТОР ПАРОЛЕЙ ЗАПУЩЕН")
    print("=" * 50)
    print(f"📱 Локальный доступ: http://127.0.0.1:8000")
    print(f"🌐 Доступ с телефона: http://{local_ip}:8000")
    print("=" * 50)
    print("⚠️  Для доступа с телефона:")
    print("   1. Телефон должен быть в той же Wi-Fi сети")
    print("   2. Введите IP-адрес выше в браузере телефона")
    print("   3. Если не работает, проверьте брандмауэр")
    print("=" * 50)
    print("\nНажмите CTRL+C для остановки сервера\n")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )