import hashlib
import json
from datetime import datetime
from pathlib import Path

USERS_FILE = Path("users_account.json")
HISTORY_FILE = Path("history_log.json")


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def load_list(path: Path) -> list[dict]:
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return data
        except Exception:
            return []
    return []


def save_list(path: Path, records: list[dict]) -> None:
    try:
        path.write_text(json.dumps(records, indent=2), encoding="utf-8")
    except Exception:
        pass


def create_account(users: list[dict], name: str, email: str, password: str) -> tuple[bool, str, dict | None]:
    clean_name = name.strip()
    clean_email = email.strip().lower()
    if not clean_name or "@" not in clean_email or len(password) < 4:
        return False, "Enter a valid name, email, and password (at least 4 characters).", None
    if any(u.get("email", "").lower() == clean_email for u in users):
        return False, "An account with this email already exists. Please log in.", None

    new_user = {
        "name": clean_name,
        "email": clean_email,
        "password_hash": hash_password(password),
    }
    users.append(new_user)
    save_list(USERS_FILE, users)
    return True, "Account created successfully.", {"name": clean_name, "email": clean_email}


def authenticate_user(users: list[dict], email: str, password: str) -> dict | None:
    clean_email = email.strip().lower()
    pwd_hash = hash_password(password)
    for u in users:
        if u.get("email", "").lower() == clean_email and u.get("password_hash") == pwd_hash:
            return {"name": u["name"], "email": u["email"]}
    return None


def add_history_entry(history: list[dict], user: dict | None, text: str, source: str, platform: str, verdict_data: dict) -> list[dict]:
    entry = {
        "user_email": user["email"] if user else "guest",
        "verdict": verdict_data["verdict"],
        "cls": verdict_data["cls"],
        "confidence": verdict_data["confidence"],
        "fake_prob": verdict_data["fake_prob"],
        "timestamp": datetime.now().strftime("%m/%d/%Y, %I:%M:%S %p"),
        "text": text[:240],
        "source": source or "Unspecified",
        "platform": platform or "Unspecified",
    }
    history.insert(0, entry)
    save_list(HISTORY_FILE, history)
    return history