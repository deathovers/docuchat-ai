from fastapi import FastAPI
from app.api import chat

app = FastAPI(title="DocuChat AI API")

# Include API routers
app.include_router(chat.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "DocuChat AI API is running"}
