# Globetrotter: Selective Translation & TTS
**Generative AI and ML Capstone Project**  
*Edureka & Illinois Institute of Technology*

---

## 1. Overview & Project Goals

The **Globetrotter** application is a production-grade, interactive web system built with **Streamlit** that enables users to translate text across multiple languages, synthesize the translated text into spoken audio, and download the resulting MP3 audio file. 

The system leverages **Google's Gemini 3.5 Flash API** for context-aware language translation, audio transcription, and layout-preserving PDF extraction, paired with **Google Text-to-Speech (gTTS)** for speech synthesis. The backend is engineered according to **Clean Hexagonal Architecture**, **Zero Hardcoding**, **Zero Absolute Paths**, and **Fail-Fast Configuration** standards.

---

## 2. System Architecture

The application is structured into four decoupled layers ensuring single responsibility and stateless cloud execution:

![Globetrotter Architecture](architecture.png)

> **Excalidraw Editable Diagram:** The vector source file is provided in `architecture.excalidraw`. Full architectural specifications are detailed in `ARCHITECTURE.md`.

### Architectural Breakdown:
1. **Presentation Layer (`app.py`):** User interface built with Streamlit. Manages UI layout, session state, input widgets, audio playback, and download actions. Contains zero business logic or direct database/SDK calls.
2. **Domain Service Layer (`modules/file_processor.py`):** Encapsulates format routing (PDF, TXT, CSV, Excel), DataFrame cell-by-cell translation, and text sanitization. Includes security guardrails to block prompt injection attacks.
3. **Hexagonal Adapters Layer (`modules/gemini_client.py` & `modules/tts_engine.py`):** Isolates third-party SDK boundaries behind clean domain classes. `GeminiClient` enforces structured JSON outputs and handles multimodal vision. `TTSEngine` handles text sanitization (stripping Markdown tags) and generates MP3 audio streams in-memory.
4. **External Cloud Infrastructure:** Google Gemini 3.5 Flash API, Google Text-to-Speech public endpoint, and Streamlit Community Cloud hosting.

---

## 3. Core Features

- **Direct Text Input & Selective Processing:** Type or paste text instantly into the workspace, or selectively copy extracted document sections.
- **Multi-Format Document Upload:** Seamless ingestion of **PDF**, **TXT**, **CSV**, and **Excel (`.xlsx`, `.xls`)** files.
- **Multimodal Document Understanding:** PDFs are processed via Gemini's multimodal vision endpoint, perfectly preserving Markdown headers, lists, and tabular formatting.
- **Voice Recording & Transcription:** Built-in microphone audio recorder capturing speech directly in the browser, transcribed via Gemini.
- **Context-Aware Translation & Language Detection:** Automatically identifies source languages and returns accurate, culturally coherent translations into 13+ languages.
- **In-Memory Audio Generation (Stateless TTS):** Synthesizes high-fidelity MP3 audio streams entirely within memory buffers (`io.BytesIO`), bypassing ephemeral local disk restrictions on serverless platforms.
- **Security Guardrails:** Built-in prompt injection filters intercepting adversarial instructions before submission to the LLM.

---

## 4. Installation & Local Setup

### Prerequisites
- Python 3.12 (specified in `.python-version`)

### Installation Steps

1. **Set up a Virtual Environment:**
   - **Windows:**
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\activate
     ```
   - **macOS / Linux:**
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## 5. Obtaining & Configuring the Gemini API Key

To use translation, transcription, and PDF extraction:

1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Sign in with your Google account and click **"Create API Key"**.
3. Copy the generated API key.
4. Supply the key via either:
   - **Option A (Environment Variable):** Create a `.env` file in the project root:
     ```env
     GEMINI_API_KEY="your_api_key_here"
     ```
   - **Option B (Web UI):** Enter the key directly into the sidebar password field in the running web application.

---

## 6. Considerations, Limitations, and Challenges Faced

### 1. Considerations
- **Stateless Cloud Execution:** Serverless environments (Streamlit Cloud, Heroku) feature ephemeral filesystems where writing temporary `.mp3` files causes I/O bottlenecks and race conditions. The system was designed to stream audio strictly in-memory via `io.BytesIO`.
- **Text Sanitization for Speech:** Direct conversion of rich Markdown into audio leads to the TTS engine vocalizing formatting characters (`hashtag`, `asterisk`, `link`). An automated sanitization filter was introduced to strip HTML and Markdown syntax before synthesis.
- **Fail-Fast Operational Reliability:** To prevent silent failures in production, the application enforces dynamic path resolution (`Path(__file__).resolve().parent`) and strict dictionary lookups that raise explicit errors immediately if configuration keys are missing.
- **Prompt Injection Defense:** LLM inputs are evaluated through heuristic guardrails to block prompt-hijacking attempts before querying external APIs.

### 2. Limitations
- **gTTS Endpoint Constraints:** `gTTS` relies on Google's public translation TTS interface. While producing natural pronunciation, it does not support fine-grained pitch, timbre, or speaking-speed modulation.
- **Free-Tier API Quotas:** Google Gemini API free-tier quotas enforce requests-per-minute (RPM) limits. High-frequency automated calls may trigger rate limits.
- **Very Large Tabular Files:** Extremely large CSV or Excel files (thousands of rows) require batch chunking to avoid exceeding context window limits during cell-by-cell translation.

### 3. Challenges Faced & Solutions
- **Challenge 1: Preserving PDF Layout & Tables**  
  *Issue:* Standard open-source PDF extractors strip visual whitespace, collapsing tables and headers into unintelligible text blocks.  
  *Solution:* Integrated Gemini's multimodal vision endpoint, passing document bytes directly to generate clean, structured Markdown that mirrors the original visual hierarchy.
- **Challenge 2: TTS Vocalizing Formatting Syntax**  
  *Issue:* When translating structured documents, the generated output contains Markdown syntax (e.g. `### Heading`, `**bold**`, `| col |`). gTTS pronounced these characters verbatim.  
  *Solution:* Implemented `TTSEngine.strip_markdown()`, using `markdown` and `BeautifulSoup` to strip formatting tags while preserving the underlying phonetic text.
- **Challenge 3: Multi-Script Font Rendering in Streamlit**  
  *Issue:* Non-Latin alphabets (particularly Hindi / Devanagari script) suffered glyph truncation and uneven line spacing in standard browser text areas.  
  *Solution:* Injected custom CSS loading the Google Font `Noto Sans Devanagari` globally to ensure clean typography across all supported languages.

---

## 7. Automated Testing & Verification

The project includes an automated test suite with **17 unit and integration tests** built with `pytest`:

```bash
# Run tests with coverage
.\.venv\Scripts\python -m pytest --cov=modules tests/
```

| Module | Statements | Missing | Coverage | Key Scenarios Tested |
|---|---|---|---|---|
| `modules/__init__.py` | 0 | 0 | 100% | Package initialization |
| `modules/file_processor.py` | 54 | 22 | 59% | CSV/Excel parsing, DataFrame string translation, empty file guards |
| `modules/gemini_client.py` | 59 | 14 | 76% | Prompt injection interception, JSON parsing errors, live translation |
| `modules/tts_engine.py` | 38 | 8 | 79% | Markdown stripping, empty input rejection, live MP3 ID3 header validation |
| **Total** | **151** | **44** | **71%** | **17 passed** |

---

## 8. Deployment Guide (Streamlit Community Cloud)

1. Push your repository to GitHub.
2. Visit [share.streamlit.io](https://share.streamlit.io/) and authenticate with your GitHub account.
3. Click **"New app"**, select your repository, branch (`main`), and set the main file path to `app.py`.
4. In **"Advanced settings..."**, optionally add `GEMINI_API_KEY` under Secrets.
5. Click **"Deploy"**. The app deploys seamlessly due to its stateless in-memory architecture.

---

## 9. Application Screenshots Walkthrough

### 1. Application Landing & Configuration
![capstone-001.png](screenshots/capstone-001.png)
*Initial view displaying the configuration sidebar, target language selector, and input options.*

### 2. Input Workspace
![capstone-002.png](screenshots/capstone-002.png)
*Text entered into the processing area ready for selective translation.*

### 3. Document Extraction & Viewer
![capstone-003.png](screenshots/capstone-003.png)
*Extracted document text rendered within the interactive viewer container.*

### 4. Workspace Selection
![capstone-004.png](screenshots/capstone-004.png)
*Selecting specific text portions for processing.*

### 5. Translation & Language Detection
![capstone-005.png](screenshots/capstone-005.png)
*Gemini detects the source language (English) and outputs context-aware translation in the target language.*

### 6. Speech Synthesis & Audio Player
![capstone-006.png](screenshots/capstone-006.png)
*In-memory audio generated via gTTS with integrated player and MP3 download button.*

### 7. Complete Dashboard View
![capstone-007.png](screenshots/capstone-007.png)
*Full-page dashboard showing complete end-to-end workflow.*
