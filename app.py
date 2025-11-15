from fastapi import FastAPI, Request, Response
from logic.actions import executar_acao
from logic.integrations import configure_google_sheets
from dotenv import load_dotenv
import os
import requests

load_dotenv()

ULTRAMSG_INSTANCE_ID = os.getenv("ULTRAMSG_INSTANCE_ID")
ULTRAMSG_TOKEN = os.getenv("ULTRAMSG_TOKEN")

GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
CREDENTIALS_PATH = os.getenv("CREDENTIALS_PATH")

configure_google_sheets(
    credentials_json_path=CREDENTIALS_PATH,
    sheet_id=GOOGLE_SHEET_ID,
    worksheet_name="Agendamentos",
    use_cache=True,
)

app = FastAPI()

@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    data = await request.json()

    inner = data.get("data", {})
    incoming_message = inner.get("body")
    user_id = inner.get("from")

    if not incoming_message or not user_id:
        return Response(content="success", media_type="application/json")

    try:
        response_text = executar_acao(incoming_message, user_id)
    except Exception:
        response_text = "Erro interno."

    url = f"https://api.ultramsg.com/{ULTRAMSG_INSTANCE_ID}/messages/chat"
    payload = {
        "token": ULTRAMSG_TOKEN,
        "to": user_id,
        "body": response_text
    }

    requests.post(url, data=payload)

    return Response(content="success", media_type="application/json")

@app.get("/")
def home():
    return {"status": "ok"}
