import io
import logging
import pandas as pd
from markitdown import MarkItDown

logger = logging.getLogger(__name__)


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extracts all text from a PDF file as Markdown using MarkItDown."""
    try:
        md = MarkItDown()
        result = md.convert_stream(io.BytesIO(file_bytes), file_extension='.pdf')
        return result.text_content
    except Exception as e:
        logger.error(f"Failed to extract text from PDF via MarkItDown: {e}")
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
            translated_df[col] = translated_df[col].apply(
                lambda x: translator_func(str(x), target_language) if isinstance(x, str) and str(x).strip() else x
            )

    return translated_df


def process_file_upload(
    uploaded_file,
    file_type: str,
    translator_func=None,
    target_language: str = None,
    gemini_client=None
):
    """
    Main router and service layer for file processing based on type.
    Encapsulates format-specific extraction (PDF, TXT, CSV, Excel).
    """
    file_bytes = uploaded_file.read()

    normalized_type = file_type.lower().strip().lstrip('.')

    if normalized_type == 'pdf':
        if gemini_client:
            try:
                text = gemini_client.extract_pdf_markdown(file_bytes)
                return text, 'text'
            except Exception as e:
                logger.warning(f"Gemini PDF extraction failed ({e}), falling back to local MarkItDown.")
        text = extract_text_from_pdf(file_bytes)
        return text, 'text'

    elif normalized_type == 'txt':
        return file_bytes.decode('utf-8', errors='replace'), 'text'

    elif normalized_type == 'csv':
        try:
            df = pd.read_csv(io.BytesIO(file_bytes))
        except pd.errors.EmptyDataError as e:
            logger.error(f"Empty CSV file uploaded: {e}")
            raise ValueError("The uploaded CSV file is empty.") from e

        if translator_func and target_language:
            df = translate_dataframe(df, translator_func, target_language)
        return df, 'dataframe'

    elif normalized_type in ['xlsx', 'xls', 'excel']:
        try:
            df = pd.read_excel(io.BytesIO(file_bytes))
        except ValueError as e:
            logger.error(f"Excel read error: {e}")
            raise ValueError(f"Failed to read Excel file: {str(e)}") from e

        if translator_func and target_language:
            df = translate_dataframe(df, translator_func, target_language)
        return df, 'dataframe'

    else:
        raise ValueError(f"Unsupported file type: {file_type}")
