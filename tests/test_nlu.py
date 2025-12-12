"""Tests for NLU module."""

import pytest

from src.nlu import MockNLUEngine
from src.config import IntentPattern


@pytest.fixture
def nlu_engine():
    """Create mock NLU engine for testing."""
    intents_config = {
        "test_intent": IntentPattern(
            intent="test_intent",
            patterns=["test pattern one", "test pattern two"],
            actions={"description": "Test intent"}
        )
    }
    return MockNLUEngine(intents_config=intents_config)


class TestNLUEngine:
    """Test NLU functionality."""
    
    def test_initialization(self, nlu_engine):
        """Test NLU engine initialization."""
        assert nlu_engine is not None
        assert nlu_engine.config is not None
    
    def test_intent_classification(self, nlu_engine):
        """Test intent classification."""
        intent, confidence = nlu_engine.classify_intent("test pattern")
        assert isinstance(intent, str)
        assert isinstance(confidence, float)
        assert 0 <= confidence <= 1
    
    def test_entity_extraction(self, nlu_engine):
        """Test entity extraction."""
        entities = nlu_engine.extract_entities("test pattern")
        assert isinstance(entities, dict)
    
    def test_intent_description(self, nlu_engine):
        """Test getting intent description."""
        description = nlu_engine.get_intent_description("test_intent")
        assert isinstance(description, str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
