"""Tests for configuration module."""

import pytest
from pathlib import Path

from src.config import (
    SystemConfig, VoiceConfig, ASRConfig, NLUConfig,
    IntentPattern, CommandMapping, get_system_config
)


class TestConfiguration:
    """Test configuration management."""
    
    def test_voice_config(self):
        """Test voice configuration."""
        config = VoiceConfig()
        assert config.sample_rate == 16000
        assert config.channels == 1
    
    def test_asr_config(self):
        """Test ASR configuration."""
        config = ASRConfig()
        assert config.model_name == "base"
        assert config.language == "en"
    
    def test_nlu_config(self):
        """Test NLU configuration."""
        config = NLUConfig()
        assert config.confidence_threshold == 0.7
        assert config.device in ["cpu", "cuda"]
    
    def test_system_config(self):
        """Test system configuration."""
        config = SystemConfig()
        assert config.app_name == "Voice Command Automation"
        assert config.voice is not None
        assert config.asr is not None
        assert config.nlu is not None
    
    def test_get_system_config(self):
        """Test getting system configuration."""
        config = get_system_config()
        assert config is not None
        assert isinstance(config, SystemConfig)


class TestConfigModels:
    """Test configuration models."""
    
    def test_intent_pattern(self):
        """Test intent pattern model."""
        pattern = IntentPattern(
            intent="test",
            patterns=["pattern1", "pattern2"],
            actions={"action": "value"}
        )
        assert pattern.intent == "test"
        assert len(pattern.patterns) == 2
    
    def test_command_mapping(self):
        """Test command mapping model."""
        mapping = CommandMapping(
            intent="test",
            command_type="control",
            parameters={"param": "value"},
            description="Test command"
        )
        assert mapping.intent == "test"
        assert mapping.command_type == "control"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
