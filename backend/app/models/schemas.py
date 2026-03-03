from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    session_id: str
    message: str

class Source(BaseModel):
    file: str
    page: int

class ChatResponse(BaseModel):
    answer: str
    sources: List[Source]
    timestamp: str

class FileInfo(BaseModel):
    file_id: str
    filename: str
    status: str
