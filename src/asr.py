"""Automatic Speech Recognition (ASR) module using lightweight libraries."""

import io
from pathlib import Path
from typing import Optional
import numpy as np
import speech_recognition as sr
from loguru import logger

from .config import ASRConfig


class ASREngine:
    """Speech-to-text engine using SpeechRecognition library."""
    
    def __init__(self, config: Optional[ASRConfig] = None):
        """Initialize ASR engine.
        
        Args:
            config: ASR configuration
        """
        self.config = config or ASRConfig()
        self.recognizer = sr.Recognizer()
        logger.info("SpeechRecognition ASR engine initialized")
    
    def transcribe(
        self,
        audio_input,
        language: Optional[str] = None
    ) -> str:
        """Transcribe audio to text.
        
        Args:
            audio_input: Audio data (numpy array), file path, or audio file path
            language: Language code (e.g., 'en-US', 'en-GB')
        
        Returns:
            Transcribed text
        """
        language = language or self.config.language
        
        try:
            # Handle different input types
            if isinstance(audio_input, (str, Path)):
                audio = self._load_audio_file(str(audio_input))
            else:
                # Assume numpy array
                audio = audio_input.astype(np.float32)
            
            # Convert numpy array to AudioData
            audio_data = sr.AudioData(
                audio.tobytes(),
                self.config.sample_rate,
                2  # 2 bytes per sample
            )
            
            logger.info(f"Transcribing audio (language: {language})")
            
            # Use Google Speech Recognition (free, no API key needed)
            text = self.recognizer.recognize_google(audio_data, language=language)
            
            logger.info(f"Transcription: {text}")
            return text
            
        except sr.RequestError as e:
            logger.error(f"Speech Recognition API unavailable: {e}")
            raise
        except sr.UnknownValueError:
            logger.warning("Audio could not be understood")
            return ""
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
    
    def _load_audio_file(self, file_path: str) -> np.ndarray:
        """Load audio file using pydub.
        
        Args:
            file_path: Path to audio file
        
        Returns:
            Audio data as numpy array
        """
        try:
            from pydub import AudioSegment
            
            # Auto-detect format from extension
            audio = AudioSegment.from_file(file_path)
            
            # Convert to numpy array
            samples = np.array(audio.get_array_of_samples())
            
            # Convert to 16-bit signed
            if audio.channels == 2:
                samples = samples.reshape((-1, 2))
                samples = samples.mean(axis=1).astype(np.int16)
            
            # Normalize to -1.0 to 1.0
            return samples.astype(np.float32) / 32768.0
            
        except ImportError:
            logger.error("pydub not available. Install with: pip install pydub")
            raise
        except Exception as e:
            logger.error(f"Failed to load audio file: {e}")
            raise


class MockASREngine:
    """Mock ASR engine for testing without downloading models."""
    
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
