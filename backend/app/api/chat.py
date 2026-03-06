from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.services.rag_engine import query_documents
from pydantic import BaseModel

router = APIRouter()

class ChatRequest(BaseModel):
    session_id: str
    query: str

@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Endpoint to handle chat queries and return a streaming SSE response.
    """
    return StreamingResponse(
        query_documents(request.session_id, request.query),
        media_type="text/event-stream"
    )
