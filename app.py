import streamlit as st
from google import genai
from google.genai import types
import wave
# --------------------
# Page
# --------------------
st.set_page_config(
    page_title="Gemini TTS",
    page_icon="🎤",
    layout="centered",
)

st.title("🎤 Gemini 2.5 Flash Preview TTS")

# --------------------
# API Key
# --------------------
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("❌ GEMINI_API_KEY မတွေ့ပါ")
    st.stop()

client = genai.Client(api_key=api_key)

# --------------------
# Voices
# --------------------
voices = [
    "Kore",
    "Aoede",
    "Charon",
    "Fenrir",
    "Puck",
]

voice = st.selectbox(
    "🎙️ Voice ရွေးပါ",
    voices,
)

# --------------------
# Text
# --------------------
text = st.text_area(
    "စာသားထည့်ပါ",
    height=250,
    placeholder="ဒီနေရာမှာ စာသားထည့်ပါ..."
)

generate = st.button(
    "🎤 Generate Voice",
    use_container_width=True,
)
from google.genai import types
import wave

def save_wave(filename, pcm):
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(24000)
        wf.writeframes(pcm)

if generate:

    if not text.strip():
        st.warning("စာသားထည့်ပါ")
        st.stop()

    with st.spinner("Gemini အသံထုတ်နေပါတယ်..."):

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

        audio = response.candidates[0].content.parts[0].inline_data.data

        save_wave("output.wav", audio)

        st.success("✅ အသံထုတ်ပြီးပါပြီ")

        st.audio("output.wav")

        with open("output.wav", "rb") as f:
            st.download_button(
                "⬇️ Download WAV",
                f,
                file_name="gemini_tts.wav",
                mime="audio/wav",
            )
