# Globetrotter: Selective Translation & TTS
A Generative AI and ML Capstone Project

## Overview
The goal of this capstone project is to develop a web application using Streamlit that enables users to translate text into various languages, convert the translated text into speech, and download the resulting audio file. The project leverages **Google's Gemini API** for deep, context-aware translation and PDF layout preservation, alongside **Google Text-to-Speech (gTTS)** for speech synthesis.

## Features
- **Direct Text Input:** Type or paste text instantly into the processor.
- **Microphone Input:** Record audio directly in the browser. The audio is transcribed and sent to the Document Viewer using Gemini.
- **Smart File Extraction:** Upload PDF, TXT, CSV, or Excel files. Text files are read natively, dataframes are parsed safely, and PDFs are sent directly to Gemini to perfectly preserve their visual formatting (headers, tables, bold text) as Markdown.
- **Selective Translation:** Copy specific snippets of the extracted document to translate, instead of being forced to translate the entire document.
- **In-Memory Audio Generation (TTS):** Generates an MP3 audio stream of both the original and translated texts. The audio is stored in memory (bypassing local file storage restrictions for seamless cloud deployment) and can be downloaded instantly.
- **Guardrails:** Prevents prompt injection and handles malicious AI inputs gracefully.

---

## Installation

This project utilizes Python 3.12. Follow these steps to set up the project locally:

1. **Clone or Download the Repository** and extract the files to your local directory.
   
2. **Set up a Virtual Environment:**
   It is highly recommended to use a virtual environment to manage dependencies.
   ```bash
   python -m venv .venv
   ```

3. **Activate the Virtual Environment:**
   - On **Windows**: `.venv\Scripts\activate`
   - On **macOS/Linux**: `source .venv/bin/activate`

4. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## Detailed Usage Guide

1. Make sure your virtual environment is activated.
2. Run the Streamlit application:
   ```bash
   streamlit run app.py
   ```
3. Open your browser to `http://localhost:8501`.
4. **Configuration:** Expand the sidebar on the left. Enter your **Google Gemini API Key** and choose your Target Language (e.g., Spanish, French).
5. **Populate the Document Viewer:** 
   - **Upload** a PDF, TXT, or CSV file. The text will instantly populate in the "Document Viewer" panel. PDFs will retain their rich formatting (Markdown).
   - **Or Record** your voice. It will transcribe your speech and append it to the Document Viewer.
6. **Process the Text:**
   - Copy the specific chunk of text you want from the Document Viewer and paste it into the **"Text to Process"** box.
   - Click **"Translate Selected Text"** to translate it using Gemini.
   - Click **"Generate Audio (Original)"** or **"Generate Audio (Translated)"** to hear the text spoken aloud. The underlying Markdown is stripped cleanly before reaching the TTS engine.
   - Download the text or the generated MP3 file via the respective download buttons.

---

## Code Structure

```text
Edureka-Capstone-Translation/
│
├── app.py                      # Main Streamlit application entry point. Handles the UI, state, and wiring.
├── config.json                 # Configuration file for model names, supported languages, and TTS options.
├── requirements.txt            # List of Python dependencies required to run the project.
│
├── modules/                    # Core business logic and modularized backend services
│   ├── __init__.py
│   ├── file_processor.py       # Handles TXT, CSV, Excel parsing and translates DataFrames cell-by-cell.
│   ├── gemini_client.py        # Wrapper class for the Google GenAI SDK. Handles API requests, PDF Vision extraction, guardrails, and JSON parsing.
│   └── tts_engine.py           # Handles Text-to-Speech conversion using gTTS and in-memory byte streaming.
│
└── tests/                      # Pytest unit and integration test suite
    ├── __init__.py
    ├── test_file_processor.py  # Mocks file parsing and DataFrame logic for validation.
    ├── test_gemini_client.py   # Validates prompt injection blocks and checks error handling.
    └── test_tts_engine.py      # Verifies in-memory MP3 byte generation and ID3 header validation.
```

---

## Libraries Used & Why

- **`streamlit`**: The core frontend framework used to build the interactive web UI rapidly without needing to write raw HTML/JS/CSS.
- **`google-genai`**: The official, up-to-date Google GenAI SDK. It's used to connect to the Gemini API (`gemini-3.5-flash`) for text translation, audio transcription, and intelligent PDF-to-Markdown extraction.
- **`gTTS` (Google Text-to-Speech)**: Used as the primary Text-to-Speech engine. It sends text to Google's public Translate TTS API to retrieve human-sounding audio bytes.
- **`pandas` & `openpyxl`**: Used in `file_processor.py` for reading, parsing, and iterating through tabular data structures like CSV and Excel files.
- **`streamlit_mic_recorder`**: A specialized Streamlit component that allows capturing microphone audio directly from the user's web browser and passing it back to Python.
- **`markitdown`, `beautifulsoup4`, & `markdown`**: Used to intelligently clean and strip rich markdown formatting from text right before it hits the TTS engine, ensuring the audio reader doesn't pronounce markdown symbols (like asterisks or hash marks).
- **`python-dotenv`**: Used to safely load environment variables (like `GEMINI_API_KEY`) from a `.env` file instead of hardcoding secrets into the source code.
- **`pytest` & `pytest-asyncio`**: The testing framework used to ensure each module behaves reliably and correctly handles mock data or integration edge cases.

---

## Running Tests

The project includes a suite of unit tests built with `pytest` to ensure core functionalities work.

```bash
# Ensure PYTHONPATH is set to the current directory so modules can be imported
# On Windows (PowerShell):
$env:PYTHONPATH="."
pytest tests/

# On macOS/Linux:
PYTHONPATH="." pytest tests/
```

### Generating a Test Coverage Report

To see exactly how much of your codebase is covered by the tests, you can use the `pytest-cov` plugin:

```bash
# First, ensure you have the coverage plugin installed
pip install pytest-cov

# Run the tests with the coverage flag, specifically targeting the 'modules' folder
# On Windows (PowerShell):
$env:PYTHONPATH="."
pytest --cov=modules tests/

# On macOS/Linux:
PYTHONPATH="." pytest --cov=modules tests/
```
This will print out a table in your terminal showing the total percentage of lines of code that were successfully executed during the test run.

### Test Suites Breakdown

**1. `test_gemini_client.py`**
- **`test_guardrails_malicious_input`**: Simulates an attempt at prompt injection (e.g., asking the AI to ignore instructions). Verifies that the internal guardrails intercept it and return a safe error state instead of executing the translation request.
- **`test_guardrails_safe_input`**: Ensures that normal conversational texts are not falsely flagged as malicious.
- **`test_json_parse_error`**: Tests resilience against LLM hallucinations by passing non-JSON raw text to the parser, verifying it safely throws a `JSONParseError` instead of causing a generic crash.
- **`test_translate_text_integration`**: A live integration test that connects to the Gemini API (using your `.env` API key). It sends a real translation request (English to Spanish) and verifies that both the translation and the JSON structure response are correctly formed.

**2. `test_tts_engine.py`**
- **`test_tts_engine_init`**: Tests that the TTSEngine class initializes properly without unexpected filesystem dependencies.
- **`test_generate_audio_gtts_integration`**: A live integration test that requests Google's public TTS endpoint. It validates that the returned output is a valid `bytes` object with a non-zero length, and parses the binary response checking for standard MP3 magic bytes (ID3 tags or MPEG frame sync headers) to confirm media integrity.
- **`test_generate_audio_empty_text`**: Ensures the engine safely catches and rejects empty strings before querying the external API to save bandwidth.
- **`test_generate_audio_invalid_engine`**: Validates exception handling if a developer requests an unsupported TTS engine configuration.

**3. `test_file_processor.py`**
- **`test_translate_dataframe`**: A purely offline unit test using a mocked translator function. It builds a dummy Pandas DataFrame (simulating an uploaded Excel/CSV), verifies that valid string cells are translated accurately, and confirms that integers and blank cells are skipped to prevent corrupting table data types.
- **`test_translate_empty_dataframe`**: Verifies that submitting a completely empty DataFrame gracefully passes through the logic loop without causing an index out-of-bounds crash.
- **`test_extract_text_from_pdf`**: Mocks the internal `MarkItDown` Microsoft PDF parser dependencies. It verifies that when binary PDF bytes are passed, the function returns clean text strings without requiring a live external PDF processing service.
- **`test_process_file_upload_txt`**: Tests the generic file upload handler to verify standard `.txt` files are decoded cleanly.
- **`test_process_file_upload_csv`**: Tests the generic file upload handler to ensure CSV/Excel byte streams are properly routed and parsed into structured Pandas DataFrames.
- **`test_process_file_upload_empty_csv`**: Asserts that passing a 0-byte CSV explicitly throws a readable ValueError ("empty CSV file uploaded") instead of returning unhandled Pandas empty data exceptions to the user UI.
