# logic/actions.py
from logic.nlu import reconhecer_mensagem

# Corrigir as funções

def sadacao_chat(user_id):
    return (
        "Olá! Eu sou seu assistente virtual da autoescola Brasília\n"
        "Como posso te ajudar hoje?\n\n"
        "1️⃣ - Marcar aula prática\n"
        "2️⃣ - Marcar aula teórica\n"
        "3️⃣ - Fazer simulado teórico (link do Detran)\n"
        "4️⃣ - Falar com um atendente humano\n"
        "5️⃣ - Finalizar atendimento"
    )


def fallback(user_id):
    return (
        "Desculpe, não entendi o que você quis dizer 😅\n"
        "Mas posso te ajudar com as seguintes opções:\n\n"
        "1️⃣ - Marcar aula prática\n"
        "2️⃣ - Marcar aula teórica\n"
        "3️⃣ - Fazer simulado teórico (link do Detran)\n"
        "4️⃣ - Falar com um atendente humano\n"
        "5️⃣ - Finalizar atendimento"
    )


def Falar_atendente(user_id):
    return (
        "Certo, vou te encaminhar para um atendente humano 👨‍💼\n"
        "Por favor, aguarde um momento..."
    )


def executar_acao(mensagem: str, user_id: str = None) -> str:
    intencao = reconhecer_mensagem(mensagem)

    if intencao == "saudacao":
        return sadacao_chat(user_id)

    elif intencao == "marcar_aula_pratica":
        return "Perfeito! Vamos marcar sua aula prática. Qual seu nome completo?"

    elif intencao == "marcar_aula_teorica":
        return "Certo! Vamos agendar sua aula teórica. Pode me dizer seu nome completo?"

    elif intencao == "fazer_simulado":
        return "Aqui está o link para o simulado teórico do Detran: https://www.detran.sp.gov.br/simulado"

    elif intencao == "falar_com_humano":
        return reconhecer_mensagem(user_id)

    elif intencao == "finalizar_atendimento":
        return "Tudo bem! Atendimento finalizado. 😊 Tenha um ótimo dia!"

    else:
        return fallback(user_id)
