"""Command mapping and JSON generation module."""

import json
from datetime import datetime
from typing import Dict, Any, Optional
from loguru import logger

from .config import CommandMapping


class CommandMapper:
    """Maps recognized intents to JSON commands."""
    
    def __init__(self, commands_config: Dict[str, CommandMapping]):
        """Initialize command mapper.
        
        Args:
            commands_config: Command mappings
        """
        self.commands_config = commands_config
        logger.info(f"Initialized command mapper with {len(commands_config)} commands")
    
    def map_intent_to_command(
        self,
        intent: str,
        confidence: float,
        entities: Optional[Dict[str, str]] = None,
        transcribed_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """Map recognized intent to command JSON.
        
        Args:
            intent: Recognized intent name
            confidence: Classification confidence
            entities: Extracted entities
            transcribed_text: Original transcribed text
        
        Returns:
            Command JSON dictionary
        """
        entities = entities or {}
        
        if intent not in self.commands_config:
            logger.warning(f"Unknown intent: {intent}")
            return self._create_error_response(intent, confidence, transcribed_text)
        
        command_mapping = self.commands_config[intent]
        
        command_json = {
            "timestamp": datetime.utcnow().isoformat(),
            "command_type": command_mapping.command_type,
            "intent": intent,
            "confidence": round(confidence, 3),
            "transcribed_text": transcribed_text or "",
            "parameters": self._merge_parameters(command_mapping.parameters, entities),
            "description": command_mapping.description,
            "status": "authorized"
        }
        
        logger.info(f"Mapped intent '{intent}' to command: {command_mapping.command_type}")
        return command_json
    
    def _merge_parameters(
        self,
        base_params: Dict[str, str],
        entity_params: Dict[str, str]
    ) -> Dict[str, str]:
        """Merge base parameters with extracted entities.
        
        Args:
            base_params: Base parameters from configuration
            entity_params: Extracted entity parameters
        
        Returns:
            Merged parameters dictionary
        """
        merged = base_params.copy()
        merged.update(entity_params)
        return merged
    
    def _create_error_response(
        self,
        intent: str,
        confidence: float,
        transcribed_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create error response for unknown intent.
        
        Args:
            intent: Unknown intent
            confidence: Classification confidence
            transcribed_text: Original transcribed text
        
        Returns:
            Error response JSON
        """
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "command_type": "error",
            "intent": intent,
            "confidence": round(confidence, 3),
            "transcribed_text": transcribed_text or "",
            "parameters": {},
            "error": f"Unknown intent: {intent}",
            "status": "rejected"
        }
    
    def validate_command(self, command_json: Dict[str, Any]) -> bool:
        """Validate generated command.
        
        Args:
            command_json: Command to validate
        
        Returns:
            True if valid, False otherwise
        """
        required_fields = ["command_type", "intent", "confidence", "timestamp"]
        
        for field in required_fields:
            if field not in command_json:
                logger.error(f"Missing required field: {field}")
                return False
        
        if not isinstance(command_json.get("confidence"), (int, float)):
            logger.error("Confidence must be numeric")
            return False
        
        if not (0 <= command_json["confidence"] <= 1):
            logger.error("Confidence must be between 0 and 1")
            return False
        
        return True
    
    def format_command_output(
        self,
        command_json: Dict[str, Any],
        pretty: bool = True
    ) -> str:
        """Format command JSON for output.
        
        Args:
            command_json: Command to format
            pretty: Pretty print JSON
        
        Returns:
            Formatted JSON string
        """
        if pretty:
            return json.dumps(command_json, indent=2)
        return json.dumps(command_json)


class CommandAuthorizationManager:
    """Manages command authorization and security."""
    
    def __init__(self, authorized_intents: Optional[list[str]] = None):
        """Initialize authorization manager.
        
        Args:
            authorized_intents: List of authorized intents
        """
        self.authorized_intents = authorized_intents or []
        logger.info(f"Initialized authorization manager with {len(self.authorized_intents)} authorized intents")
    
    def is_authorized(self, intent: str, confidence: float, min_confidence: float = 0.8) -> bool:
        """Check if command is authorized.
        
        Args:
            intent: Intent to check
            confidence: Classification confidence
            min_confidence: Minimum confidence threshold for authorization
        
        Returns:
            True if authorized, False otherwise
        """
        is_authorized = intent in self.authorized_intents and confidence >= min_confidence
        
        if not is_authorized:
            reason = "intent not authorized" if intent not in self.authorized_intents else "low confidence"
            logger.warning(f"Command rejected: {intent} ({reason})")
        
        return is_authorized
    
    def add_authorized_intent(self, intent: str) -> None:
        """Add intent to authorized list."""
        if intent not in self.authorized_intents:
            self.authorized_intents.append(intent)
            logger.info(f"Added authorized intent: {intent}")
    
    def remove_authorized_intent(self, intent: str) -> None:
        """Remove intent from authorized list."""
        if intent in self.authorized_intents:
            self.authorized_intents.remove(intent)
            logger.info(f"Removed authorized intent: {intent}")
    
    def list_authorized_intents(self) -> list[str]:
        """List all authorized intents."""
        return self.authorized_intents.copy()
