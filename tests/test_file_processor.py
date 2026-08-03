import pytest
import pandas as pd
import io
from unittest.mock import patch, MagicMock
from modules.file_processor import translate_dataframe, process_file_upload, extract_text_from_pdf

def dummy_translator(text, lang):
    return f"{text}_{lang}"

def test_translate_dataframe():
    df = pd.DataFrame({
        "A": ["Hello", "World", 123],
        "B": ["Test", None, ""]
    })
    
    translated_df = translate_dataframe(df, dummy_translator, "es")
    
    # Check that strings are translated and non-strings/nulls are ignored
    assert translated_df.loc[0, "A"] == "Hello_es"
    assert translated_df.loc[2, "A"] == 123  # Int untouched
    
    assert translated_df.loc[0, "B"] == "Test_es"
    assert pd.isnull(translated_df.loc[1, "B"])
    assert translated_df.loc[2, "B"] == ""  # Empty string untouched

@patch('modules.file_processor.MarkItDown')
def test_extract_text_from_pdf(mock_markitdown):
    # Mock PDF behavior
    mock_instance = MagicMock()
    mock_result = MagicMock()
    mock_result.text_content = "# Page 1 Text."
    mock_instance.convert_stream.return_value = mock_result
    mock_markitdown.return_value = mock_instance

    result = extract_text_from_pdf(b'fake_pdf_bytes')
    
    assert result == "# Page 1 Text."

def test_process_file_upload_txt():
    class DummyFile:
        def read(self):
            return b"Hello world"
            
    result, file_type = process_file_upload(DummyFile(), 'txt')
    assert result == "Hello world"
    assert file_type == "text"

def test_process_file_upload_csv():
    class DummyFile:
        def read(self):
            return b"col1,col2\nval1,val2\n"
            
    result, file_type = process_file_upload(DummyFile(), 'csv')
    assert isinstance(result, pd.DataFrame)
    assert file_type == "dataframe"
    assert result.loc[0, "col1"] == "val1"
