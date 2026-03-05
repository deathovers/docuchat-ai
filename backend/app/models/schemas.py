from pydantic import BaseModel
from typing import List, Optional

class Source(BaseModel):
    file_name: str
    page_number: int

class ChatRequest(BaseModel):
    session_id: str
    query: str
    stream: bool = False

class ChatResponse(BaseModel):
    answer: str
    sources: List[Source]

class FileStatus(BaseModel):
    file_id: str
    name: str
    status: str

class UploadResponse(BaseModel):
    files: List[FileStatus]
