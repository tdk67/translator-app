import streamlit as st
import pandas as pd
import io
import os
import json
from bs4 import BeautifulSoup
import markdown
from streamlit_mic_recorder import mic_recorder

from modules.gemini_client import GeminiClient
from modules.tts_engine import TTSEngine
from modules.file_processor import process_file_upload

from dotenv import load_dotenv

# Load env variables
load_dotenv()

# Load Config
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

gemini_model_name = config.get("gemini", {}).get("model_name", "gemini-3.5-flash")
LANGUAGES = config.get("languages", {})
TTS_ENGINES = config.get("tts", {}).get("engines", ["gTTS"])

# Setup page
st.set_page_config(page_title="Translate & TTS with Gemini", layout="wide")

# Sidebar for Config
st.sidebar.title("Configuration")
env_api_key = os.getenv("GEMINI_API_KEY", "")
api_key = st.sidebar.text_input("Gemini API Key", type="password", value=env_api_key, help="Enter your Google Gemini API Key or set GEMINI_API_KEY in .env")

target_language = st.sidebar.selectbox("Target Language", list(LANGUAGES.keys()))
tts_engine_choice = st.sidebar.selectbox("TTS Engine", TTS_ENGINES)

if "gemini_client" not in st.session_state:
    st.session_state.gemini_client = None

if api_key:
    st.session_state.gemini_client = GeminiClient(api_key=api_key, model_name=gemini_model_name)

tts_engine = TTSEngine()

st.title("Globetrotter: Selective Translation & TTS")
st.markdown("Extract text from documents or voice, select the part you need, and translate or generate speech.")

# Inject CSS for Devanagari (Hindi) and other scripts support without breaking buttons
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@400;700&display=swap');
    
    .stTextArea textarea, .stMarkdown p {
        font-family: "Source Sans Pro", "Noto Sans Devanagari", sans-serif;
    }
</style>
""", unsafe_allow_html=True)

if not st.session_state.gemini_client:
    st.warning("Please enter your Gemini API Key in the sidebar to proceed.")
    st.stop()

# --- State Management ---
if "doc_viewer" not in st.session_state:
    st.session_state.doc_viewer = ""
if "translation_result" not in st.session_state:
    st.session_state.translation_result = ""
if "audio_bytes" not in st.session_state:
    st.session_state.audio_bytes = None

# --- Helper Functions ---
def perform_translation(text):
    with st.spinner("Translating..."):
        try:
            res = st.session_state.gemini_client.translate_text(text, target_language)
            st.session_state.translation_result = res['translation']
            return res
        except Exception as e:
            st.error(f"Translation Error: {e}")
            return {}

def perform_tts(text, lang_code=None):
    with st.spinner("Generating Audio..."):
        if not lang_code:
            lang_code = LANGUAGES.get(target_language)
            if not lang_code:
                st.error("Configuration Error: No valid language code found for the selected language.")
                return
            
        # Strip markdown formatting so the TTS engine reads simple text
        try:
            html = markdown.markdown(text)
            clean_text = "".join(BeautifulSoup(html, "html.parser").findAll(string=True))
            if not clean_text.strip():
                clean_text = text
        except Exception:
            clean_text = text # Fallback in case of parsing error
            
        try:
            audio_bytes = tts_engine.generate_audio(clean_text, lang=lang_code, engine=tts_engine_choice)
            st.session_state.audio_bytes = audio_bytes
        except Exception as e:
            st.error(f"TTS Error: {e}")

# --- Unified Input Section ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Upload a Document")
    uploaded_file = st.file_uploader("Upload txt, pdf, csv, xlsx", type=['txt', 'pdf', 'csv', 'xlsx'])
    if st.button("Extract Text from File") and uploaded_file:
        file_extension = uploaded_file.name.split('.')[-1].lower()
        with st.spinner("Extracting..."):
            try:
                # We don't pass translator_func so it just returns the raw text/df
                if file_extension == 'pdf' and st.session_state.gemini_client:
                    result = st.session_state.gemini_client.extract_pdf_markdown(uploaded_file.getvalue())
                    output_type = 'text'
                else:
                    result, output_type = process_file_upload(
                        uploaded_file, 
                        file_extension
                    )
                
                if output_type == 'text':
                    st.session_state.doc_viewer = result
                elif output_type == 'dataframe':
                    # Convert dataframe to string representation (CSV style) for text selection
                    csv_text = result.to_csv(index=False)
                    st.session_state.doc_viewer = csv_text
                st.success("Extraction complete!")
            except ValueError as e:
                st.error(f"Data format error: {e}")
            except Exception as e:
                st.error(f"Unexpected error processing file: {e}")

with col2:
    st.subheader("Or Record Voice")
    st.write("Record audio to be transcribed into the document viewer.")
    audio = mic_recorder(start_prompt="🎙️ Start Recording", stop_prompt="🛑 Stop Recording", key='recorder')
    
    if audio:
        with st.spinner("Transcribing Voice..."):
            mime_type = "audio/webm" if "webm" in audio.get('format', 'webm') else "audio/wav"
            # We use target_language=English as a base for transcription if we just want raw text, 
            # but actually the user can just translate it later. So we extract transcription.
            try:
                res = st.session_state.gemini_client.transcribe_and_translate_audio(
                    audio['bytes'], mime_type, target_language="English" 
                )
                transcription = res.get('transcription', '')
            except Exception as e:
                st.error(f"Transcription Error: {e}")
                transcription = ""
                
            if transcription:
                # Append to document text or replace
                if st.session_state.doc_viewer:
                    new_text = st.session_state.doc_viewer + "\n\n--- Audio Transcription ---\n" + transcription
                else:
                    new_text = transcription
                
                st.session_state.doc_viewer = new_text
                st.success("Transcription appended!")

# --- Document Viewer ---
st.write("---")
st.subheader("2. Document Viewer")
st.info("Copy the specific text you want to process from here, or type directly into the 'Text to Process' box below.")
st.write("**Original Text** (Read-Only/Copy from here)")
if st.session_state.doc_viewer:
    with st.container(height=300, border=True):
        st.markdown(st.session_state.doc_viewer)
else:
    st.write("No document loaded yet. You can type directly into the **Text to Process** box below!")

# --- Processing Box ---
st.write("---")
st.subheader("3. Select & Process")
text_to_process = st.text_area("Text to Process (Paste or type here)", height=150, help="Only the text in this box will be translated or converted to speech.")

col_btn1, col_btn2, col_btn3 = st.columns(3)

if col_btn1.button("🌐 Translate Selected Text"):
    if text_to_process.strip():
        res = perform_translation(text_to_process)
        st.success(f"Detected Source Language: {res.get('detected_language', 'Unknown')}")
    else:
        st.warning("Please paste or type text into the 'Text to Process' box first.")

if col_btn2.button("🔊 Generate Audio (Original)"):
    if text_to_process.strip():
        # Generate audio using English or attempt to auto-detect. 
        # Since we don't know the source lang perfectly without translating, we default to 'en' or a generic one.
        perform_tts(text_to_process, lang_code="en")
    else:
        st.warning("Please paste or type text into the 'Text to Process' box first.")

if col_btn3.button("🔊 Generate Audio (Translated)"):
    if st.session_state.translation_result:
        perform_tts(st.session_state.translation_result)
    else:
        st.warning("Please translate the text first before generating translated audio.")

# --- Results Section ---
if st.session_state.translation_result:
    st.subheader("Translation Result")
    st.text_area("Translated Text", value=st.session_state.translation_result, height=150)
    st.download_button("📥 Download Translated Text", data=st.session_state.translation_result, file_name="translated_text.txt")

if st.session_state.audio_bytes:
    st.subheader("Generated Audio")
    st.audio(st.session_state.audio_bytes, format="audio/mp3")
    st.download_button(
        label="📥 Download Audio File",
        data=st.session_state.audio_bytes,
        file_name="generated_audio.mp3",
        mime="audio/mp3"
    )
