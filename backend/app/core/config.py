from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENAI_API_KEY: str
    PINECONE_API_KEY: str
    PINECONE_INDEX: str = "docuchat"
    
    class Config:
        env_file = ".env"

settings = Settings()
