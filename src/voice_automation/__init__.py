"""Voice command automation package initialization."""

from .processor import VoiceCommandProcessor
from .config import SystemConfig, get_system_config

__version__ = "1.0.0"
__author__ = "Auto Control Team"

__all__ = [
    "VoiceCommandProcessor",
    "SystemConfig",
    "get_system_config",
]
