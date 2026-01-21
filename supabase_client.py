import random
import hmac
import hashlib
import secrets
import requests
from datetime import date

from config import SUPABASE_URL, SUPABASE_API_KEY

HEADERS = {
    "apikey": SUPABASE_API_KEY,
    "Authorization": f"Bearer {SUPABASE_API_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# ==================================================
# HTTP helpers
# ==================================================
def _url(path: str) -> str:
    return f"{SUPABASE_URL}/rest/v1/{path}"

def _get(path: str, params=None):
    return requests.get(_url(path), headers=HEADERS, params=params, timeout=20)

def _post(path: str, data: dict):
    return requests.post(_url(path), headers=HEADERS, json=data, timeout=20)

def _patch(path: str, data: dict):
    return requests.patch(_url(path), headers=HEADERS, json=data, timeout=20)

def _delete(path: str):
    return requests.delete(_url(path), headers=HEADERS, timeout=20)

# ==================================================
# Password hash (PBKDF2)
# format: pbkdf2$iters$salthex$hashhex
# ==================================================
def hash_password(password: str, iterations: int = 120_000) -> str:
    salt = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return f"pbkdf2${iterations}${salt.hex()}${dk.hex()}"

def verify_password(password: str, stored: str) -> bool:
    if not stored:
        return False
    # backward compatible: kalau dulu pernah plain text
    if not stored.startswith("pbkdf2$"):
        return hmac.compare_digest(password, stored)

    try:
        _, it_s, salt_hex, hash_hex = stored.split("$", 3)
        iterations = int(it_s)
        salt = bytes.fromhex(salt_hex)
        dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
        return hmac.compare_digest(dk.hex(), hash_hex)
    except Exception:
        return False

# ==================================================
# USERS
# ==================================================
def get_user_by_username(username: str):
    params = {"username": f"eq.{username}", "select": "id,username,password"}
    r = _get("users", params=params)
    return r.json() if r.ok else []

def insert_user(username: str, password_plain: str):
    # cek unik
    if get_user_by_username(username):
        return {"ok": False, "error": "USERNAME_TAKEN"}

    payload = {"username": username, "password": hash_password(password_plain)}
    r = _post("users", payload)
    if r.ok:
        return {"ok": True, "data": r.json()}
    return {"ok": False, "error": r.text}

def select_user(username: str, password_plain: str):
    rows = get_user_by_username(username)
    if not rows:
        return []
    u = rows[0]
    if verify_password(password_plain, u.get("password", "")):
        return [{"id": u["id"], "username": u["username"]}]
    return []

# ==================================================
# FOLDERS 
# ==================================================
def _folder_name_from_row(row: dict) -> str:
    return row.get("nama_folder") or row.get("nama") or ""

def get_folders(user_id: int):
    params = {"user_id": f"eq.{user_id}", "order": "id.desc"}
    r = _get("folders", params=params)
    return r.json() if r.ok else []

def insert_folder(user_id: int, nama_folder: str):
    r = _post("folders", {"user_id": user_id, "nama_folder": nama_folder})
    if r.ok:
        return {"ok": True, "data": r.json()}

    r2 = _post("folders", {"user_id": user_id, "nama": nama_folder})
    if r2.ok:
        return {"ok": True, "data": r2.json()}

    return {"ok": False, "error": r.text}

def update_folder(folder_id: int, nama_folder: str):
    r = _patch(f"folders?id=eq.{folder_id}", {"nama_folder": nama_folder})
    if r.ok:
        return {"ok": True, "data": r.json()}

    r2 = _patch(f"folders?id=eq.{folder_id}", {"nama": nama_folder})
    if r2.ok:
        return {"ok": True, "data": r2.json()}

    return {"ok": False, "error": r.text}

def delete_folder(folder_id: int):
    r = _delete(f"folders?id=eq.{folder_id}")
    return r.status_code

# ==================================================
# NOTES
# ==================================================
def get_notes(user_id: int, folder_id=None, hafal=None):
    """
    folder_id:
      - None => all
      - "NO_FOLDER" => folder_id IS NULL
      - int => folder_id = int
    hafal:
      - None => all
      - True/False => filter
    """
    params = {"user_id": f"eq.{user_id}", "order": "id.desc"}
    if folder_id == "NO_FOLDER":
        params["folder_id"] = "is.null"
    elif isinstance(folder_id, int):
        params["folder_id"] = f"eq.{folder_id}"

    if hafal is True:
        params["hafal"] = "eq.true"
    elif hafal is False:
        params["hafal"] = "eq.false"

    r = _get("notes", params=params)
    return r.json() if r.ok else []

def insert_note(data: dict):
    r = _post("notes", data)
    return r.json() if r.ok else []

def update_note(note_id: int, data: dict):
    r = _patch(f"notes?id=eq.{note_id}", data)
    return r.json() if r.ok else []

def delete_note(note_id: int):
    r = _delete(f"notes?id=eq.{note_id}")
    return r.status_code

def set_note_hafal(note_id: int, hafal: bool):
    r = _patch(f"notes?id=eq.{note_id}", {"hafal": bool(hafal)})
    return r.status_code

# ==================================================
# REMINDERS
# ==================================================
def get_reminders(user_id: int):
    params = {"user_id": f"eq.{user_id}", "order": "id.desc"}
    r = _get("reminders", params=params)
    return r.json() if r.ok else []

def insert_reminder(user_id: int, judul: str, tanggal_iso: str):
    # tanggal_iso: "YYYY-MM-DD"
    r = _post("reminders", {"user_id": user_id, "judul": judul, "tanggal": tanggal_iso, "selesai": False})
    return r.json() if r.ok else []

def update_reminder(reminder_id: int, data: dict):
    r = _patch(f"reminders?id=eq.{reminder_id}", data)
    return r.json() if r.ok else []

def delete_reminder(reminder_id: int):
    r = _delete(f"reminders?id=eq.{reminder_id}")
    return r.status_code

def set_reminder_done(reminder_id: int, selesai: bool):
    r = _patch(f"reminders?id=eq.{reminder_id}", {"selesai": bool(selesai)})
    return r.status_code

# ==================================================
# VOCABULARY
# ==================================================
def get_vocabularies(user_id: int, folder_id=None, sudah_hafal=None):
    params = {
        "user_id": f"eq.{user_id}",
        "order": "id.desc",
        "select": "id,folder_id,catatan,sudah_hafal"
    }

    if folder_id == "NO_FOLDER":
        params["folder_id"] = "is.null"
    elif isinstance(folder_id, int):
        params["folder_id"] = f"eq.{folder_id}"

    if sudah_hafal is True:
        params["sudah_hafal"] = "eq.true"
    elif sudah_hafal is False:
        params["sudah_hafal"] = "eq.false"

    r = _get("vocabulary", params=params)
    return r.json() if r.ok else []

def insert_vocabulary(user_id: int, catatan: str = "", folder_id=None):
    data = {"user_id": user_id, "catatan": catatan, "sudah_hafal": False, "folder_id": folder_id}
    r = _post("vocabulary", data)
    return r.json() if r.ok else []

def update_vocabulary(vocab_id: int, data: dict):
    r = _patch(f"vocabulary?id=eq.{vocab_id}", data)
    return r.json() if r.ok else []

def delete_vocabulary(vocab_id: int):
    r = _delete(f"vocabulary?id=eq.{vocab_id}")
    return r.status_code

def set_vocab_hafal(vocab_id: int, hafal: bool):
    r = _patch(f"vocabulary?id=eq.{vocab_id}", {"sudah_hafal": bool(hafal)})
    return r.status_code

# translations
def get_translations(vocabulary_id: int):
    params = {"vocabulary_id": f"eq.{vocabulary_id}", "order": "id.asc"}
    r = _get("vocabulary_translation", params=params)
    return r.json() if r.ok else []

def find_translation(vocabulary_id: int, bahasa: str):
    params = {"vocabulary_id": f"eq.{vocabulary_id}", "bahasa": f"eq.{bahasa}", "select": "id"}
    r = _get("vocabulary_translation", params=params)
    rows = r.json() if r.ok else []
    return rows[0]["id"] if rows else None

def insert_translation(data: dict):
    r = _post("vocabulary_translation", data)
    return r.json() if r.ok else []

def update_translation(translation_id: int, data: dict):
    r = _patch(f"vocabulary_translation?id=eq.{translation_id}", data)
    return r.json() if r.ok else []

def upsert_translation(vocabulary_id: int, bahasa: str, kosakata: str, pengucapan: str, arti: str):
    tid = find_translation(vocabulary_id, bahasa)
    payload = {"vocabulary_id": vocabulary_id, "bahasa": bahasa, "kosakata": kosakata, "pengucapan": pengucapan, "arti": arti}
    if tid is None:
        return insert_translation(payload)
    else:
        payload2 = {"kosakata": kosakata, "pengucapan": pengucapan, "arti": arti}
        return update_translation(tid, payload2)

def delete_translation(translation_id: int):
    r = _delete(f"vocabulary_translation?id=eq.{translation_id}")
    return r.status_code

# ==================================================
# QUIZ HELPERS
# ==================================================
LANGS = ["Indonesia", "Inggris", "Mandarin", "Jepang"]

def _all_vocab_with_translations(user_id: int, include_hafal: bool = False):
    params = {
        "user_id": f"eq.{user_id}",
        "select": "id,folder_id,catatan,sudah_hafal,vocabulary_translation(id,bahasa,kosakata,pengucapan,arti)",
        "order": "id.desc"
    }
    if not include_hafal:
        params["sudah_hafal"] = "eq.false"
    r = _get("vocabulary", params=params)
    return r.json() if r.ok else []

def get_quiz_vocab_questions(user_id: int, from_lang: str = "Acak", to_lang: str = "Acak", limit: int = 30, include_hafal: bool = False):
    """
    - Kalau from/to = Acak: pasangan bahasa akan random per soal.
    - Yang sudah hafal tidak ikut (default include_hafal=False)
    """
    items = _all_vocab_with_translations(user_id, include_hafal=include_hafal)
    questions = []

    for v in items:
        trans = v.get("vocabulary_translation") or []
        m = {t.get("bahasa"): t for t in trans if t.get("bahasa") and t.get("kosakata")}
        available = [b for b in LANGS if b in m]

        # butuh minimal 2 bahasa
        if len(available) < 2:
            continue

        # buat semua pasangan (a->b) untuk vocab itu
        for a in available:
            for b in available:
                if a == b:
                    continue
                if from_lang != "Acak" and a != from_lang:
                    continue
                if to_lang != "Acak" and b != to_lang:
                    continue

                q = (m[a].get("kosakata") or "").strip()
                ans = (m[b].get("kosakata") or "").strip()
                if q and ans:
                    questions.append({
                        "vocab_id": v["id"],
                        "from_lang": a,
                        "to_lang": b,
                        "prompt": q,
                        "answer": ans
                    })

    random.shuffle(questions)
    return questions[:limit]

def get_quiz_notes_questions(user_id: int, limit: int = 30, include_hafal: bool = False):
    notes = get_notes(user_id, folder_id=None, hafal=None)
    if not include_hafal:
        notes = [n for n in notes if not (n.get("hafal") is True)]
    random.shuffle(notes)
    return notes[:limit]

# ==================================================
# STATISTICS
# ==================================================
def count_notes(user_id: int) -> int:
    return len(get_notes(user_id))

def count_notes_hafal(user_id: int) -> int:
    return len(get_notes(user_id, hafal=True))

def count_folders(user_id: int) -> int:
    return len(get_folders(user_id))

def count_vocab(user_id: int) -> int:
    return len(get_vocabularies(user_id))

def count_vocab_hafal(user_id: int) -> int:
    return len(get_vocabularies(user_id, sudah_hafal=True))

def count_reminders(user_id: int) -> int:
    return len(get_reminders(user_id))

def count_reminders_done(user_id: int) -> int:
    data = get_reminders(user_id)
    return len([x for x in data if x.get("selesai") is True])

def count_vocab_translations(user_id: int) -> int:
    vocabs = get_vocabularies(user_id)
    total = 0
    for v in vocabs:
        total += len(get_translations(v["id"]))
    return total

def count_vocab_by_language(user_id: int):
    result = {b: 0 for b in LANGS}
    vocabs = get_vocabularies(user_id)
    for v in vocabs:
        for t in get_translations(v["id"]):
            b = t.get("bahasa")
            if b in result:
                result[b] += 1
    return result
