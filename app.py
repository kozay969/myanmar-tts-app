import streamlit as st
import wave
import zipfile
import io
import os
from google import genai
from google.genai import types

# 1. Page Configuration
st.set_page_config(page_title="Gemini TTS Pro", layout="centered")
st.title("🎙️ Gemini 2.5 Flash Preview TTS")
st.write("✅ Auto Split | 📊 Progress Bar | 📁 ZIP Download | 🛡️ Error Handling")

# 2. API Key Check
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("❌ GEMINI_API_KEY မတွေ့ပါ (Secrets တွင် စစ်ဆေးပါ)")
    st.stop()
client = genai.Client(api_key=api_key)

# 3. Helper Functions
def split_text(text, max_chars=1000):
    text = text.strip()
    if len(text) <= max_chars: return [text]
    chunks = []
    while len(text) > max_chars:
        pos = text.rfind("။", 0, max_chars)
        if pos == -1: pos = text.rfind(" ", 0, max_chars)
        if pos == -1: pos = max_chars
        chunks.append(text[:pos + 1].strip())
        text = text[pos + 1:].strip()
    if text: chunks.append(text)
    return chunks

# 4. User Inputs
voice = st.selectbox("🎙️ Voice", ["Kore", "Aoede", "Charon", "Fenrir", "Puck"])
text_input = st.text_area("စာသားများ ထည့်သွင်းပါ:", height=250)

# 5. Generation Logic
if st.button("🚀 Generate & ZIP"):
    if not text_input.strip():
        st.warning("စာသားအနည်းငယ် ထည့်သွင်းပေးပါ။")
    else:
        try:
            chunks = split_text(text_input)
            progress_bar = st.progress(0)
            zip_buffer = io.BytesIO()
            
            with zipfile.ZipFile(zip_buffer, 'w') as zf:
                for i, chunk in enumerate(chunks):
                    # Gemini API Call
                    response = client.models.generate_content(
                        model="gemini-2.5-flash-preview-tts",
                        contents=chunk,
                        config=types.GenerateContentConfig(
                            response_modalities=["AUDIO"],
                            speech_config=types.SpeechConfig(
                                voice_config=types.VoiceConfig(
                                    prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice)
                                )
                            ),
                        ),
                    )
                    
                    audio_data = response.candidates[0].content.parts[0].inline_data.data
                    zf.writestr(f"audio_part_{i+1}.wav", audio_data)
                    progress_bar.progress((i + 1) / len(chunks))
            
            st.success("✅ အားလုံးပြီးဆုံးပါပြီ!")
            st.download_button(
                label="📥 Download ZIP",
                data=zip_buffer.getvalue(),
                file_name="gemini_tts_output.zip",
                mime="application/zip"
            )
        except Exception as e:
            st.error(f"🛡️ Error ဖြစ်ပေါ်ပါသည်: {e}")

