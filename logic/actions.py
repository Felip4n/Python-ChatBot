from typing import Dict, Any
from logic.state_manager import set_state, clear_state, get_state
from logic.nlu import recognize_intent
from logic.integrations import calendar_api_check_availability, calendar_api_book_slot

def get_saudacao(user_id):
    state = {"fluxo": "menu", "etapa": "aguardando_opcao", "tipo_aula": None}
    set_state(user_id, state)
    return (
        "Olá! Eu sou seu assistente virtual da autoescola Brasília\n"
        "Como posso te ajudar hoje?\n\n"
        "1️⃣ - Marcar aula prática\n"
        "2️⃣ - Marcar aula teórica\n"
        "3️⃣ - Fazer simulado teórico (link do Detran)\n"
        "4️⃣ - Falar com um atendente humano\n"
        "5️⃣ - Finalizar atendimento"
    )

def get_fallback(user_id):
    return (
        "Desculpe, não entendi o que você quis dizer 😅\n"
        "Mas posso te ajudar com as seguintes opções:\n\n"
        "1️⃣ - Marcar aula prática\n"
        "2️⃣ - Marcar aula teórica\n"
        "3️⃣ - Fazer simulado teórico (link do Detran)\n"
        "4️⃣ - Falar com um atendente humano\n"
        "5️⃣ - Finalizar atendimento"
    )

def falar_com_atendente(user_id):
    clear_state(user_id)
    return "Certo, vou te encaminhar para um atendente humano 👨‍💼"

def finalizar_atendimento(user_id):
    clear_state(user_id)
    return "Tudo bem! Atendimento finalizado."

def get_link_simulado(user_id):
    clear_state(user_id)
    return "Aqui está o link para o simulado: https://www.detran.sp.gov.br/simulado"

def iniciar_agendamento(user_id: str, tipo_aula: str):
    state = {"fluxo": "agendamento", "etapa": "aguardando_nome", "tipo_aula": tipo_aula}
    set_state(user_id, state)
    return f"Perfeito! Vamos marcar sua aula {tipo_aula}. Qual seu nome completo?"

def processar_nome_agendamento(user_id: str, nome_completo: str):
    state = get_state(user_id)
    state["nome"] = nome_completo.strip()
    state["etapa"] = "aguardando_data"
    set_state(user_id, state)
    primeiro_nome = nome_completo.strip().split()[0]
    return f"Ótimo, {primeiro_nome}! Qual data e horário (ex: YYYY-MM-DDTHH:MM) você gostaria de agendar?"

def processar_data_agendamento(user_id: str, data_hora: str):
    state = get_state(user_id)
    slot = data_hora.strip()

    if calendar_api_check_availability(slot):
        result = calendar_api_book_slot({
            "nome": state.get("nome"),
            "tipo": state.get("tipo_aula"),
            "slot": slot,
            "user_id": user_id
        })

        if result["status"] == "booked":
            clear_state(user_id)
            return f"Aula agendada com sucesso para {slot}!"

        elif result["status"] == "conflict":
            return f"O horário {slot} não está disponível. Tente outro."

        else:
            return "Ocorreu um erro ao tentar agendar."

    else:
        return f"O horário {slot} não está disponível. Tente outro."

def executar_acao(message: str, user_id: str) -> str:
    state = get_state(user_id)

    intent, extra_data = recognize_intent(message, state)

    if intent == "marcar_aula_pratica":
        return iniciar_agendamento(user_id, "prática")

    elif intent == "marcar_aula_teorica":
        return iniciar_agendamento(user_id, "teórica")

    elif intent == "link_simulado":
        return get_link_simulado(user_id)

    elif intent == "falar_com_atendente":
        return falar_com_atendente(user_id)

    elif intent == "finalizar_atendimento":
        return finalizar_atendimento(user_id)

    elif intent == "saudacao":
        return get_saudacao(user_id)

    elif intent == "processar_nome_agendamento":
        return processar_nome_agendamento(user_id, extra_data)

    elif intent == "processar_data_agendamento":
        return processar_data_agendamento(user_id, extra_data)

    elif intent == "fallback":
        return get_fallback(user_id)

    return get_fallback(user_id)
