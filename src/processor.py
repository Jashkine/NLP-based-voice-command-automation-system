"""Voice command processor - main orchestrator."""

from typing import Dict, Any, Optional
from pathlib import Path
import numpy as np
from loguru import logger

from .config import (
    SystemConfig, load_intents_config, load_commands_config
)
from .asr import ASREngine, MockASREngine
from .nlu import NLUEngine, MockNLUEngine
from .mapper import CommandMapper, CommandAuthorizationManager


class VoiceCommandProcessor:
    """Main orchestrator for voice command processing."""
    
    def __init__(
        self,
        config: Optional[SystemConfig] = None,
        use_mock: bool = False
    ):
        """Initialize voice command processor.
        
        Args:
            config: System configuration
            use_mock: Use mock engines for testing
        """
        self.config = config or SystemConfig()
        self.use_mock = use_mock
        
        # Load configurations
        self.intents_config = load_intents_config(self.config.intents_config)
        self.commands_config = load_commands_config(self.config.commands_config)
        
        # Initialize engines
        if use_mock:
            self.asr = MockASREngine(self.config.asr)
            self.nlu = MockNLUEngine(self.config.nlu, self.intents_config)
        else:
            self.asr = ASREngine(self.config.asr)
            self.nlu = NLUEngine(self.config.nlu, self.intents_config)
        
        # Initialize command processing
        self.mapper = CommandMapper(self.commands_config)
        self.auth_manager = CommandAuthorizationManager(
            list(self.commands_config.keys())
        )
        
        logger.info("VoiceCommandProcessor initialized")
        logger.debug(f"Loaded {len(self.intents_config)} intents")
        logger.debug(f"Loaded {len(self.commands_config)} command mappings")
    
    def process_audio(
        self,
        audio_input,
        language: Optional[str] = None,
        min_confidence: float = 0.7
    ) -> Dict[str, Any]:
        """Process audio input and generate command.
        
        Args:
            audio_input: Audio data or file path
            language: Language code
            min_confidence: Minimum confidence threshold
        
        Returns:
            Processing result with command or error
        """
        logger.info("Processing audio input...")
        
        # Step 1: Transcribe audio
        try:
            transcribed_text = self.asr.transcribe(audio_input, language)
        except Exception as e:
            logger.error(f"ASR failed: {e}")
            return {
                "status": "error",
                "error": f"Speech recognition failed: {str(e)}",
                "stage": "asr"
            }
        
        if not transcribed_text.strip():
            logger.warning("Empty transcription")
            return {
                "status": "error",
                "error": "No speech detected",
                "stage": "asr"
            }
        
        # Step 2: Classify intent
        try:
            intent, confidence = self.nlu.classify_intent(transcribed_text)
        except Exception as e:
            logger.error(f"NLU failed: {e}")
            return {
                "status": "error",
                "error": f"Intent classification failed: {str(e)}",
                "stage": "nlu",
                "transcribed_text": transcribed_text
            }
        
        # Step 3: Extract entities
        try:
            entities = self.nlu.extract_entities(transcribed_text)
        except Exception as e:
            logger.warning(f"Entity extraction failed: {e}")
            entities = {}
        
        # Step 4: Check authorization
        if not self.auth_manager.is_authorized(intent, confidence, min_confidence):
            logger.warning(f"Command authorization failed: {intent}")
            return {
                "status": "rejected",
                "reason": "Authorization failed",
                "intent": intent,
                "confidence": round(confidence, 3),
                "transcribed_text": transcribed_text,
                "stage": "authorization"
            }
        
        # Step 5: Generate command
        try:
            command = self.mapper.map_intent_to_command(
                intent=intent,
                confidence=confidence,
                entities=entities,
                transcribed_text=transcribed_text
            )
        except Exception as e:
            logger.error(f"Command mapping failed: {e}")
            return {
                "status": "error",
                "error": f"Command mapping failed: {str(e)}",
                "stage": "mapper",
                "transcribed_text": transcribed_text
            }
        
        # Step 6: Validate command
        if not self.mapper.validate_command(command):
            logger.error("Command validation failed")
            return {
                "status": "error",
                "error": "Command validation failed",
                "stage": "validation",
                "command": command
            }
        
        logger.info(f"Successfully generated command: {command['command_type']}")
        return {
            "status": "success",
            "command": command,
            "transcribed_text": transcribed_text,
            "intent": intent,
            "confidence": round(confidence, 3)
        }
    
    def process_text(
        self,
        text: str,
        min_confidence: float = 0.7
    ) -> Dict[str, Any]:
        """Process text input and generate command (skips ASR).
        
        Args:
            text: Input text
            min_confidence: Minimum confidence threshold
        
        Returns:
            Processing result with command or error
        """
        logger.info(f"Processing text input: {text}")
        
        # Skip ASR, go directly to NLU
        try:
            intent, confidence = self.nlu.classify_intent(text)
        except Exception as e:
            logger.error(f"NLU failed: {e}")
            return {
                "status": "error",
                "error": f"Intent classification failed: {str(e)}",
                "stage": "nlu"
            }
        
        # Extract entities
        try:
            entities = self.nlu.extract_entities(text)
        except Exception as e:
            logger.warning(f"Entity extraction failed: {e}")
            entities = {}
        
        # Check authorization
        if not self.auth_manager.is_authorized(intent, confidence, min_confidence):
            logger.warning(f"Command authorization failed: {intent}")
            return {
                "status": "rejected",
                "reason": "Authorization failed",
                "intent": intent,
                "confidence": round(confidence, 3),
                "transcribed_text": text
            }
        
        # Generate command
        try:
            command = self.mapper.map_intent_to_command(
                intent=intent,
                confidence=confidence,
                entities=entities,
                transcribed_text=text
            )
        except Exception as e:
            logger.error(f"Command mapping failed: {e}")
            return {
                "status": "error",
                "error": f"Command mapping failed: {str(e)}",
                "stage": "mapper"
            }
        
        # Validate command
        if not self.mapper.validate_command(command):
            logger.error("Command validation failed")
            return {
                "status": "error",
                "error": "Command validation failed",
                "stage": "validation"
            }
        
        logger.info(f"Successfully generated command: {command['command_type']}")
        return {
            "status": "success",
            "command": command,
            "transcribed_text": text,
            "intent": intent,
            "confidence": round(confidence, 3)
        }
    
    def reload_configurations(self) -> None:
        """Reload intents and commands configurations."""
        logger.info("Reloading configurations...")
        self.intents_config = load_intents_config(self.config.intents_config)
        self.commands_config = load_commands_config(self.config.commands_config)
        
        # Re-initialize engines with new configs
        self.nlu = NLUEngine(self.config.nlu, self.intents_config)
        self.mapper = CommandMapper(self.commands_config)
        self.auth_manager = CommandAuthorizationManager(list(self.commands_config.keys()))
        
        logger.info("Configurations reloaded")
    
    def get_status(self) -> Dict[str, Any]:
        """Get processor status."""
        return {
            "intents_loaded": len(self.intents_config),
            "commands_loaded": len(self.commands_config),
            "authorized_intents": self.auth_manager.list_authorized_intents(),
            "asr_model": self.config.asr.model_name,
            "nlu_model": self.config.nlu.model_name,
            "debug_mode": self.config.debug
        }
