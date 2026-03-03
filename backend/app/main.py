from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import documents, chat

app = FastAPI(title="DocuChat AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router, prefix="/v1", tags=["documents"])
app.include_router(chat.router, prefix="/v1", tags=["chat"])

@app.get("/")
async def root():
    return {"message": "DocuChat AI API is running"}
