from openai import OpenAI
from app.core.config import settings
from app.db.pinecone_client import get_index
from typing import List, Dict

client = OpenAI(api_key=settings.OPENAI_API_KEY)
index = get_index()

SYSTEM_PROMPT = """You are a helpful assistant. Answer only based on the provided context. 
If the answer is not in the context, say 'The answer was not found in the uploaded documents.' 
Always cite the source file and page number in your response.

Context:
{context}
"""

def get_chat_response(query: str, session_id: str, history: List[Dict] = []):
    # 1. Embed Query
    embedding_res = client.embeddings.create(
        input=query,
        model=settings.EMBEDDING_MODEL
    )
    query_vector = embedding_res.data[0].embedding
    
    # 2. Retrieve Context
    results = index.query(
        vector=query_vector,
        top_k=5,
        include_metadata=True,
        filter={"session_id": {"$eq": session_id}}
    )
    
    context_parts = []
    sources = []
    seen_sources = set()
    
    for match in results['matches']:
        meta = match['metadata']
        context_parts.append(f"Source: {meta['file_name']} (Page {meta['page_number']})\nContent: {meta['text']}")
        
        source_key = f"{meta['file_name']}_{meta['page_number']}"
        if source_key not in seen_sources:
            sources.append({"file_name": meta['file_name'], "page_number": int(meta['page_number'])})
            seen_sources.add(source_key)
            
    context_str = "\n\n---\n\n".join(context_parts)
    
    # 3. Generate Answer
    messages = [{"role": "system", "content": SYSTEM_PROMPT.format(context=context_str)}]
    # Add history (last 5 exchanges)
    messages.extend(history[-10:])
    messages.append({"role": "user", "content": query})
    
    response = client.chat.completions.create(
        model=settings.LLM_MODEL,
        messages=messages,
        temperature=0
    )
    
    answer = response.choices[0].message.content
    
    # Filter sources to only those actually mentioned in the answer if possible, 
    # but for MVP we return all retrieved sources or rely on LLM to cite.
    # The prompt instructs the LLM to cite.
    
    return {
        "answer": answer,
        "sources": sources
    }
