from typing import List, Dict
from database.vector_store import get_vector_store
from services.embedding_service import get_embedding_service
import logging

logger = logging.getLogger(__name__)


class TranslationService:
    def __init__(self):
        self.vector_store = get_vector_store()
        self.embedding_service = get_embedding_service()
    
    def add_translation_pair(
        self,
        source_language: str,
        target_language: str,
        sentence: str,
        translation: str
    ) -> None:
        """
        Store a translation pair in ChromaDB.
        
        Args:
            source_language: ISO 639-1 source language code
            target_language: ISO 639-1 target language code
            sentence: Source sentence
            translation: Target translation
        """
        # Generate embedding
        embedding = self.embedding_service.encode(sentence)
        
        # Generate unique ID
        import hashlib
        pair_id = hashlib.md5(f"{source_language}_{target_language}_{sentence}".encode()).hexdigest()[:16]
        
        # Store in ChromaDB
        self.vector_store.add_pair(
            pair_id=f"{source_language}_{target_language}_{pair_id}",
            sentence=sentence,
            embedding=embedding,
            metadata={
                "source_language": source_language,
                "target_language": target_language,
                "translation": translation
            }
        )
        
        logger.info(f"Added translation pair: {source_language}->{target_language}")
    
    def generate_translation_prompt(
        self,
        source_language: str,
        target_language: str,
        query_sentence: str
    ) -> str:
        """
        Generate a translation prompt with similar examples from RAG.
        
        Args:
            source_language: ISO 639-1 source language code
            target_language: ISO 639-1 target language code
            query_sentence: Sentence to translate
            
        Returns:
            Formatted prompt string with examples
        """
        # Generate embedding for query
        query_embedding = self.embedding_service.encode(query_sentence)
        
        # Search for similar pairs
        similar_pairs = self.vector_store.search_similar(
            query_embedding=query_embedding,
            source_language=source_language,
            target_language=target_language,
            n_results=4
        )
        
        # Format prompt
        prompt = self._format_prompt(
            source_language=source_language,
            target_language=target_language,
            query_sentence=query_sentence,
            examples=similar_pairs
        )
        
        return prompt
    
    def _format_prompt(
        self,
        source_language: str,
        target_language: str,
        query_sentence: str,
        examples: List[Dict]
    ) -> str:
        """Format the translation prompt with examples."""
        prompt_lines = [
            f"Translate the following sentence from {source_language} to {target_language}:",
            "",
            f'"{query_sentence}"',
            ""
        ]
        
        if examples:
            prompt_lines.append("Here are some similar translation examples:")
            prompt_lines.append("")
            
            for i, example in enumerate(examples, 1):
                prompt_lines.append(f"{i}. {example['source_language']}: \"{example['sentence']}\"")
                prompt_lines.append(f"   {example['target_language']}: \"{example['translation']}\"")
                prompt_lines.append("")
        
        return "\n".join(prompt_lines)


def get_translation_service() -> TranslationService:
    """Get translation service instance."""
    return TranslationService()
