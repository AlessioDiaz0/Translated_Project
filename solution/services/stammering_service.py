import re
from typing import List, Tuple
from collections import Counter


class StammeringDetector:
    """
    Detects non-natural repetitions (stammering) in translated text.
    
    Stammering is identified when:
    - Words or phrases repeat consecutively in the translation
    - The repetition doesn't appear naturally in the source
    - Character-level elongations occur excessively
    """
    
    def __init__(self, min_repetitions: int = 3, max_ngram_size: int = 5):
        self.min_repetitions = min_repetitions
        self.max_ngram_size = max_ngram_size
    
    def detect(self, source_sentence: str, translated_sentence: str) -> bool:
        """
        Detect stammering in a translation.
        
        Returns: True if stammering is detected, False otherwise
        """
        # Check for character-level elongation (excessive repeated characters)
        if self._has_excessive_elongation(translated_sentence, source_sentence):
            return True
        
        # Check for word/phrase repetitions
        if self._has_phrase_repetition(translated_sentence, source_sentence):
            return True
        
        return False
    
    def _has_excessive_elongation(self, translated: str, source: str) -> bool:
        """
        Detect excessive character repetition (e.g., 'soooooo').
        Only flag if the elongation in translation is significantly more than source.
        """
        # Find all sequences of repeated characters (3+ times) with their full matches
        pattern = r'(.)\1{2,}'
        
        translated_matches = re.finditer(pattern, translated.lower())
        source_matches = re.finditer(pattern, source.lower())
        
        # Count total elongated characters in translation
        translated_count = sum(len(match.group()) for match in translated_matches 
                              if match.group()[0].isalnum())
        
        source_count = sum(len(match.group()) for match in source_matches
                          if match.group()[0].isalnum())
        
        # Flag if translation has significantly more elongation
        # Adjusted: 3x threshold and lower minimum (40)
        if translated_count > 40 and translated_count > source_count * 3:
            return True
        
        return False
    
    def _has_phrase_repetition(self, translated: str, source: str) -> bool:
        """
        Detect consecutive repetitions of words or phrases.
        """
        # Tokenize (simple whitespace split, preserve punctuation attachment)
        translated_tokens = self._tokenize(translated)
        source_tokens = self._tokenize(source)
        
        # Check for n-gram repetitions (1 to max_ngram_size words)
        for n in range(1, min(self.max_ngram_size + 1, len(translated_tokens))):
            if self._has_ngram_repetition(translated_tokens, source_tokens, n):
                return True
        
        return False
    
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization preserving words and punctuation."""
        # Split on whitespace and filter empty strings
        tokens = text.split()
        return [t.lower() for t in tokens if t]
    
    def _has_ngram_repetition(
        self, 
        translated_tokens: List[str], 
        source_tokens: List[str], 
        n: int
    ) -> bool:
        """
        Check for repetition of n-grams in translation that don't appear in source.
        """
        # Generate n-grams for translation
        translated_ngrams = self._get_ngrams(translated_tokens, n)
        source_ngrams = self._get_ngrams(source_tokens, n)
        
        # Also check for actual word repetitions (not just ngram positions)
        # For example "is really the" repeating multiple times even if non-consecutive
        translated_ngram_counts = Counter(translated_ngrams)
        source_ngram_counts = Counter(source_ngrams)
        
        # Get max repetition count in source for ANY ngram
        max_source_repetition = max(source_ngram_counts.values()) if source_ngram_counts else 0
        
        for ngram, count in translated_ngram_counts.items():
            if count >= self.min_repetitions:
                # Check if source has a similar repetition pattern (not necessarily the same ngram)
                # For multi-word ngrams (n>1), check if source has ANY ngram repeated as much
                # For single words, check if translated significantly exceeds source pattern
                if n > 1:
                    # For multi-word phrases, allow if source has similar repetition level
                    if count > max_source_repetition * 1.5:
                        return True
                else:
                    # For single words, allow equal repetition from source
                    if count > max_source_repetition * 1.5:
                        return True
        
        # Look for consecutive repetitions in translation (original check)
        for i in range(len(translated_ngrams) - self.min_repetitions + 1):
            # Get a window of consecutive n-grams
            window = translated_ngrams[i:i + self.min_repetitions]
            
            # Check if all n-grams in window are identical
            if len(set(window)) == 1:
                ngram = window[0]
                
                # Check if source has ANY similar pattern of consecutive repetition
                max_source_consecutive = self._count_max_consecutive_any(source_ngrams)
                max_translated_consecutive = self._count_max_consecutive(translated_ngrams, ngram)
                
                # If source has natural consecutive repetitions of ANY ngram, allow similar in translation
                if max_source_consecutive >= self.min_repetitions:
                    # Source has natural repetition pattern - allow equal or slightly more in translation
                    # Only flag if translation has 2x+ more consecutive repetitions
                    if max_translated_consecutive > max_source_consecutive * 2:
                        return True
                else:
                    # Source doesn't have this consecutive repetition pattern - it's stammering
                    return True
        
        return False
    
    def _count_max_consecutive(self, ngrams: List[Tuple[str, ...]], target: Tuple[str, ...]) -> int:
        """Count maximum consecutive occurrences of an ngram."""
        max_count = 0
        current_count = 0
        
        for ngram in ngrams:
            if ngram == target:
                current_count += 1
                max_count = max(max_count, current_count)
            else:
                current_count = 0
        
        return max_count
    
    def _count_max_consecutive_any(self, ngrams: List[Tuple[str, ...]]) -> int:
        """Count maximum consecutive occurrences of ANY ngram."""
        if not ngrams:
            return 0
        
        max_count = 1
        current_count = 1
        prev_ngram = ngrams[0]
        
        for ngram in ngrams[1:]:
            if ngram == prev_ngram:
                current_count += 1
                max_count = max(max_count, current_count)
            else:
                current_count = 1
                prev_ngram = ngram
        
        return max_count
    
    def _get_ngrams(self, tokens: List[str], n: int) -> List[Tuple[str, ...]]:
        """Generate n-grams from token list."""
        return [tuple(tokens[i:i+n]) for i in range(len(tokens) - n + 1)]


def detect_stammering(source_sentence: str, translated_sentence: str) -> bool:
    detector = StammeringDetector(min_repetitions=3, max_ngram_size=5)
    return detector.detect(source_sentence, translated_sentence)
