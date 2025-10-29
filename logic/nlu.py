import re


def reconhecer_mensagem(mensagem: str) -> str:

    mensagem = mensagem.lower().strip()

    if re.search(r'\b(1|aula prática|pratica|marcar aula prática)\b', mensagem):
        return "marcar_aula_pratica"

    if re.search(r'\b(2|aula teórica|teorica|marcar aula teórica)\b', mensagem):
        return "marcar_aula_teorica"

    if re.search(r'\b(3|simulado|teste teórico|fazer simulado)\b', mensagem):
        return "fazer_simulado"

    if re.search(r'\b(4|atendente|humano|pessoa de verdade|falar com atendente)\b', mensagem):
        return "falar_com_humano"

    if re.search(r'\b(5|finalizar|encerrar|sair)\b', mensagem):
        return "finalizar_atendimento"

    # Saudações do chatbot
    return "saudacao"
