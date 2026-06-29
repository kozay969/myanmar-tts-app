import streamlit as st
from google import genai
from google.genai import types
import wave
import tempfile
import os

# -------------------------
# Page Config
# -------------------------
st.set_page_config(
    page_title="Gemini TTS",
    page_icon="🎤",
    layout="centered"
)

st.title("🎤 Gemini 2.5 Flash Preview TTS")
st.caption("Google AI Studio Text-to-Speech")

# -------------------------
# API KEY
# -------------------------
api_key = st.secrets.get("GEMINI_API_KEY", "")

if not api_key:
    st.error("❌ GEMINI_API_KEY မတွေ့ပါ")
    st.stop()

client = genai.Client(api_key=api_key)

# -------------------------
# Voice List
# -------------------------
voice = st.selectbox(
    "🎙️ Voice",
    [
        "Kore",
        "Aoede",
        "Charon",
        "Fenrir",
        "Puck",
    ]
)

# -------------------------
# Text Input
# -------------------------
text = st.text_area(
    "စာသားထည့်ပါ",
    height=300,
    placeholder="ဒီနေရာမှာ စာသားထည့်ပါ..."
)

# -------------------------
# Generate Button
# -------------------------
generate = st.button(
    "🎤 Generate Voice",
    use_container_width=True
)
# -------------------------
# Generate Audio
# -------------------------
if generate:

    if not text.strip():
        st.warning("စာသားထည့်ပါ။")
        st.stop()

    progress = st.progress(0)

    try:

        progress.progress(20)

        response = client.models.generate_content(
            model="gemini-2.5-flash-preview-tts",
            contents=text,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name=voice
                        )
                    )
                ),
            ),
        )

        progress.progress(70)

        audio_bytes = (
            response.candidates[0]
            .content.parts[0]
            .inline_data.data
        )

        output = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".wav"
        )

        with wave.open(output.name, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(24000)
            wf.writeframes(audio_bytes)

        progress.progress(100)

        st.success("✅ အသံထုတ်ပြီးပါပြီ")

        st.audio(output.name)

        with open(output.name, "rb") as f:

            st.download_button(
                "⬇️ Download WAV",
                data=f,
                file_name="gemini_tts.wav",
                mime="audio/wav",
                use_container_width=True,
            )

    except Exception as e:
        st.error(f"❌ Error : {e}")
