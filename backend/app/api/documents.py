from fastapi import APIRouter, UploadFile, File, BackgroundTasks, Header
from app.services.ingestion import process_pdf
import uuid

router = APIRouter()

@router.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    x_session_id: str = Header(None)
):
    session_id = x_session_id or str(uuid.uuid4())
    content = await file.read()
    background_tasks.add_task(process_pdf, content, file.filename, session_id)
    
    return {"message": "Processing started", "session_id": session_id, "filename": file.filename}
