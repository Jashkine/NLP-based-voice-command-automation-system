"""Tests for command mapping module."""

import json
import pytest

from src.mapper import CommandMapper, CommandAuthorizationManager
from src.config import CommandMapping


@pytest.fixture
def commands_config():
    """Create sample commands configuration."""
    return {
        "test_command": CommandMapping(
            intent="test_command",
            command_type="test",
            parameters={"action": "test"},
            description="Test command"
        )
    }


@pytest.fixture
def mapper(commands_config):
    """Create command mapper for testing."""
    return CommandMapper(commands_config)


class TestCommandMapper:
    """Test command mapping functionality."""
    
    def test_initialization(self, mapper):
        """Test mapper initialization."""
        assert mapper is not None
        assert mapper.commands_config is not None
    
    def test_map_intent_to_command(self, mapper):
        """Test mapping intent to command."""
        command = mapper.map_intent_to_command(
            intent="test_command",
            confidence=0.95,
            transcribed_text="test input"
        )
        assert command is not None
        assert command["command_type"] == "test"
        assert command["intent"] == "test_command"
        assert command["confidence"] == 0.95
        assert command["status"] == "authorized"
    
    def test_unknown_intent_handling(self, mapper):
        """Test handling of unknown intent."""
        command = mapper.map_intent_to_command(
            intent="unknown_intent",
            confidence=0.5
        )
        assert command["command_type"] == "error"
        assert command["status"] == "rejected"
    
    def test_command_validation(self, mapper):
        """Test command validation."""
        valid_command = {
            "timestamp": "2024-01-01T00:00:00",
            "command_type": "test",
            "intent": "test",
            "confidence": 0.9,
            "parameters": {}
        }
        assert mapper.validate_command(valid_command) is True
    
    def test_invalid_command_validation(self, mapper):
        """Test validation of invalid command."""
        invalid_command = {
            "command_type": "test",
            # Missing required fields
        }
        assert mapper.validate_command(invalid_command) is False
    
    def test_format_command_output(self, mapper):
        """Test command formatting."""
        command = {
            "timestamp": "2024-01-01T00:00:00",
            "command_type": "test",
            "intent": "test",
            "confidence": 0.9
        }
        formatted = mapper.format_command_output(command, pretty=True)
        assert isinstance(formatted, str)
        # Should be valid JSON
        parsed = json.loads(formatted)
        assert parsed["command_type"] == "test"


class TestCommandAuthorizationManager:
    """Test authorization management."""
    
    def test_initialization(self):
        """Test authorization manager initialization."""
        auth = CommandAuthorizationManager(["intent1", "intent2"])
        assert auth is not None
        assert len(auth.authorized_intents) == 2
    
    def test_authorization_check(self):
        """Test authorization checking."""
        auth = CommandAuthorizationManager(["allowed_intent"])
        assert auth.is_authorized("allowed_intent", 0.95) is True
        assert auth.is_authorized("denied_intent", 0.95) is False
    
    def test_low_confidence_rejection(self):
        """Test low confidence rejection."""
        auth = CommandAuthorizationManager(["test_intent"])
        assert auth.is_authorized("test_intent", 0.5, min_confidence=0.8) is False
    
    def test_add_authorized_intent(self):
        """Test adding authorized intent."""
        auth = CommandAuthorizationManager()
        auth.add_authorized_intent("new_intent")
        assert "new_intent" in auth.authorized_intents
    
    def test_remove_authorized_intent(self):
        """Test removing authorized intent."""
        auth = CommandAuthorizationManager(["remove_me"])
        auth.remove_authorized_intent("remove_me")
        assert "remove_me" not in auth.authorized_intents


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
