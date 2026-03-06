import os
from app.core.security import sanitize_session_id

STORAGE_BASE_DIR = os.getenv("STORAGE_BASE_DIR", "./storage")

def get_storage_path(session_id: str) -> str:
    """
    Returns the sanitized absolute path for a session's vector store.
    """
    safe_id = sanitize_session_id(session_id)
    # os.path.join with a sanitized base and sanitized ID is safe
    path = os.path.join(os.path.abspath(STORAGE_BASE_DIR), safe_id)
    return path

def ensure_storage_exists(session_id: str):
    path = get_storage_path(session_id)
    os.makedirs(path, exist_ok=True)
    return path
