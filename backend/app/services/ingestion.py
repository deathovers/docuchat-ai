import fitz  # PyMuPDF
import uuid
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from openai import OpenAI
from app.core.config import settings
from app.db.pinecone_client import get_index

client = OpenAI(api_key=settings.OPENAI_API_KEY)
index = get_index()

def process_pdf(file_content: bytes, file_name: str, session_id: str):
    doc = fitz.open(stream=file_content, filetype="pdf")
    file_id = str(uuid.uuid4())
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    
    vectors = []
    
    for page_num, page in enumerate(doc):
        text = page.get_text()
        chunks = text_splitter.split_text(text)
        
        for i, chunk in enumerate(chunks):
            # Generate embedding
            embedding_res = client.embeddings.create(
                input=chunk,
                model=settings.EMBEDDING_MODEL
            )
            embedding = embedding_res.data[0].embedding
            
            vector_id = f"{file_id}_{page_num}_{i}"
            vectors.append({
                "id": vector_id,
                "values": embedding,
                "metadata": {
                    "text": chunk,
                    "file_id": file_id,
                    "file_name": file_name,
                    "page_number": page_num + 1,
                    "session_id": session_id
                }
            })
            
            # Batch upsert if needed, but for simplicity:
            if len(vectors) >= 100:
                index.upsert(vectors=vectors)
                vectors = []
                
    if vectors:
        index.upsert(vectors=vectors)
        
    return {"file_id": file_id, "name": file_name, "status": "processed"}

def delete_file_vectors(file_id: str):
    index.delete(filter={"file_id": {"$eq": file_id}})
