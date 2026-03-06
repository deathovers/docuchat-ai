import json
from typing import AsyncGenerator
from llama_index.core import VectorStoreIndex
from llama_index.core.retrievers import VectorIndexRetriever
from app.services.vector_store import get_vector_store

SYSTEM_PROMPT = (
    "You are a helpful assistant that answers questions based ONLY on the provided context. "
    "If the answer is not present in the context, state: 'The answer was not found in the uploaded documents.' "
    "Do not use outside knowledge."
)

async def stream_chat(query: str, session_id: str) -> AsyncGenerator[str, None]:
    vector_store = get_vector_store(session_id)
    index = VectorStoreIndex.from_vector_store(vector_store)
    
    # Get citations first
    retriever = VectorIndexRetriever(index=index, similarity_top_k=3)
    nodes = retriever.retrieve(query)
    citations = [{"filename": n.metadata["file_name"], "page": n.metadata["page_label"]} for n in nodes]
    
    yield f"data: {json.dumps({'type': 'citations', 'content': citations})}\n\n"

    query_engine = index.as_query_engine(streaming=True, system_prompt=SYSTEM_PROMPT)
    response = query_engine.query(query)
    
    for text in response.response_gen:
        yield f"data: {json.dumps({'type': 'text', 'content': text})}\n\n"
    
    yield "data: {\"type\": \"done\"}\n\n"
