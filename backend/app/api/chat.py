from fastapi import APIRouter, Body
msg_router = APIRouter()
from fastapi.responses import StreamingResponse
from app.services.rag_engine import query_documents

@msg_router.post("/chat")
async def chat_endpoint(
    session_id: str = Body(..., embed=True),
    query: str = Body(..., embed=True)
):
    """
    Streaming SSE endpoint for the chat interface.
    """
    return StreamingResponse(
        query_documents(session_id, query),
        media_type="text/event-stream"
    )
