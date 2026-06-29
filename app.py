import streamlit as st
from google import genai

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
