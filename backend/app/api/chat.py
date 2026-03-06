from fastapi import APIRouter, Body
from sse_starlette.sse import EventSourceResponse
from app.services.rag_engine import stream_chat

router = APIRouter()

@router.post("/chat")
async def chat_endpoint(
    query: str = Body(..., embed=True),
    session_id: str = Body(..., embed=True)
):
    return EventSourceResponse(stream_chat(query, session_id))
