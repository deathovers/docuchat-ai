import json
import logging
from typing import AsyncGenerator
from llama_index.core import VectorStoreIndex
from app.services.vector_store import get_vector_store

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a helpful assistant that answers questions based ONLY on the provided context. "
    "If the answer is not present in the context, state: 'The answer was not found in the uploaded documents.' "
    "Do not use outside knowledge. Provide concise and accurate answers."
)

async def stream_chat(query: str, session_id: str) -> AsyncGenerator[str, None]:
    """
    Streams a RAG-based chat response for a given query and session.
    Uses Pinecone namespaces for session isolation.
    
    Fixes:
    - Replaced sync .query() with async .aquery() to prevent event loop blocking.
    - Removed redundant retriever.retrieve() call; citations are now extracted from the response object.
    - Added comprehensive try-except block for robust error handling during streaming.
    """
    try:
        # 1. Initialize Vector Store for the specific session (Namespace)
        # The session_id acts as the namespace to ensure data isolation.
        vector_store = get_vector_store(session_id)
        index = VectorStoreIndex.from_vector_store(vector_store)
        
        # 2. Initialize Query Engine with streaming enabled
        # We use similarity_top_k=5 as per TRD requirements.
        query_engine = index.as_query_engine(
            streaming=True, 
            similarity_top_k=5,
            system_prompt=SYSTEM_PROMPT
        )
        
        # 3. Perform the query asynchronously
        # This is non-blocking and allows the FastAPI event loop to handle other requests.
        response = await query_engine.aquery(query)

        # 4. Extract citations from the response object directly
        # This avoids the redundant retrieval step (calling retriever.retrieve separately),
        # reducing latency and API costs for embeddings.
        citations = [
            {
                "filename": n.node.metadata.get("file_name", "Unknown"),
                "page": n.node.metadata.get("page_label", "Unknown")
            }
            for n in response.source_nodes
        ]
        
        # Stream citations first so the UI can display sources immediately
        yield f"data: {json.dumps({'type': 'citations', 'content': citations})}\n\n"

        # 5. Stream the text response chunks
        # We iterate through the response generator provided by LlamaIndex
        for text in response.response_gen:
            yield f"data: {json.dumps({'type': 'text', 'content': text})}\n\n"
            
    except Exception as e:
        logger.error(f"Error in stream_chat for session {session_id}: {str(e)}", exc_info=True)
        # Stream a structured error message to the frontend
        yield f"data: {json.dumps({'type': 'error', 'content': 'An error occurred while processing your request. Please try again.'})}\n\n"
    
    finally:
        # Signal completion to the frontend to close the connection or update UI state
        yield "data: {\"type\": \"done\"}\n\n"
