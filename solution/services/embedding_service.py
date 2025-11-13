from sentence_transformers import SentenceTransformer
from typing import List, Union
import numpy as np
from functools import lru_cache


class EmbeddingService:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
    
    def encode(self, texts: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
        """
        Generate embeddings for input text(s).
        
        Args:
            texts: Single text string or list of strings
            
        Returns:
            Embedding vector(s) as list of floats
        """
        if isinstance(texts, str):
            embedding = self.model.encode([texts], normalize_embeddings=True)[0]
            return embedding.tolist()
        else:
            embeddings = self.model.encode(texts, normalize_embeddings=True)
            return [emb.tolist() for emb in embeddings]


@lru_cache()
def get_embedding_service() -> EmbeddingService:
    """Cached singleton for embedding service."""
    from config import get_settings
    settings = get_settings()
    return EmbeddingService(settings.embedding_model)
