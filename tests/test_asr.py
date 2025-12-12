"""Tests for ASR module."""

import numpy as np
import pytest

from src.asr import MockASREngine


@pytest.fixture
def asr_engine():
    """Create mock ASR engine for testing."""
    return MockASREngine()


class TestASREngine:
    """Test ASR functionality."""
    
    def test_initialization(self, asr_engine):
        """Test ASR engine initialization."""
        assert asr_engine is not None
        assert asr_engine.config is not None
    
    def test_transcribe(self, asr_engine):
        """Test transcription with mock audio."""
        # Create mock audio array (16kHz, 1 second)
        audio = np.random.randn(16000).astype(np.float32)
        result = asr_engine.transcribe(audio)
        assert isinstance(result, str)
    
    def test_configuration(self, asr_engine):
        """Test ASR configuration."""
        assert asr_engine.config.sample_rate == 16000
        assert asr_engine.config.language == "en"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
