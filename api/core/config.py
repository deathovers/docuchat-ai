from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "DocuChat AI"
    OPENAI_API_KEY: str
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: str = ""
    COLLECTION_NAME: str = "docuchat_chunks"
    
    MAX_FILES_PER_SESSION: int = 10
    MAX_FILE_SIZE_MB: int = 25

    class Config:
        env_file = ".env"

settings = Settings()
