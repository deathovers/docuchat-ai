import re
import os
from fastapi import HTTPException

def sanitize_session_id(session_id: str) -> str:
    """
    Sanitizes the session_id to prevent directory traversal attacks.
    Only allows alphanumeric characters, hyphens, and underscores.
    """
    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID is required")
    
    # Remove any character that isn't alphanumeric, hyphen, or underscore
    sanitized = re.sub(r'[^a-zA-Z0-9_-]', '', session_id)
    
    if not sanitized:
        raise HTTPException(status_code=400, detail="Invalid Session ID format")
        
    return sanitized
