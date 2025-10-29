
user_status = {}

def get_state(user_id: str) -> dict:
    #Retorna o estado do usuário
    return user_status.get(user_id, {})

def set_state(user_id: str, state: dict):
    #Salva o estado do usuário
    user_status[user_id] = state

def clear_state(user_id: str):
    #Limpa o estado
    if user_id in user_status:
        del user_status[user_id]
