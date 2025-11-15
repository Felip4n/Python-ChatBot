from typing import Dict, List, Optional, Any
import threading

_booked_slots = set()
_lock = threading.RLock()

_use_sheets = False
_sheets_client = None
_sheet_id: Optional[str] = None
_worksheet_name: str = "Sheet1"
_cache: Optional[set] = None


def configure_google_sheets(
    client: Any = None,
    credentials_json_path: Optional[str] = None,
    credentials_json_dict: Optional[dict] = None,
    sheet_id: Optional[str] = None,
    worksheet_name: str = "Sheet1",
    use_cache: bool = True,
) -> None:
    global _use_sheets, _sheets_client, _sheet_id, _worksheet_name, _cache

    if client is None and credentials_json_path is None and credentials_json_dict is None:
        raise ValueError("Forneça `client` ou `credentials_json_path`/`credentials_json_dict` para usar Google Sheets.")

    _worksheet_name = worksheet_name
    _sheet_id = sheet_id

    if client is not None:
        _sheets_client = client
        _use_sheets = True
        _cache = set() if use_cache else None
        return

    try:
        import gspread
        from google.oauth2.service_account import Credentials
    except Exception as e:
        raise RuntimeError(
            "Para usar Google Sheets você precisa instalar `gspread` e `google-auth`.\n"
            "Ex: `pip install gspread google-auth`.\n"
            f"Erro interno: {e}"
        )

    if credentials_json_path:
        _sheets_client = gspread.service_account(filename=credentials_json_path)
    else:
        creds = Credentials.from_service_account_info(credentials_json_dict)
        _sheets_client = gspread.Client(auth=creds)
        _sheets_client.session = gspread.client.Session()

    _use_sheets = True
    _cache = set() if use_cache else None
    if _cache is not None and _sheet_id:
        try:
            _cache.update(_read_all_slots_from_sheet())
        except Exception:
            _cache = None


def use_google_sheets() -> bool:
    return bool(_use_sheets and _sheets_client and _sheet_id)


def _get_worksheet():
    if not use_google_sheets():
        raise RuntimeError("Google Sheets não está configurado. Use `configure_google_sheets(...)`.")
    ws = _sheets_client.open_by_key(_sheet_id).worksheet(_worksheet_name)
    return ws


def _read_all_slots_from_sheet() -> List[str]:
    ws = _get_worksheet()
    rows = ws.get_all_values()
    slots = []
    for row in rows:
        if not row:
            continue
        first = row[2].strip() if len(row) > 2 else ""
        if not first:
            continue
        if first.lower() == "slot" or first.lower() == "horario":
            continue
        slots.append(first)
    return slots


def _append_slot_to_sheet(info: dict) -> None:
    ws = _get_worksheet()
    ws.append_row([info["nome"], info["tipo"], info["slot"], info["user_id"]])


def _sheet_has_slot(slot: str) -> bool:
    if _cache is not None:
        return slot in _cache
    slots = _read_all_slots_from_sheet()
    return slot in slots


def calendar_api_check_availability(slot: str) -> bool:
    if use_google_sheets():
        with _lock:
            try:
                available = not _sheet_has_slot(slot)
            except Exception:
                available = slot not in _booked_slots
            return available
    with _lock:
        return slot not in _booked_slots


def calendar_api_book_slot(info: dict) -> Dict[str, str]:
    slot = info["slot"]

    if use_google_sheets():
        with _lock:
            try:
                if _sheet_has_slot(slot):
                    return {"status": "conflict", "slot": slot}

                _append_slot_to_sheet(info)

                if _cache is not None:
                    _cache.add(slot)

                return {"status": "booked", "slot": slot}

            except Exception as e:
                return {"status": "error", "slot": slot, "reason": str(e)}

    with _lock:
        if slot in _booked_slots:
            return {"status": "conflict", "slot": slot}
        _booked_slots.add(slot)
        return {"status": "booked", "slot": slot}


def list_booked_slots() -> List[str]:
    if use_google_sheets():
        with _lock:
            try:
                if _cache is not None:
                    return sorted(list(_cache))
                return sorted(_read_all_slots_from_sheet())
            except Exception:
                pass

    with _lock:
        return sorted(list(_booked_slots))


def reset_bookings() -> None:
    with _lock:
        if use_google_sheets():
            if _cache is not None:
                _cache.clear()
        else:
            _booked_slots.clear()
