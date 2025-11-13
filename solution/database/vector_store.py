import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Optional
from functools import lru_cache


class VectorStore:
    def __init__(self, persist_directory: str):
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        self.collection = self.client.get_or_create_collection(
            name="translation_pairs",
            metadata={"hnsw:space": "cosine"}
        )
    
    def add_pair(
        self, 
        pair_id: str,
        sentence: str,
        embedding: List[float],
        metadata: Dict[str, str]
    ) -> None:
        """
        Add a translation pair to the vector store.
        
        Args:
            pair_id: Unique identifier for the pair
            sentence: Source sentence text
            embedding: Vector embedding of the sentence
            metadata: Additional metadata (languages, translation)
        """
        self.collection.add(
            ids=[pair_id],
            embeddings=[embedding],
            documents=[sentence],
            metadatas=[metadata]
        )
    
    def search_similar(
        self,
        query_embedding: List[float],
        source_language: str,
        target_language: str,
        n_results: int = 4
    ) -> List[Dict]:
        """
        Search for similar translation pairs.
        
        Args:
            query_embedding: Query vector embedding
            source_language: Source language filter
            target_language: Target language filter
            n_results: Number of results to return
            
        Returns:
            List of similar translation pairs with metadata
        """
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where={
                "$and": [
                    {"source_language": {"$eq": source_language}},
                    {"target_language": {"$eq": target_language}}
                ]
            }
        )
        
        # Format results
        similar_pairs = []
        if results['ids'][0]:
            for i in range(len(results['ids'][0])):
                similar_pairs.append({
                    'sentence': results['documents'][0][i],
                    'translation': results['metadatas'][0][i]['translation'],
                    'source_language': results['metadatas'][0][i]['source_language'],
                    'target_language': results['metadatas'][0][i]['target_language'],
                    'distance': results['distances'][0][i] if 'distances' in results else None
                })
        
        return similar_pairs


@lru_cache()
def get_vector_store() -> VectorStore:
    """Cached singleton for vector store."""
    from config import get_settings
    settings = get_settings()
    return VectorStore(settings.chroma_persist_dir)
