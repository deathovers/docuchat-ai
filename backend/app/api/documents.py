from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from app.services.document_service import process_pdf
from app.services.vector_service import upsert_chunks
from app.models.schemas import FileInfo
import uuid

router = APIRouter()

# In-memory store for session file tracking (MVP)
session_files = {}

@router.post("/upload", response_model=FileInfo)
async def upload_document(session_id: str = Form(...), file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    if session_id not in session_files:
        session_files[session_id] = []
    
    if len(session_files[session_id]) >= 10:
        raise HTTPException(status_code=400, detail="Maximum 10 files per session reached")

    content = await file.read()
    try:
        chunks = process_pdf(content, file.filename, session_id)
        await upsert_chunks(chunks)
        
        file_id = str(uuid.uuid4())
        session_files[session_id].append({"file_id": file_id, "filename": file.filename})
        
        return FileInfo(file_id=file_id, filename=file.filename, status="processed")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@router.get("/files")
async def list_files(session_id: str):
    return session_files.get(session_id, [])
