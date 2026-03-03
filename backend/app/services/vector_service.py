from pinecone import Pinecone
from openai import OpenAI
from app.core.config import settings

pc = Pinecone(api_key=settings.PINECONE_API_KEY)
index = pc.Index(settings.PINECONE_INDEX)
client = OpenAI(api_key=settings.OPENAI_API_KEY)

async def get_embeddings(texts: list[str]):
    response = client.embeddings.create(
        input=texts,
        model="text-embedding-3-small"
    )
    return [d.embedding for d in response.data]

async def upsert_chunks(chunks: list[dict]):
    texts = [c["text"] for c in chunks]
    embeddings = await get_embeddings(texts)
    
    vectors = []
    for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
        vectors.append({
            "id": f"{chunk['metadata']['session_id']}_{chunk['metadata']['filename']}_{i}",
            "values": emb,
            "metadata": {
                **chunk['metadata'],
                "text": chunk['text']
            }
        })
    
    index.upsert(vectors=vectors)

async def query_vectors(query: str, session_id: str, top_k: int = 5):
    query_emb = (await get_embeddings([query]))[0]
    
    results = index.query(
        vector=query_emb,
        top_k=top_k,
        include_metadata=True,
        filter={"session_id": {"$eq": session_id}}
    )
    
    return results.matches

async def delete_session_vectors(session_id: str):
    index.delete(filter={"session_id": {"$eq": session_id}})
