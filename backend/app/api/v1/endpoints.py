from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List
from app.models.schemas import UploadResponse, ChatRequest, ChatResponse
from app.services.ingestion import process_pdf, delete_file_vectors
from app.services.llm_service import get_chat_response

router = APIRouter()

# In-memory session history for MVP
session_histories = {}

@router.post("/documents/upload", response_model=UploadResponse)
async def upload_documents(
    session_id: str = Form(...),
    files: List[UploadFile] = File(...)
):
    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 files allowed per session.")
    
    results = []
    for file in files:
        if file.content_type != "application/pdf":
            continue
        content = await file.read()
        res = process_pdf(content, file.filename, session_id)
        results.append(res)
        
    return {"files": results}

@router.post("/chat/query", response_model=ChatResponse)
async def chat_query(request: ChatRequest):
    history = session_histories.get(request.session_id, [])
    
    response_data = get_chat_response(request.query, request.session_id, history)
    
    # Update history
    history.append({"role": "user", "content": request.query})
    history.append({"role": "assistant", "content": response_data["answer"]})
    session_histories[request.session_id] = history[-10:] # Keep last 10
    
    return response_data

@router.delete("/documents/{file_id}", status_code=204)
async def delete_document(file_id: str):
    delete_file_vectors(file_id)
    return None
