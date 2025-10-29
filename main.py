from logic.actions import executar_acao

while True:
    msg = input("Cliente: ")
    resposta = executar_acao(msg, user_id="123")
    print(f"Bot: {resposta}\n")
    if "finalizado" in resposta.lower():
        break
