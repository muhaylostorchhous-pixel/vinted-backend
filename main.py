from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

app = FastAPI(title="Vinted & Resell Tools API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- МОДЕЛИ ДАННЫХ ---
class ManualPaymentRequest(BaseModel):
    service_name: str     # Например: "SMS Number Vinted" или "Legit Check"
    amount: str           # Например: "$12" или "500 UAH"
    user_contact: str     # Telegram / Email пользователя для связи
    receipt_info: str     # Номер транзакции, имя отправителя или ссылка на чек

class OfferRequest(BaseModel):
    vinted_url: str
    offer_price: float
    refresh_token: str

class SMSRequest(BaseModel):
    country: str
    service: str = "vinted"


# --- 1. ПРИЁМ ЗАЯВКИ С ОПЛАТОЙ ПО РЕКВИЗИТАМ ---
@app.post("/api/pay/manual-confirm")
def manual_payment_confirm(data: ManualPaymentRequest):
    # Здесь бэкенд фиксирует заявку
    return {
        "status": "success",
        "message": "Заявка принята! Ожидайте подтверждения перевода (обычно 2–5 минут)."
    }


# --- 2. ЭНДПОИНТЫ VINTED И SMS ---
@app.post("/api/vinted/send-offer")
def send_vinted_offer(data: OfferRequest):
    try:
        item_id = data.vinted_url.split("/items/")[1].split("-")[0]
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Authorization": f"Bearer {data.refresh_token}",
            "Content-Type": "application/json"
        }
        payload = {"price": str(data.offer_price), "currency": "EUR"}
        vinted_api_url = f"https://www.vinted.com/api/v2/items/{item_id}/offers"
        response = requests.post(vinted_api_url, json=payload, headers=headers)
        
        if response.status_code in [200, 201]:
            return {"status": "success", "message": f"Оффер €{data.offer_price} успешно отправлен!"}
        else:
            return {"status": "error", "message": f"Ошибка Vinted ({response.status_code}): {response.text}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка ссылки: {str(e)}")

@app.post("/api/sms/get-number")
def get_sms_number(data: SMSRequest):
    return {
        "status": "success",
        "phone_number": "+44 7700 900077",
        "order_id": "8839201",
        "price_usd": 12.00,
        "country": data.country
    }

@app.get("/")
def root():
    return {"status": "online", "message": "Vinted Automation API Server is Running"}
