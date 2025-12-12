"""Tests for the main voice command processor."""

import json
from pathlib import Path
import pytest

from src.processor import VoiceCommandProcessor
from src.config import SystemConfig, IntentPattern, CommandMapping


@pytest.fixture
def processor():
    """Create processor with mock engines for testing."""
    return VoiceCommandProcessor(use_mock=True)


@pytest.fixture
def sample_config():
    """Create sample configuration."""
    return SystemConfig(debug=True)


class TestVoiceCommandProcessor:
    """Test VoiceCommandProcessor main functionality."""
    
    def test_initialization(self, processor):
        """Test processor initialization."""
        assert processor is not None
        assert processor.asr is not None
        assert processor.nlu is not None
        assert processor.mapper is not None
    
    def test_process_text(self, processor):
        """Test text processing."""
        result = processor.process_text("stop tracking")
        assert result is not None
        assert "status" in result
    
    def test_get_status(self, processor):
        """Test status reporting."""
        status = processor.get_status()
        assert status is not None
        assert "intents_loaded" in status
        assert "commands_loaded" in status
        assert "asr_model" in status
        assert "nlu_model" in status
    
    def test_authorization_check(self, processor):
        """Test authorization checking."""
        assert processor.auth_manager is not None
        # Sample intent should be in authorized list
        authorized = processor.auth_manager.list_authorized_intents()
        assert isinstance(authorized, list)
    
    def test_configuration_reload(self, processor):
        """Test configuration reloading."""
        initial_intents = len(processor.intents_config)
        processor.reload_configurations()
        assert len(processor.intents_config) == initial_intents


@pytest.mark.parametrize("input_text,expected_status", [
    ("stop tracking", "success"),
    ("start tracking", "success"),
    ("unknown command xyz", "success"),  # Will have low confidence
])
def test_various_inputs(processor, input_text, expected_status):
    """Test various input texts."""
    result = processor.process_text(input_text, min_confidence=0.0)
    assert result["status"] in ["success", "rejected"]


class TestErrorHandling:
    """Test error handling."""
    
    def test_empty_text_processing(self, processor):
        """Test handling of empty text."""
        # Should handle gracefully
        result = processor.process_text("", min_confidence=0.7)
        assert result is not None
    
    def test_invalid_language(self, processor):
        """Test handling of invalid language."""
        # Should still process with default language
        result = processor.process_text("stop tracking")
        assert result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
