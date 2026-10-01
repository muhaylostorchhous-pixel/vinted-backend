from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

app = FastAPI(title="Vinted & Resell Tools API")

# Разрешаем запросы с твоего сайта Vercel (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- МОДЕЛИ ДАННЫХ ---
class OfferRequest(BaseModel):
    vinted_url: str
    offer_price: float
    refresh_token: str

class SMSRequest(BaseModel):
    country: str
    service: str = "vinted"


# --- 1. ЭНДПОИНТ: ОТПРАВКА ОФФЕРА НА VINTED ---
@app.post("/api/vinted/send-offer")
def send_vinted_offer(data: OfferRequest):
    try:
        # 1. Извлекаем ID товара из ссылки Vinted
        # Пример ссылки: https://www.vinted.com/items/123456789-jacket
        item_id = data.vinted_url.split("/items/")[1].split("-")[0]
        
        # 2. Формируем заголовки с Refresh Token пользователя
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Authorization": f"Bearer {data.refresh_token}",
            "Content-Type": "application/json"
        }
        
        # 3. Payload для Vinted API
        payload = {
            "price": str(data.offer_price),
            "currency": "EUR"
        }
        
        # 4. Отправляем оффер на Vinted (Замените URL при необходимости под нужный регион)
        vinted_api_url = f"https://www.vinted.com/api/v2/items/{item_id}/offers"
        response = requests.post(vinted_api_url, json=payload, headers=headers)
        
        if response.status_code in [200, 201]:
            return {"status": "success", "message": f"Оффер €{data.offer_price} успешно отправлен!"}
        else:
            return {
                "status": "error", 
                "message": f"Ошибка Vinted ({response.status_code}): {response.text}"
            }
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Некорректная ссылка или ошибка: {str(e)}")


# --- 2. ЭНДПОИНТ: ПОКУПКА СМС-НОМЕРА ---
@app.post("/api/sms/get-number")
def get_sms_number(data: SMSRequest):
    # Здесь подключается API ключ от SMS-Activate или 5SIM
    # Для теста возвращаем заглушку с номером
    return {
        "status": "success",
        "phone_number": "+48 791 234 567",
        "order_id": "987654321",
        "country": data.country
    }

@app.get("/")
def root():
    return {"status": "online", "message": "Vinted Automation API Server is Running"}