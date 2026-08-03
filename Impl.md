# Edureka Capstone: Translation & TTS App

## Goal Description
Develop a web application using Streamlit that enables users to translate text into various languages, convert the translated text into speech, and download the resulting audio file. The project leverages Google's **Gemini API** for translation and Text-to-Speech (and optionally gTTS), fulfilling all requirements of the provided Capstone assignment while adding advanced enhancements.

Directory: `C:\Data\work\Edureka-Capstone-Translation`

## Core Features & Enhancements

### 1. Multi-Modal Input
*   **Direct Text Entry:** Standard text area for quick translations.
*   **Voice Input (Mic Feature):** Integrating a Streamlit microphone component (`streamlit-mic-recorder`) to capture voice, transcribing it using Gemini or standard STT, and then translating it.
*   **Document Uploads:** Support for PDF, TXT, CSV, and Excel.
    *   *PDF/TXT:* Extract text, translate, and allow downloading the translated text.
    *   *CSV/Excel:* Parse with `pandas`, iterate through rows/cells, translate text content, and construct a new translated CSV/Excel file for download.

### 2. Intelligent Translation & Language Handling
*   **Language Detection:** The app will automatically detect the source language of the input text using Gemini (e.g., via a structured JSON response returning `{"detected_language": "...", "translation": "..."}`).
*   **Target Languages:** A curated dropdown list of languages supported by both Gemini and the TTS engine (e.g., English, Spanish, French, German, Italian, Portuguese, Dutch, Russian, Mandarin Chinese, Japanese, Korean, Hindi, Arabic).
*   **Guardrails & Security:** A pre-processing step will check for Prompt Injections, malicious content, or attempts to extract system instructions. If flagged, the app will politely reject the input.

### 3. Advanced Text-to-Speech (TTS)
*   **Google Text-to-Speech (gTTS):** The baseline requirement from the assignment to ensure grading criteria are met.
*   **Gemini / Google Streaming TTS:** We will integrate Google's advanced TTS (e.g., Gemini Flash audio generation or Google Cloud TTS) for a more natural, expressive voice, selectable by the user.

### 4. User Experience & Configuration
*   **API Key Management:** Users can securely input their Gemini API Key directly in the Streamlit UI (sidebar). If omitted, the app falls back to `.env` variables or Streamlit secrets.
*   **Responsive UI:** Clean separation of input, processing status (spinners/progress bars), and output. 
    *   *Text/PDF:* Output displayed as standard text/markdown.
    *   *CSV/Excel:* Output displayed interactively using `st.dataframe()` or `st.data_editor()` so the user can see the tabular data before downloading.

## Proposed Architecture & File Structure

#### `app.py`
The main Streamlit application entry point. Handles UI layout, session state, API key injection, and orchestrates the modules. Displays Text and Dataframes conditionally based on the input type.

#### `modules/file_processor.py`
Logic to handle document parsing and reconstruction.
*   `pdfplumber` or `PyPDF2` for PDFs.
*   `pandas` for CSV and Excel (reading cell-by-cell or row-by-row for translation).

#### `modules/gemini_client.py`
Wrapper for the Gemini API.
*   Handles system prompts.
*   Implements the **Guardrails** check before translation.
*   Returns structured JSON for detected language and translated text.

#### `modules/tts_engine.py`
Handles speech synthesis.
*   Implements `gTTS` for baseline compatibility.
*   Integrates Google/Gemini streaming TTS as the advanced option.

#### `tests/`
Pytest suite for validating translation (gemini_client) and speech generation (tts_engine) independently.

#### `requirements.txt`
Dependencies: `streamlit`, `google-generativeai`, `gTTS`, `pandas`, `PyPDF2`, `openpyxl`, `streamlit-mic-recorder`, `pytest`, `pytest-asyncio`.

---

## Task Checklist (Implementation Plan)
- [x] Setup basic project structure and requirements (created venv and `requirements.txt`)
- [ ] Create `pytest` tests for the `gemini_client` and `tts_engine`
- [ ] Implement `modules/gemini_client.py` (Translation & Guardrails)
- [ ] Implement `modules/tts_engine.py` (gTTS and Google TTS support)
- [ ] Create `pytest` tests for `file_processor`
- [ ] Implement `modules/file_processor.py` (Text, PDF, CSV, Excel parsing)
- [ ] Implement UI Mockup in `app.py`
  - [ ] Sidebar (API Key, Language selection)
  - [ ] Main area (Input methods: Text, Mic, File)
  - [ ] Display logic (Markdown for Text/PDF, Dataframe for CSV/Excel)
- [ ] Integrate modules into Streamlit UI and test end-to-end
- [ ] Final review and bug fixes
