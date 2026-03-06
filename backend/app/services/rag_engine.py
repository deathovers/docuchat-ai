import logging
import json
from typing import AsyncGenerator
from llama_index.core import StorageContext, load_index_from_storage
from app.services.vector_store import get_storage_path
from app.core.security import sanitize_session_id

logger = logging.getLogger(__name__)

async def query_documents(session_id: str, query: str) -> AsyncGenerator[str, None]:
    """
    Core RAG logic: Retrieves context and streams LLM response with citations.
    Addresses QA bugs:
    1. Uses async_response_gen for async iteration.
    2. Sanitizes session_id for security.
    3. Uses aquery for non-blocking I/O.
    """
    safe_session_id = sanitize_session_id(session_id)
    storage_dir = get_storage_path(safe_session_id)
    
    if not os.path.exists(storage_dir):
        yield f"data: {json.dumps({'type': 'error', 'content': 'No documents found for this session. Please upload files first.'})}\n\n"
        return

    try:
        # Load index for the specific session
        storage_context = StorageContext.from_defaults(persist_dir=storage_dir)
        index = load_index_from_storage(storage_context)
        
        # Configure query engine with streaming enabled
        query_engine = index.as_query_engine(
            streaming=True,
            similarity_top_k=5
        )
        
        # Use asynchronous query to prevent blocking the event loop
        response = await query_engine.aquery(query)
        
        # 1. Stream the text chunks using the correct async generator
        # Fix for TypeError: 'generator' object is not an async iterable
        async for token in response.async_response_gen:
            yield f"data: {json.dumps({'type': 'text', 'content': token})}\n\n"
            
        # 2. Extract citations from source nodes (metadata)
        # This replaces redundant retriever.retrieve() calls
        citations = []
        if hasattr(response, "source_nodes"):
            for node in response.source_nodes:
                metadata = node.node.metadata
                citations.append({
                    "filename": metadata.get("file_name", "Unknown"),
                    "page": metadata.get("page_label", "N/A")
                })
        
        # Deduplicate citations based on filename and page
        unique_citations = []
        seen = set()
        for c in citations:
            key = (c["filename"], c["page"])
            if key not in seen:
                unique_citations.append(c)
                seen.add(key)

        yield f"data: {json.dumps({'type': 'citations', 'content': unique_citations})}\n\n"
        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    except Exception as e:
        logger.exception(f"Critical error in RAG engine for session {safe_session_id}")
        yield f"data: {json.dumps({'type': 'error', 'content': 'An internal error occurred during retrieval.'})}\n\n"
