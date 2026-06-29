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
