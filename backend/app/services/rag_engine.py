import logging
import json
import re
import asyncio
from typing import AsyncGenerator
from llama_index.core import StorageContext, load_index_from_storage
from app.services.vector_store import get_storage_path

logger = logging.getLogger(__name__)

def sanitize_session_id(session_id: str) -> str:
    """Strictly sanitize session_id to prevent directory traversal."""
    return re.sub(r'[^a-zA-Z0-9_-]', '', session_id)

async def query_documents(session_id: str, query: str) -> AsyncGenerator[str, None]:
    """
    Core RAG logic: Retrieves context and streams LLM response with citations.
    Offloads blocking I/O to a thread pool to keep the event loop responsive.
    """
    safe_session_id = sanitize_session_id(session_id)
    
    # SECURITY FIX: Ensure session_id is not empty after sanitization
    if not safe_session_id:
        logger.error(f"Invalid session_id attempt: '{session_id}'")
        yield f"data: {json.dumps({'type': 'error', 'content': 'Invalid session ID provided.'})}\n\n"
        return

    storage_dir = get_storage_path(safe_session_id)
    loop = asyncio.get_event_loop()
    
    try:
        # PERFORMANCE FIX: Offload blocking I/O to thread pool
        # This prevents the event loop from freezing during disk access
        storage_context = await loop.run_in_executor(
            None, lambda: StorageContext.from_defaults(persist_dir=storage_dir)
        )
        index = await loop.run_in_executor(
            None, lambda: load_index_from_storage(storage_context)
        )
        
        # Configure query engine with streaming enabled
        query_engine = index.as_query_engine(
            streaming=True,
            similarity_top_k=5
        )
        
        # Use asynchronous query
        response = await query_engine.aquery(query)
        
        # 1. Stream the text chunks
        async for token in response.async_response_gen:
            yield f"data: {json.dumps({'type': 'text', 'content': token})}\n\n"
            
        # 2. Extract and stream citations from source nodes
        citations = []
        for node in response.source_nodes:
            metadata = node.node.metadata
            citations.append({
                "filename": metadata.get("file_name", "Unknown"),
                "page": metadata.get("page_label", "N/A")
            })
        
        # Remove duplicates
        unique_citations = [dict(t) for t in {tuple(d.items()) for d in citations}]
        yield f"data: {json.dumps({'type': 'citations', 'content': unique_citations})}\n\n"
        yield "data: {\"type\": \"done\"}\n\n"

    except Exception as e:
        logger.error(f"Error in RAG engine for session {safe_session_id}: {str(e)}")
        yield f"data: {json.dumps({'type': 'error', 'content': 'An error occurred while processing your request.'})}\n\n"
