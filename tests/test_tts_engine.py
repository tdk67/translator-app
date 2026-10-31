import pytest
from modules.tts_engine import TTSEngine


def test_tts_engine_init():
    engine = TTSEngine()
    assert engine is not None


def test_strip_markdown():
    engine = TTSEngine()
    markdown_text = "# Header\n\nThis is **bold** and *italic* text with [a link](https://example.com)."
    stripped = engine.strip_markdown(markdown_text)
    assert "#" not in stripped
    assert "**" not in stripped
    assert "Header" in stripped
    assert "This is bold and italic text with a link." in stripped


def test_generate_audio_gtts_integration():
    """
    Integration test for gTTS. 
    Actually generates an audio file by calling Google's public TTS endpoint.
    """
    engine = TTSEngine()
    audio_bytes = engine.generate_audio("Hello world, this is a real integration test.", lang="en", engine="gTTS")

    assert isinstance(audio_bytes, bytes)
    assert len(audio_bytes) > 0

    # Check for MP3 ID3 header or MPEG frame sync (0xFF) to prove it is a valid audio file
    is_id3 = audio_bytes.startswith(b'ID3')
    is_mpeg = audio_bytes.startswith(b'\xff')
    assert is_id3 or is_mpeg, "Generated file is not a valid MP3 audio file"


def test_generate_audio_empty_text():
    engine = TTSEngine()
    with pytest.raises(ValueError, match="Text cannot be empty"):
        engine.generate_audio("")


def test_generate_audio_whitespace_or_empty_markdown():
    engine = TTSEngine()
    with pytest.raises(ValueError, match="Text cannot be empty"):
        engine.generate_audio("   ")


def test_generate_audio_invalid_engine():
    engine = TTSEngine()
    with pytest.raises(ValueError, match="Unsupported TTS engine"):
        engine.generate_audio("Hello", engine="InvalidEngine")
