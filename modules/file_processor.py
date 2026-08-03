import pandas as pd
from markitdown import MarkItDown
import io
import logging

logger = logging.getLogger(__name__)

def extract_text_from_pdf(file_bytes) -> str:
    """Extracts all text from a PDF file as Markdown to preserve formatting."""
    try:
        md = MarkItDown()
        result = md.convert_stream(io.BytesIO(file_bytes), file_extension='.pdf')
        return result.text_content
    except Exception as e:
        logger.error(f"Failed to extract text from PDF: {e}")
        return f"Error extracting PDF: {str(e)}"

def translate_dataframe(df: pd.DataFrame, translator_func, target_language: str) -> pd.DataFrame:
    """
    Translates all string columns in a DataFrame cell by cell.
    translator_func should be a callable like: lambda text, lang: string
    """
    if df.empty:
        return df.copy()

    translated_df = df.copy()
    
    for col in translated_df.columns:
        if pd.api.types.is_object_dtype(translated_df[col]) or pd.api.types.is_string_dtype(translated_df[col]):
            # Translate only string content
            translated_df[col] = translated_df[col].apply(
                lambda x: translator_func(str(x), target_language) if isinstance(x, str) and str(x).strip() else x
            )
            
    return translated_df

def process_file_upload(uploaded_file, file_type: str, translator_func=None, target_language: str=None):
    """
    Main router for file processing based on type.
    """
    file_bytes = uploaded_file.read()
    
    if file_type == 'pdf':
        text = extract_text_from_pdf(file_bytes)
        return text, 'text'
    elif file_type == 'txt':
        return file_bytes.decode('utf-8'), 'text'
    elif file_type == 'csv':
        try:
            df = pd.read_csv(io.BytesIO(file_bytes))
        except pd.errors.EmptyDataError as e:
            logger.error(f"Empty CSV file uploaded: {e}")
            raise ValueError("The uploaded CSV file is empty.") from e
            
        if translator_func and target_language:
            df = translate_dataframe(df, translator_func, target_language)
        return df, 'dataframe'
    elif file_type in ['xlsx', 'xls', 'excel']:
        try:
            df = pd.read_excel(io.BytesIO(file_bytes))
        except ValueError as e:
            # openpyxl raises ValueError for bad/empty Excel formats occasionally
            logger.error(f"Excel read error: {e}")
            raise ValueError(f"Failed to read Excel file: {str(e)}") from e
            
        if translator_func and target_language:
            df = translate_dataframe(df, translator_func, target_language)
        return df, 'dataframe'
    else:
        raise ValueError(f"Unsupported file type: {file_type}")
