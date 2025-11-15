from typing import Dict, Any, Tuple
import unicodedata
import re

_menu_options = {
    "1": "marcar_aula_pratica",
    "pratica": "marcar_aula_pratica",
    "2": "marcar_aula_teorica",
    "teorica": "marcar_aula_teorica",
    "3": "link_simulado",
    "simulado": "link_simulado",
    "4": "falar_com_atendente",
    "atendente": "falar_com_atendente",
    "5": "finalizar_atendimento",
    "finalizar": "finalizar_atendimento",
    "cancelar": "finalizar_atendimento",
}

_saudacoes = {"ola", "olá", "oi", "oie", "menu"}

def _normalize(text: str) -> str:
    t = text.lower().strip()
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode("ascii")
    t = re.sub(r"[^\w\s]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t

def recognize_intent(message: str, state: Dict[str, Any]) -> Tuple[str, str]:
    text = _normalize(message)
    if not text:
        return "fallback", ""
    words = text.split()

    if state and state.get("fluxo") == "agendamento":
        etapa = state.get("etapa")
        if etapa == "aguardando_nome":
            return "processar_nome_agendamento", message.strip()
        if etapa == "aguardando_data":
            return "processar_data_agendamento", message.strip()

    if text in _saudacoes:
        return "saudacao", ""
    if len(words) == 1 and words[0] in _saudacoes:
        return "saudacao", ""

    for key, intent in _menu_options.items():
        if text == key:
            return intent, ""
        if len(words) == 1 and words[0] == key:
            return intent, ""

    return "fallback", ""
