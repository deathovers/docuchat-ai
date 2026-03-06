import fitz  # PyMuPDF
from llama_index.core import Document
from llama_index.core.node_parser import TokenTextSplitter
from app.services.vector_store import get_vector_store
from llama_index.core import StorageContext, VectorStoreIndex

async def process_pdf(file_bytes: bytes, filename: str, session_id: str):
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    documents = []
    
    for page_num, page in enumerate(doc):
        text = page.get_text()
        documents.append(Document(
            text=text,
            metadata={
                "file_name": filename,
                "page_label": str(page_num + 1)
            }
        ))
    
    # Split into chunks
    parser = TokenTextSplitter(chunk_size=1000, chunk_overlap=150)
    nodes = parser.get_nodes_from_documents(documents)
    
    # Ingest into Pinecone
    vector_store = get_vector_store(session_id)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    VectorStoreIndex(nodes, storage_context=storage_context)
    
    return {"status": "success", "nodes": len(nodes)}
