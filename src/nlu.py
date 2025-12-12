"""Natural Language Understanding (NLU) module for intent classification."""

from typing import Dict, Optional, Tuple
import numpy as np
from transformers import pipeline, Pipeline
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
        self.classifier = None
        self._init_classifier()
        self._build_intent_index()
    
    def _init_classifier(self) -> None:
        """Initialize zero-shot classification pipeline."""
        try:
            logger.info(f"Loading NLU model: {self.config.model_name}")
            # Using sentence-transformers based zero-shot classifier
            self.classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli",
                device=0 if self.config.device == "cuda" else -1
            )
            logger.info("NLU model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load NLU model: {e}")
            # Fallback to sentiment analysis
            logger.warning("Falling back to sentiment analysis")
            self.classifier = pipeline(
                "sentiment-analysis",
                model=self.config.model_name,
                device=0 if self.config.device == "cuda" else -1
            )
    
    def _build_intent_index(self) -> None:
        """Build intent index from patterns."""
        self.intent_candidates = list(self.intents_config.keys())
        if not self.intent_candidates:
            logger.warning("No intents configured")
    
    def classify_intent(
        self,
        text: str,
        use_zero_shot: bool = True
    ) -> Tuple[str, float]:
        """Classify intent from text.
        
        Args:
            text: Input text
            use_zero_shot: Use zero-shot classification
        
        Returns:
            Tuple of (intent, confidence)
        """
        if not self.intent_candidates:
            logger.warning("No intents available for classification")
            return "unknown", 0.0
        
        try:
            if use_zero_shot and self.classifier:
                result = self.classifier(
                    text,
                    self.intent_candidates,
                    multi_class=False
                )
                intent = result["labels"][0]
                confidence = result["scores"][0]
            else:
                # Fallback: simple keyword matching
                intent, confidence = self._keyword_match(text)
            
            # Check against confidence threshold
            if confidence < self.config.confidence_threshold:
                logger.warning(f"Low confidence ({confidence:.2f}) for intent: {intent}")
                return "unknown", confidence
            
            logger.info(f"Classified intent: {intent} (confidence: {confidence:.2f})")
            return intent, float(confidence)
            
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
