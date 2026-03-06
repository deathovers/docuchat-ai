import os

def get_storage_path(session_id: str) -> str:
    """Returns the persistent storage path for a given session."""
    base_path = os.getenv("STORAGE_BASE_PATH", "./storage")
    return os.path.join(base_path, session_id)
