import pytest
import os
from modules.tts_engine import TTSEngine

def test_tts_engine_init():
    engine = TTSEngine(output_dir="test_audio")
    assert os.path.exists("test_audio")
    # cleanup
    os.rmdir("test_audio")

def test_generate_audio_gtts_integration():
    """
    Integration test for gTTS. 
    Actually generates an audio file by calling Google's public TTS endpoint.
    """
    engine = TTSEngine(output_dir="temp_test_audio")
    filepath = engine.generate_audio("Hello world, this is a real integration test.", lang="en", engine="gTTS")
    
    assert os.path.exists(filepath)
    assert filepath.endswith(".mp3")
    
    # Check that the file actually contains data (greater than 0 bytes)
    file_size = os.path.getsize(filepath)
    assert file_size > 0
    
    # Check for MP3 ID3 header to prove it is a valid audio file
    with open(filepath, 'rb') as f:
        header = f.read(3)
        assert header == b'ID3', "Generated file is not a valid MP3 audio file"

    
    # cleanup
    engine.cleanup(filepath)
    os.rmdir("temp_test_audio")

def test_generate_audio_empty_text():
    engine = TTSEngine()
    with pytest.raises(ValueError, match="Text cannot be empty"):
        engine.generate_audio("")

def test_generate_audio_invalid_engine():
    engine = TTSEngine()
    with pytest.raises(ValueError, match="Unsupported TTS engine"):
        engine.generate_audio("Hello", engine="Invalid")
