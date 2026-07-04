import streamlit as st
import edge_tts
import tempfile
import os
import asyncio
import re

st.set_page_config(page_title="Myanmar TTS", page_icon="🔊")

st.title("🔊 Myanmar TTS - Card မလို")
st.caption("Edge-TTS နဲ့ အလကား 100%")

voice_options = {
    "မြန်မာ - Nilar (မိန်းကလေး)": "my-MM-NilarNeural",
    "မြန်မာ - Thiha (ယောက်ျားလေး)": "my-MM-ThihaNeural",
}

selected_voice_name = st.selectbox("🎤 အသံရွေးပါ", list(voice_options.keys()))
selected_voice = voice_options[selected_voice_name]

# Style Preset
style = st.selectbox("🎭 အသံစတိုင်", [
    "သာမန်",
    "ပျော်ရွှင်စရာ - rate:+8%, pitch:+4Hz", 
    "ဝမ်းနည်းစရာ - rate:-25%, pitch:-4Hz",
    "ဒေါသထွက်စရာ - rate:+12%, pitch:+3Hz",
    "သတင်းကြေညာသူ - rate:-5%, pitch:-2Hz"
])

style_map = {
    "သာမန်": {"rate": "0%", "pitch": "0Hz"},
    "ပျော်ရွှင်စရာ - rate:+8%, pitch:+4Hz": {"rate": "+8%", "pitch": "+4Hz"},
    "ဝမ်းနည်းစရာ - rate:-25%, pitch:-4Hz": {"rate": "-25%", "pitch": "-4Hz"},
    "ဒေါသထွက်စရာ - rate:+12%, pitch:+3Hz": {"rate": "+12%", "pitch": "+3Hz"},
    "သတင်းကြေညာသူ - rate:-5%, pitch:-2Hz": {"rate": "-5%", "pitch": "-2Hz"},
}

text_input = st.text_area("📝 စာသားထည့်ပါ:", height=200, placeholder="မင်္ဂလာပါ။ ဒီနေ့ ရာသီဥတု ကောင်းပါတယ်။")

async def generate_audio(text, voice, rate, pitch):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
        output_file = tmp_file.name
    
    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    await communicate.save(output_file)
    
    with open(output_file, "rb") as f:
        audio_bytes = f.read()
    os.unlink(output_file)
    return audio_bytes

if st.button("🚀 အသံထုတ်မယ်", use_container_width=True, type="primary"):
    if not text_input.strip():
        st.error("⚠️ စာသားအရင်ထည့်ပါ!")
    else:
        with st.spinner('🎤 အသံထုတ်နေတယ်...'):
            try:
                cfg = style_map[style]
                audio_bytes = asyncio.run(generate_audio(
                    text_input, selected_voice, cfg["rate"], cfg["pitch"]
                ))
                
                st.success("✅ ရပြီ!")
                st.audio(audio_bytes, format="audio/mp3")
                st.download_button(
                    "📥 MP3 Download",
                    audio_bytes,
                    "myanmar_tts.mp3",
                    "audio/mp3",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"❌ Error: {e}")

st.caption("✅ Visa Card မလို | ✅ API Key မလို | ✅ Unlimited အလကား")
