from typing import Any, Dict
import threading

# Dicionário global de estados dos usuários
user_status: Dict[str, Dict[str, Any]] = {}
_lock = threading.RLock()


def get_state(user_id: str) -> Dict[str, Any]:
    """Retorna o estado atual do usuário.

    Se o usuário ainda não existir, retorna um estado padrão.
    """
    with _lock:
        return user_status.get(user_id, {"step": "start", "data": {}})


def set_state(user_id: str, state: Dict[str, Any]) -> None:
    """Define o estado completo do usuário."""
    with _lock:
        user_status[user_id] = state


def clear_state(user_id: str) -> None:
    """Remove o estado do usuário (por exemplo, ao encerrar o fluxo)."""
    with _lock:
        if user_id in user_status:
            del user_status[user_id]


def set_step(user_id: str, step: str) -> None:
    """Define apenas a etapa atual do fluxo do usuário."""
    with _lock:
        state = get_state(user_id)
        state["step"] = step
        user_status[user_id] = state


def update_data(user_id: str, key: str, value: Any) -> None:
    """Atualiza um campo dentro de 'data' do usuário."""
    with _lock:
        state = get_state(user_id)
        if "data" not in state:
            state["data"] = {}
        state["data"][key] = value
        user_status[user_id] = state


def example_usage() -> None:
    """Exemplo simples de uso."""
    user = "user_123"

    print("Inicial:", get_state(user))
    set_step(user, "asking_date")
    update_data(user, "slot", "2025-11-05T15:00")
    print("Atualizado:", get_state(user))
    clear_state(user)
    print("Após limpar:", get_state(user))


if __name__ == "__main__":
    example_usage()
