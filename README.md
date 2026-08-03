# Generative AI and ML Capstone Project: Translation and TTS

## Overview
The goal of this capstone project is to develop a web application using Streamlit that enables users to translate text into various languages, convert the translated text into speech, and download the resulting audio file. The project leverages **Google's Gemini API** for translation and **Google Text-to-Speech (gTTS)** for speech synthesis.

## Project Description
This project aims to develop a system that translates text into various languages and converts the translated text into speech. The system is designed to be user-friendly and interactive, allowing users to either enter text directly, use their microphone, or upload a file in various formats (PDF, TXT, Excel, CSV). The text is then translated into a language selected by the user from a dropdown menu, utilizing the Gemini API for accurate and context-aware translations. 

Features included:
- **Direct Text Input:** Translate text instantly.
- **Microphone Input:** Record audio, which is then transcribed and translated directly using Gemini.
- **File Upload:** Upload PDF, TXT, CSV, or Excel files for automatic translation.
- **Text-to-Speech:** Generates an MP3 audio file of the translated text for playback and download.
- **Guardrails:** Prevents prompt injection and handles malicious inputs.

## Installation

This project utilizes Python 3.12. Follow these steps to set up the project locally:

1. **Clone or Download the Repository:**
   Extract the files to your local directory.
   
2. **Set up a Virtual Environment:**
   It is highly recommended to use a virtual environment to manage dependencies.
   ```bash
   python -m venv .venv
   ```

3. **Activate the Virtual Environment:**
   - On **Windows**:
     ```bash
     .venv\Scripts\activate
     ```
   - On **macOS/Linux**:
     ```bash
     source .venv/bin/activate
     ```

4. **Install Dependencies:**
   Install the required packages using `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

## How to Run the App

1. Make sure your virtual environment is activated.
2. Run the Streamlit application:
   ```bash
   streamlit run app.py
   ```
3. The application will open in your default web browser (usually at `http://localhost:8501`).
4. **Important**: You must provide your own **Google Gemini API Key** in the sidebar configuration to perform translations.

## Running Tests

The project includes a suite of unit tests built with `pytest` to ensure core functionalities work as expected without needing to hit the live Gemini API. 

The available test suites cover:
- `test_gemini_client.py`: Verifies the translation guardrails and JSON parsing of the Gemini API wrapper.
- `test_tts_engine.py`: Verifies the generation of MP3 audio using the gTTS engine.
- `test_file_processor.py`: Verifies PDF text extraction and Pandas DataFrame cell-by-cell translation for CSV/Excel uploads.

To run all available tests, execute the following command in the project root:
```bash
# Ensure PYTHONPATH is set to the current directory so modules can be imported
# On Windows (PowerShell):
$env:PYTHONPATH="."
pytest tests/

# On macOS/Linux:
PYTHONPATH="." pytest tests/
```
