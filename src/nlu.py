"""Natural Language Understanding (NLU) module for intent classification."""

from typing import Dict, Optional, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from loguru import logger

from .config import NLUConfig, IntentPattern


class NLUEngine:
    """Intent classification and entity extraction engine."""
    
    def __init__(self, config: Optional[NLUConfig] = None, intents_config: Optional[Dict[str, IntentPattern]] = None):
        """Initialize NLU engine.
        
        Args:
            config: NLU configuration
            intents_config: Intent patterns mapping
        """
        self.config = config or NLUConfig()
        self.intents_config = intents_config or {}
        self.vectorizer = TfidfVectorizer(lowercase=True, stop_words='english')
        self._build_intent_index()
    
    def _build_intent_index(self) -> None:
        """Build intent index from patterns."""
        self.intent_candidates = list(self.intents_config.keys())
        
        # Build pattern vectors for similarity matching
        self.pattern_vectors = {}
        if self.intent_candidates:
            all_patterns = []
            pattern_to_intent = {}
            
            for intent_name, intent_pattern in self.intents_config.items():
                for pattern in intent_pattern.patterns:
                    all_patterns.append(pattern)
                    pattern_to_intent[len(all_patterns) - 1] = intent_name
            
            if all_patterns:
                try:
                    self.vectorizer.fit(all_patterns)
                    for idx, pattern in enumerate(all_patterns):
                        intent = pattern_to_intent[idx]
                        if intent not in self.pattern_vectors:
                            self.pattern_vectors[intent] = []
                        vec = self.vectorizer.transform([pattern]).toarray()[0]
                        self.pattern_vectors[intent].append(vec)
                except Exception as e:
                    logger.warning(f"Failed to build pattern vectors: {e}")
        
        if not self.intent_candidates:
            logger.warning("No intents configured")
    
    def classify_intent(
        self,
        text: str,
        use_similarity: bool = True
    ) -> Tuple[str, float]:
        """Classify intent from text using TF-IDF similarity.
        
        Args:
            text: Input text
            use_similarity: Use similarity-based classification
        
        Returns:
            Tuple of (intent, confidence)
        """
        if not self.intent_candidates:
            logger.warning("No intents available for classification")
            return "unknown", 0.0
        
        try:
            if use_similarity and self.pattern_vectors:
                # Vectorize input text
                try:
                    input_vec = self.vectorizer.transform([text]).toarray()[0]
                except Exception:
                    # If text contains unknown words, use simpler matching
                    return self._keyword_match(text)
                
                # Compare with each intent's patterns
                best_intent = "unknown"
                best_score = 0.0
                
                for intent_name in self.intent_candidates:
                    if intent_name in self.pattern_vectors:
                        for pattern_vec in self.pattern_vectors[intent_name]:
                            similarity = cosine_similarity([input_vec], [pattern_vec])[0][0]
                            if similarity > best_score:
                                best_score = similarity
                                best_intent = intent_name
                
                confidence = float(best_score)
            else:
                # Fallback: simple keyword matching
                best_intent, confidence = self._keyword_match(text)
            
            # Check against confidence threshold
            if confidence < self.config.confidence_threshold:
                logger.warning(f"Low confidence ({confidence:.2f}) for intent: {best_intent}")
                return "unknown", confidence
            
            logger.info(f"Classified intent: {best_intent} (confidence: {confidence:.2f})")
            return best_intent, confidence
            
        except Exception as e:
            logger.error(f"Intent classification failed: {e}")
            return "unknown", 0.0
    
    def _keyword_match(self, text: str) -> Tuple[str, float]:
        """Fallback keyword matching for intent detection."""
        text_lower = text.lower()
        best_intent = "unknown"
        best_score = 0.0
        
        for intent_name, intent_pattern in self.intents_config.items():
            for pattern in intent_pattern.patterns:
                pattern_lower = pattern.lower()
                # Simple word overlap scoring
                text_words = set(text_lower.split())
                pattern_words = set(pattern_lower.split())
                overlap = len(text_words & pattern_words)
                score = overlap / max(len(pattern_words), 1)
                
                if score > best_score:
                    best_score = score
                    best_intent = intent_name
        
        return best_intent, min(best_score, 1.0)
    
    def extract_entities(self, text: str) -> Dict[str, str]:
        """Extract entities from text.
        
        Args:
            text: Input text
        
        Returns:
            Dictionary of extracted entities
        """
        entities = {}
        text_lower = text.lower()
        
        # Simple entity extraction from intents config
        for intent_name, intent_pattern in self.intents_config.items():
            for key, value in intent_pattern.actions.items():
                if key in text_lower:
                    entities[key] = value
        
        return entities
    
    def get_intent_description(self, intent: str) -> str:
        """Get description for an intent."""
        if intent in self.intents_config:
            return self.intents_config[intent].actions.get("description", "")
        return ""


class MockNLUEngine:
    """Mock NLU engine for testing."""
    
    def __init__(self, config: Optional[NLUConfig] = None, intents_config: Optional[Dict] = None):
        """Initialize mock NLU engine."""
        self.config = config or NLUConfig()
        self.intents_config = intents_config or {}
        logger.info("Using MockNLUEngine for testing")
    
    def classify_intent(self, text: str, use_zero_shot: bool = True) -> Tuple[str, float]:
        """Return mock classification."""
        return "test_intent", 0.95
    
    def extract_entities(self, text: str) -> Dict[str, str]:
        """Return mock entities."""
        return {}
    
    def get_intent_description(self, intent: str) -> str:
        """Return mock description."""
        return "Mock intent"
