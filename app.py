import streamlit as st
import wave
import zipfile
import io
import os
from google import genai
from google.genai import types

st.set_page_config(page_title="Gemini TTS Pro", layout="centered")
st.title("🎤 Gemini 2.5 Flash TTS Pro")

api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("❌ GEMINI_API_KEY မတွေ့ပါ")
    st.stop()

client = genai.Client(api_key=api_key)

# Text Splitter Function
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

# Voice Selection
voice = st.selectbox("🎙️ Voice", ["Kore", "Aoede", "Charon", "Fenrir", "Puck"])
text_input = st.text_area("စာသားထည့်ပါ", height=200)

if st.button("🚀 Generate & ZIP"):
    if not text_input.strip():
        st.warning("စာသားထည့်ပေးပါ")
    else:
        chunks = split_text(text_input)
        progress_bar = st.progress(0)
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w') as zf:
            for i, chunk in enumerate(chunks):
                st.write(f"Processing part {i+1}/{len(chunks)}...")
                
                # API Call
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
                
                # Write to ZIP
                filename = f"audio_part_{i+1}.wav"
                zf.writestr(filename, audio_data)
                
                progress_bar.progress((i + 1) / len(chunks))
        
        st.success("✅ အားလုံးပြီးဆုံးပါပြီ!")
        st.download_button("📥 Download ZIP", zip_buffer.getvalue(), "gemini_tts.zip", "application/zip")
