"""Configuration management for voice command automation system."""

from pathlib import Path
from typing import Dict, List, Optional
import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from loguru import logger


class IntentPattern(BaseModel):
    """Pattern definition for intent recognition."""
    
    intent: str
    patterns: List[str] = Field(..., description="List of example phrases")
    actions: Dict[str, str] = Field(default_factory=dict, description="Action mappings")


class Entity(BaseModel):
    """Entity definition for NLU."""
    
    name: str
    patterns: List[str] = Field(..., description="Regex patterns to match entities")
    type: str = Field(default="string")


class CommandMapping(BaseModel):
    """Maps recognized intents to JSON commands."""
    
    intent: str
    command_type: str
    parameters: Dict[str, str] = Field(default_factory=dict)
    description: str = ""


class VoiceConfig(BaseSettings):
    """Audio configuration."""
    
    sample_rate: int = 16000
    channels: int = 1
    chunk_duration: float = 1.0
    vad_threshold: float = 0.5
    
    class Config:
        env_prefix = "VOICE_"


class ASRConfig(BaseSettings):
    """Speech-to-Text configuration."""
    
    model_name: str = "base"  # tiny, base, small, medium, large
    language: str = "en"
    device: str = "cpu"
    precision: str = "float32"
    
    class Config:
        env_prefix = "ASR_"


class NLUConfig(BaseSettings):
    """NLU configuration."""
    
    model_name: str = "distilbert-base-uncased-finetuned-sst-2-english"
    confidence_threshold: float = 0.7
    device: str = "cpu"
    max_length: int = 128
    
    class Config:
        env_prefix = "NLU_"


class SystemConfig(BaseSettings):
    """Main system configuration."""
    
    app_name: str = "Voice Command Automation"
    version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"
    
    # Config paths
    intents_config: Path = Field(default_factory=lambda: Path("config/intents.yaml"))
    commands_config: Path = Field(default_factory=lambda: Path("config/commands.yaml"))
    
    # Sub-configurations
    voice: VoiceConfig = Field(default_factory=VoiceConfig)
    asr: ASRConfig = Field(default_factory=ASRConfig)
    nlu: NLUConfig = Field(default_factory=NLUConfig)
    
    class Config:
        env_file = ".env"
        env_nested_delimiter = "__"


def load_intents_config(config_path: Path) -> Dict[str, IntentPattern]:
    """Load intents configuration from YAML."""
    try:
        with open(config_path, 'r') as f:
            data = yaml.safe_load(f) or {}
        
        intents = {}
        for intent_name, intent_data in data.items():
            intents[intent_name] = IntentPattern(**intent_data)
        
        logger.info(f"Loaded {len(intents)} intents from {config_path}")
        return intents
    except FileNotFoundError:
        logger.warning(f"Intents config not found at {config_path}")
        return {}


def load_commands_config(config_path: Path) -> Dict[str, CommandMapping]:
    """Load command mappings from YAML."""
    try:
        with open(config_path, 'r') as f:
            data = yaml.safe_load(f) or {}
        
        commands = {}
        for cmd_name, cmd_data in data.items():
            commands[cmd_name] = CommandMapping(**cmd_data)
        
        logger.info(f"Loaded {len(commands)} command mappings from {config_path}")
        return commands
    except FileNotFoundError:
        logger.warning(f"Commands config not found at {config_path}")
        return {}


def get_system_config() -> SystemConfig:
    """Get or create system configuration."""
    return SystemConfig()
