import pandas as pd
import pdfplumber
import io
import logging

logger = logging.getLogger(__name__)

def extract_text_from_pdf(file_bytes) -> str:
    """Extracts all text from a PDF file."""
    text = []
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text.append(extracted)
        return "\n".join(text)
    except Exception as e:
        logger.error(f"Failed to extract text from PDF: {e}")
        return f"Error extracting PDF: {str(e)}"

def translate_dataframe(df: pd.DataFrame, translator_func, target_language: str) -> pd.DataFrame:
    """
    Translates all string columns in a DataFrame cell by cell.
    translator_func should be a callable like: lambda text, lang: string
    """
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
        df = pd.read_csv(io.BytesIO(file_bytes))
        if translator_func and target_language:
            df = translate_dataframe(df, translator_func, target_language)
        return df, 'dataframe'
    elif file_type in ['xlsx', 'xls', 'excel']:
        df = pd.read_excel(io.BytesIO(file_bytes))
        if translator_func and target_language:
            df = translate_dataframe(df, translator_func, target_language)
        return df, 'dataframe'
    else:
        raise ValueError(f"Unsupported file type: {file_type}")
