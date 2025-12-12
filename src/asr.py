"""Automatic Speech Recognition (ASR) module using OpenAI Whisper."""

import io
from pathlib import Path
from typing import Optional
import numpy as np
import whisper
from loguru import logger

from .config import ASRConfig


class ASREngine:
    """Speech-to-text engine using OpenAI Whisper."""
    
    def __init__(self, config: Optional[ASRConfig] = None):
        """Initialize ASR engine.
        
        Args:
            config: ASR configuration
        """
        self.config = config or ASRConfig()
        self.model = None
        self._load_model()
    
    def _load_model(self) -> None:
        """Load Whisper model."""
        try:
            logger.info(f"Loading Whisper model: {self.config.model_name}")
            self.model = whisper.load_model(
                self.config.model_name,
                device=self.config.device
            )
            logger.info("Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise
    
    def transcribe(
        self,
        audio_input: np.ndarray | str | Path,
        language: Optional[str] = None
    ) -> str:
        """Transcribe audio to text.
        
        Args:
            audio_input: Audio data (numpy array), file path, or audio file path
            language: Language code (defaults to config language)
        
        Returns:
            Transcribed text
        """
        if self.model is None:
            raise RuntimeError("ASR model not loaded")
        
        language = language or self.config.language
        
        try:
            # Handle different input types
            if isinstance(audio_input, (str, Path)):
                audio = whisper.load_audio(str(audio_input))
            else:
                # Assume numpy array
                audio = audio_input.astype(np.float32) / 32768.0
            
            logger.info(f"Transcribing audio (language: {language})")
            
            result = self.model.transcribe(
                audio,
                language=language,
                fp16=(self.config.precision == "float16"),
                verbose=False
            )
            
            text = result.get("text", "").strip()
            confidence = result.get("segments", [{}])[0].get("confidence", 0.0) if result.get("segments") else 0.0
            
            logger.info(f"Transcription: {text} (confidence: {confidence:.2f})")
            return text
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise
    
    def transcribe_file(self, audio_path: Path | str, language: Optional[str] = None) -> str:
        """Transcribe audio file.
        
        Args:
            audio_path: Path to audio file
            language: Language code
        
        Returns:
            Transcribed text
        """
        return self.transcribe(audio_path, language)


class MockASREngine:
    """Mock ASR engine for testing without Whisper."""
    
    def __init__(self, config: Optional[ASRConfig] = None):
        """Initialize mock ASR engine."""
        self.config = config or ASRConfig()
        logger.info("Using MockASREngine for testing")
    
    def transcribe(
        self,
        audio_input,
        language: Optional[str] = None
    ) -> str:
        """Return mock transcription."""
        return "mock transcription"
    
    def transcribe_file(self, audio_path: Path | str, language: Optional[str] = None) -> str:
        """Return mock file transcription."""
        return "mock file transcription"
