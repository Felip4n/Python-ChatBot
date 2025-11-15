from logic.actions import executar_acao
from logic.integrations import configure_google_sheets, use_google_sheets

GOOGLE_SHEET_ID = "SEU_SHEET_ID_AQUI"
CREDENTIALS_PATH = "service_account.json"

try:
    configure_google_sheets(
        credentials_json_path=CREDENTIALS_PATH,
        sheet_id=GOOGLE_SHEET_ID,
        worksheet_name="Agendamentos",
        use_cache=True,
    )
    status_sheets = "✅Google Sheets configurado com sucesso! As reservas serão salvas lá."
except Exception as e:
    status_sheets = f"Aviso: Não foi possível configurar o Google Sheets: {e}"
    status_sheets += "\nO chatbot continuará no modo de simulação em memória (padrão)."

USER_ID = "123"

print(f"\n--- Chatbot Autoescola Brasília (User: {USER_ID}) ---\n")
print(status_sheets)
print("-" * 50 + "\n")

resposta_inicial = executar_acao("ola", USER_ID)
print(f"Bot: {resposta_inicial}\n")


while True:
    try:
        msg = input("Cliente: ")
        if msg.lower() in ["sair", "quit"]:
            print("\nAtendimento finalizado manualmente.")
            break
        
        resposta = executar_acao(msg, USER_ID)
        print(f"Bot: {resposta}\n")
        
        if "finalizado" in resposta.lower():
            break
            
    except EOFError:
        break
    except KeyboardInterrupt:
        print("\nAtendimento finalizado manualmente.")
        break