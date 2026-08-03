import streamlit as st
import pandas as pd
import io
import os
from streamlit_mic_recorder import mic_recorder

from modules.gemini_client import GeminiClient
from modules.tts_engine import TTSEngine
from modules.file_processor import process_file_upload

from dotenv import load_dotenv
import json

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

st.title("Globetrotter: Translation & TTS App")
st.markdown("Translate text, documents, or voice into multiple languages and generate speech.")

# Inject CSS for Devanagari (Hindi) and other scripts support
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@400;700&display=swap');
    
    body, p, div, span, textarea, input, select {
        font-family: "Source Sans Pro", "Noto Sans Devanagari", sans-serif !important;
    }
</style>
""", unsafe_allow_html=True)

if not st.session_state.gemini_client:
    st.warning("Please enter your Gemini API Key in the sidebar to proceed.")
    st.stop()

# Helper function
def perform_translation(text):
    with st.spinner("Translating..."):
        result = st.session_state.gemini_client.translate_text(text, target_language)
    return result

def perform_tts(text):
    with st.spinner("Generating Audio..."):
        # Map target language to language code for gTTS
        lang_code = LANGUAGES.get(target_language, "en")
        try:
            audio_path = tts_engine.generate_audio(text, lang=lang_code, engine=tts_engine_choice)
            st.audio(audio_path, format="audio/mp3")
            with open(audio_path, "rb") as file:
                st.download_button(
                    label="Download Audio",
                    data=file,
                    file_name="translated_audio.mp3",
                    mime="audio/mp3"
                )
        except Exception as e:
            st.error(f"TTS Error: {e}")

tab1, tab2, tab3 = st.tabs(["Text", "Microphone", "Document Upload"])

with tab1:
    source_text = st.text_area("Enter text to translate:")
    if st.button("Translate Text"):
        if source_text.strip():
            res = perform_translation(source_text)
            st.success(f"**Detected Language:** {res.get('detected_language', 'Unknown')}")
            st.write(f"**Translation:**\n\n{res.get('translation', '')}")
            
            if "Error" not in res.get('translation', ''):
                perform_tts(res['translation'])
        else:
            st.warning("Please enter text to translate.")

with tab2:
    st.write("Record your voice to translate.")
    audio = mic_recorder(start_prompt="Start Recording", stop_prompt="Stop Recording", key='recorder')
    
    if audio:
        st.audio(audio['bytes'])
        
        with st.spinner("Transcribing and Translating Voice..."):
            # webm or wav depending on browser
            mime_type = "audio/webm" if "webm" in audio.get('format', 'webm') else "audio/wav"
            
            res = st.session_state.gemini_client.transcribe_and_translate_audio(
                audio['bytes'], mime_type, target_language
            )
            
            st.write(f"**Transcribed Text:** {res.get('transcription', '')}")
            st.success(f"**Detected Language:** {res.get('detected_language', 'Unknown')}")
            st.write(f"**Translation:**\n\n{res.get('translation', '')}")
            
            if "Error" not in res.get('translation', ''):
                perform_tts(res['translation'])

with tab3:
    uploaded_file = st.file_uploader("Upload Document", type=['txt', 'pdf', 'csv', 'xlsx'])
    
    if uploaded_file is not None:
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        if st.button("Process Document"):
            def translate_wrapper(text, lang):
                res = st.session_state.gemini_client.translate_text(text, lang)
                return res.get('translation', text)
                
            with st.spinner("Processing document..."):
                try:
                    result, output_type = process_file_upload(
                        uploaded_file, 
                        file_extension, 
                        translator_func=translate_wrapper, 
                        target_language=target_language
                    )
                    
                    if output_type == 'text':
                        # Translate the whole extracted text
                        res = perform_translation(result)
                        st.success(f"**Detected Language:** {res.get('detected_language', 'Unknown')}")
                        st.text_area("Translated Content", res.get('translation', ''), height=300)
                        
                        st.download_button("Download Translated Text", data=res.get('translation', ''), file_name=f"translated_{uploaded_file.name}.txt")
                        
                        if "Error" not in res.get('translation', ''):
                            perform_tts(res['translation'])
                            
                    elif output_type == 'dataframe':
                        st.write("Translated Data:")
                        st.dataframe(result)
                        
                        # Convert df to csv for download
                        csv = result.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="Download Translated CSV",
                            data=csv,
                            file_name=f"translated_{uploaded_file.name.replace('.xlsx', '.csv')}",
                            mime="text/csv",
                        )
                except Exception as e:
                    st.error(f"Error processing file: {e}")
