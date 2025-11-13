from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    chroma_persist_dir: str = "./chroma_data"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    port: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
