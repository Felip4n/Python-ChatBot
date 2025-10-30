# logic/actions.py
from logic.state_manager import set_state, clear_state, get_state

# --- Funções de API Falsas (para simular a lógica) ---

def calendar_api_check_availability(slot):
    """Função Falsa: Simula a verificação de disponibilidade."""
    print(f"[API CALENDÁRIO]: Verificando: {slot}")
    if "10:00" in slot or "09:00" in slot:
        return True  # Disponível
    return False # Ocupado

def calendar_api_book_slot(user_id, details):
    """Função Falsa: Simula o agendamento."""
    print(f"[API CALENDÁRIO]: Agendando para {user_id}: {details}")
    pass

# --- Funções de Ação do Bot ---

def get_saudacao(user_id):
    """Retorna a saudação inicial (seu menu)."""
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
    """Retorna a mensagem de erro/menu."""
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
    clear_state(user_id) # Limpa o estado
    return (
        "Certo, vou te encaminhar para um atendente humano 👨‍💼\n"
        "Por favor, aguarde um momento..."
    )

def finalizar_atendimento(user_id):
    clear_state(user_id) # Limpa o estado
    return "Tudo bem! Atendimento finalizado. 😊 Tenha um ótimo dia!"

def get_link_simulado(user_id):
    clear_state(user_id) # Limpa o estado
    return "Aqui está o link para o simulado teórico do Detran: https://www.detran.sp.gov.br/simulado"

# --- FLUXO DE AGENDAMENTO (O que você pediu) ---

def iniciar_agendamento(user_id: str, tipo_aula: str):
    """
    Ação 1: Inicia o fluxo e pergunta o nome.
    """
    # Salva o estado do usuário
    state = {"fluxo": "agendamento", "etapa": "aguardando_nome", "tipo_aula": tipo_aula}
    set_state(user_id, state)
    
    return f"Perfeito! Vamos marcar sua aula {tipo_aula}. Qual seu nome completo?"

def processar_nome_agendamento(user_id: str, nome_completo: str):
    """
    Ação 2: Recebe o nome, salva, e pergunta a data/hora.
    """
    state = get_state(user_id)
    state["nome"] = nome_completo
    state["etapa"] = "aguardando_data"
    set_state(user_id, state)
    
    return "Ótimo, " + nome_completo.split()[0] + "! Qual data e horário você gostaria de agendar?"

def processar_data_agendamento(user_id: str, data_hora: str):
    """
    Ação 3: Recebe a data/hora, verifica a API e agenda.
    """
    state = get_state(user_id)
    
    # Usamos as funções que você pediu (handle_scheduling_step)
    if calendar_api_check_availability(data_hora):
        # Salva a aula (aqui você usaria os dados do 'state' e 'data_hora')
        details = {
            "nome": state.get("nome"),
            "aula": state.get("tipo_aula"),
            "slot": data_hora
        }
        calendar_api_book_slot(user_id, details)
        
        # Limpa o estado e confirma
        clear_state(user_id)
        return "Aula agendada com sucesso!"
    else:
        # Não limpa o estado, pede para tentar de novo
        return "Esse horário não está disponível, quer tentar outro?"