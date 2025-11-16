from fastapi import FastAPI, Request
import requests
from logic.actions import executar_acao
from logic.integrations import configure_google_sheets

ULTRA_INSTANCE = "SEU_INSTANCE"      
ULTRA_TOKEN = "SEU_TOKEN"             


GOOGLE_SHEET_ID = "SEU_SHEET_ID_AQUI"
CREDENTIALS_PATH = "service_account.json"

try:
    configure_google_sheets(
        credentials_json_path=CREDENTIALS_PATH,
        sheet_id=GOOGLE_SHEET_ID,
        worksheet_name="Agendamentos",
        use_cache=True,
    )
    print("Google Sheets configurado com sucesso!")
except Exception as e:
    print("Erro ao configurar Sheets:", e)

app = FastAPI()


def ultramsg_send(to, msg):
    """Enviar mensagem pelo UltraMsg."""
    url = f"https://api.ultramsg.com/{ULTRA_INSTANCE}/messages/chat"
    payload = {"token": ULTRA_TOKEN, "to": to, "body": msg}
    requests.post(url, data=payload)


@app.post("/webhook")
async def receive_message(request: Request):
    data = await request.json()

    sender = data.get("from")
    message = data.get("body", "")

    if not sender:
        return {"status": "ignored"}

    # Seu fluxo de chatbot
    resposta = executar_acao(message, sender)

    # Responder via UltraMsg
    ultramsg_send(sender, resposta)

    return {"status": "success", "msg": resposta}
