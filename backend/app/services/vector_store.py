from pinecone import Pinecone
from llama_index.vector_stores.pinecone import PineconeVectorStore
from app.core.config import settings

pc = Pinecone(api_key=settings.PINECONE_API_KEY)

def get_vector_store(namespace: str):
    pinecone_index = pc.Index(settings.PINECONE_INDEX_NAME)
    return PineconeVectorStore(pinecone_index=pinecone_index, namespace=namespace)
