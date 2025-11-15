from typing import Dict, Any

_user_states: Dict[str, Dict[str, Any]] = {}

def set_state(user_id: str, state: Dict[str, Any]) -> None:
    _user_states[user_id] = state

def get_state(user_id: str) -> Dict[str, Any]:
    return _user_states.get(user_id, {"fluxo": "menu"})

def clear_state(user_id: str) -> None:
    if user_id in _user_states:
        del _user_states[user_id]