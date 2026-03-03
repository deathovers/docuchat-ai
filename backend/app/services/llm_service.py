from openai import OpenAI
from app.core.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

async def generate_answer(query: str, context_matches: list, history: list = None):
    context_text = ""
    sources = []
    
    for match in context_matches:
        meta = match.metadata
        context_text += f"\n\nSource: {meta['filename']} (Page {int(meta['page_number'])})\nContent: {meta['text']}"
        sources.append({"file": meta['filename'], "page": int(meta['page_number'])})
    
    system_prompt = (
        "You are a helpful AI assistant. Answer the user's question based ONLY on the provided context. "
        "If the answer is not in the context, say 'The answer was not found in the uploaded documents.' "
        "Always provide citations in your response referring to the source filename and page."
    )
    
    messages = [{"role": "system", "content": system_prompt}]
    if history:
        messages.extend(history)
    
    messages.append({"role": "user", "content": f"Context:\n{context_text}\n\nQuestion: {query}"})
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0
    )
    
    return response.choices[0].message.content, sources
