import os
from fastapi import FastAPI, Request, Response
import httpx

app = FastAPI()

VERIFY_TOKEN = os.getenv("WH_VERIFY_TOKEN", "verify123")
WH_TOKEN = os.getenv("WH_ACCESS_TOKEN", "")
PHONE_NUMBER_ID = os.getenv("WH_PHONE_NUMBER_ID", "")

# ذاكرة بسيطة مؤقتة
MEMORY = {}

async def send_whatsapp_text(to: str, text: str):
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }
    headers = {
        "Authorization": f"Bearer {WH_TOKEN}",
        "Content-Type": "application/json"
    }
    async with httpx.AsyncClient(timeout=20) as client:
        await client.post(url, headers=headers, json=payload)

@app.get("/webhook")
async def verify_webhook(request: Request):
    params = request.query_params
    if (
        params.get("hub.mode") == "subscribe"
        and params.get("hub.verify_token") == VERIFY_TOKEN
    ):
        return Response(
            content=params.get("hub.challenge"),
            media_type="text/plain"
        )
    return Response(status_code=403)

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()

    try:
        entry = data["entry"][0]
        change = entry["changes"][0]
        value = change["value"]
        message = value["messages"][0]

        user_number = message["from"]
        user_text = message["text"]["body"]

        # رد مبدئي (هنطوره بعدين)
        if "سعر" in user_text:
            reply = "سعر الطرحة X جنيه 👌 تحبي اللون إيه؟"
        else:
            reply = "أهلا 👋 تحبي تعرفي السعر ولا الخامة الأول؟"

        await send_whatsapp_text(user_number, reply)

    except Exception:
        pass

    return {"ok": True}
