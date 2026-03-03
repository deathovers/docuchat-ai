from fastapi import APIRouter, HTTPException
from app.models.schemas import ChatRequest, ChatResponse
from app.services.vector_service import query_vectors
from app.services.llm_service import generate_answer
from datetime import datetime

router = APIRouter()

# Simple in-memory history store
chat_history = {}

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # 1. Retrieve context from Pinecone with session isolation
        matches = await query_vectors(request.message, request.session_id)
        
        # 2. Get history for context
        history = chat_history.get(request.session_id, [])[-10:] # Last 10 messages
        
        # 3. Generate answer using LLM with context grounding
        answer, sources = await generate_answer(request.message, matches, history)
        
        # 4. Update history
        if request.session_id not in chat_history:
            chat_history[request.session_id] = []
        chat_history[request.session_id].append({"role": "user", "content": request.message})
        chat_history[request.session_id].append({"role": "assistant", "content": answer})
        
        return ChatResponse(
            answer=answer,
            sources=sources,
            timestamp=datetime.utcnow().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
