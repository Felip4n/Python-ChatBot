# logic/integrations.py
from typing import Dict, List, Optional, Any
import threading

# conjunto em memória com os slots reservados (strings)
_booked_slots = set()
_lock = threading.RLock()

# --- Google Sheets integration (configurável) ---
_use_sheets = False
_sheets_client = None      # cliente gspread (se fornecido)
_sheet_id: Optional[str] = None
_worksheet_name: str = "Sheet1"
# caching (opcional) to reduce API calls; set to None to disable caching
_cache: Optional[set] = None


def configure_google_sheets(
    client: Any = None,
    credentials_json_path: Optional[str] = None,
    credentials_json_dict: Optional[dict] = None,
    sheet_id: Optional[str] = None,
    worksheet_name: str = "Sheet1",
    use_cache: bool = True,
) -> None:
    """
    Configura o módulo para usar Google Sheets como backend.

    Você pode fornecer:
    - um client `gspread` já autenticado (param `client`), OR
    - um path para arquivo de credenciais do service account (param `credentials_json_path`),
        OR um dict com o JSON (param `credentials_json_dict`).

    Também forneça `sheet_id` (o ID do Google Sheet) e opcionalmente `worksheet_name`.

    Exemplo de autenticação EXTERNA (fora deste módulo):
        import gspread
        gc = gspread.service_account(filename='service_account.json')
        configure_google_sheets(client=gc, sheet_id='SHEET_ID')

    Observação: este módulo tentará importar `gspread` automaticamente se você fornecer
    `credentials_json_path` ou `credentials_json_dict`.
    """
    global _use_sheets, _sheets_client, _sheet_id, _worksheet_name, _cache

    # validate args
    if client is None and credentials_json_path is None and credentials_json_dict is None:
        raise ValueError("Forneça `client` ou `credentials_json_path`/`credentials_json_dict` para usar Google Sheets.")

    _worksheet_name = worksheet_name
    _sheet_id = sheet_id

    # try to use provided client
    if client is not None:
        _sheets_client = client
        _use_sheets = True
        _cache = set() if use_cache else None
        return

    # otherwise try to import gspread and create client
    try:
        import gspread
        from google.oauth2.service_account import Credentials  # type: ignore
    except Exception as e:
        raise RuntimeError(
            "Para usar Google Sheets você precisa instalar `gspread` e `google-auth`.\n"
            "Ex: `pip install gspread google-auth`.\n"
            f"Erro interno: {e}"
        )

    # build client
    if credentials_json_path:
        _sheets_client = gspread.service_account(filename=credentials_json_path)
    else:
        # credentials_json_dict provided
        creds = Credentials.from_service_account_info(credentials_json_dict)
        _sheets_client = gspread.Client(auth=creds)
        _sheets_client.session = gspread.client.Session()  #                                                            ensure session exists

    _use_sheets = True
    _cache = set() if use_cache else None

    # prime cache if requested and sheet_id provided
    if _cache is not None and _sheet_id:
        try:
            _cache.update(_read_all_slots_from_sheet())
        except Exception:
            # falhar silenciosamente ao inicializar cache; continuará sem cache
            _cache = None


def use_google_sheets() -> bool:
    """Retorna True se o módulo está configurado para usar Google Sheets."""
    return bool(_use_sheets and _sheets_client and _sheet_id)


# --- Helpers internos para Google Sheets ---


def _get_worksheet():
    """
    Retorna o objeto Worksheet do gspread.
    Lança se não estiver configurado.
    """
    if not use_google_sheets():
        raise RuntimeError("Google Sheets não está configurado. Use `configure_google_sheets(...)`.")
    ws = _sheets_client.open_by_key(_sheet_id).worksheet(_worksheet_name)
    return ws


def _read_all_slots_from_sheet() -> List[str]:
    """
    Lê todas as entradas da planilha. Espera que a planilha tenha uma coluna 'slot'
    (ou que cada linha contenha o valor do slot na primeira coluna).
    Retorna lista de strings.
    """
    ws = _get_worksheet()
    # ler todas as colunas/linhas
    rows = ws.get_all_values()  # lista de listas
    slots = []
    for row in rows:
        if not row:
            continue
        # assume slot na primeira coluna; ignore header se detectado (heurística)
        first = row[0].strip()
        if not first:
            continue
        # opcionalmente pular header: se 'slot' estiver no texto (case-insensitive)
        if first.lower() == "slot" or first.lower() == "horario":
            continue
        slots.append(first)
    return slots


def _append_slot_to_sheet(slot: str) -> None:
    """Anexa uma nova linha com o slot na planilha."""
    ws = _get_worksheet()
    # append_row usa API; pode ser lento
    ws.append_row([slot])


def _sheet_has_slot(slot: str) -> bool:
    """Checa se já existe o slot na planilha (varredura simples)."""
    # Se cache está ativo, use-o
    if _cache is not None:
        return slot in _cache
    # caso contrário, leia tudo (ineficiente mas simples)
    slots = _read_all_slots_from_sheet()
    return slot in slots


# --- API pública (mantendo compatibilidade com comportamento em memória) ---


def calendar_api_check_availability(slot: str) -> bool:
    """Simula checar disponibilidade de um horário (slot).

    Args:
        slot: string representando o horário (ex: "2025-11-05T15:00")

    Returns:
        True se disponível, False se ocupado.
    """
    if use_google_sheets():
        with _lock:
            try:
                available = not _sheet_has_slot(slot)
            except Exception:
                # Se houve erro com Sheets, fallback para memória
                available = slot not in _booked_slots
            return available

    # fallback in-memory
    with _lock:
        return slot not in _booked_slots


def calendar_api_book_slot(slot: str) -> Dict[str, str]:
    """Tenta reservar um slot.

    Se bem-sucedido, adiciona ao conjunto de reservas (ou ao Google Sheet) e retorna:
        {"status": "booked", "slot": slot}

    Se já estiver reservado, retorna:
        {"status": "conflict", "slot": slot}
    """
    if use_google_sheets():
        with _lock:
            try:
                if _sheet_has_slot(slot):
                    return {"status": "conflict", "slot": slot}
                # append na planilha
                _append_slot_to_sheet(slot)
                # atualizar cache se necessário
                if _cache is not None:
                    _cache.add(slot)
                return {"status": "booked", "slot": slot}
            except Exception as e:
                # Se algo falhar com Sheets, volte para fallback em memória
                # (não propaga o erro, apenas informa conflito/erro)
                # Você pode alterar esse comportamento para propagar o erro se preferir.
                return {"status": "error", "slot": slot, "reason": str(e)}

    # fallback in-memory
    with _lock:
        if slot in _booked_slots:
            return {"status": "conflict", "slot": slot}
        _booked_slots.add(slot)
        return {"status": "booked", "slot": slot}


def list_booked_slots() -> List[str]:
    """Retorna a lista de slots atualmente reservados (útil para testes)."""
    if use_google_sheets():
        with _lock:
            try:
                # preferir cache
                if _cache is not None:
                    return sorted(list(_cache))
                return sorted(_read_all_slots_from_sheet())
            except Exception:
                # fallback
                pass

    with _lock:
        return sorted(list(_booked_slots))


def reset_bookings() -> None:
    """Limpa todas as reservas (útil para testes).

    NOTE: se estiver usando Google Sheets, esta função **não** apagará a planilha automaticamente
    (por segurança). Em vez disso, ela:
    - Se usando Sheets: limpa apenas o cache local (se houver).
    - Se usando memória: limpa `_booked_slots`.

    Se quiser que eu adicione uma função que apague as linhas do Google Sheet, eu posso,
    mas isso exige cuidado (e permissão explícita).
    """
    with _lock:
        if use_google_sheets():
            # apenas limpar cache local; não apagar a planilha automaticamente
            if _cache is not None:
                _cache.clear()
        else:
            _booked_slots.clear()