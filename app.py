import streamlit as st
import edge_tts
import tempfile
import os
import asyncio

st.set_page_config(page_title="Myanmar TTS - High Quality", page_icon="🔊", layout="centered")

st.markdown("""
<style>
    .stTextArea textarea { font-size: 18px !important; min-height: 150px !important; }
    .stButton button { width: 100% !important; padding: 15px !important; font-size: 18px !important; border-radius: 10px !important; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important; color: white !important; font-weight: bold !important; }
    .stSelectbox { font-size: 16px !important; }
    @media (max-width: 768px) { .stApp { padding: 10px !important; } }
</style>
""", unsafe_allow_html=True)

st.title("🔊 Myanmar TTS - High Quality")
st.caption("အရည်အသွေးမြင့် Edge TTS ကို အသုံးပြုထားသည်")

# Voice options
voice_options = {
    "မြန်မာ - Nilar (အမျိုးသမီး)": "my-MM-NilarNeural",
    "မြန်မာ - Thiha (အမျိုးသား)": "my-MM-ThihaNeural",
    "US English - Jenny (Neural)": "en-US-JennyNeural",
    "US English - Guy (Neural)": "en-US-GuyNeural",
    "UK English - Sonia (Neural)": "en-GB-SoniaNeural",
}

# ===== Voice Selection =====
selected_voice_name = st.selectbox(
    "🎤 Select Voice / အသံရွေးချယ်ပါ",
    list(voice_options.keys())
)
selected_voice = voice_options[selected_voice_name]

# ===== Quality Selection (အရည်အသွေး ၃ မျိုး) =====
quality_options = {
    "📀 Standard (48 kbps) - File size အသေး": "audio-24khz-48kbitrate-mono-mp3",
    "💿 High (96 kbps) - File size အလယ်": "audio-24khz-96kbitrate-mono-mp3",
    "🎵 Premium (160 kbps) - File size အကြီး": "audio-24khz-160kbitrate-mono-mp3",
}

selected_quality_name = st.selectbox(
    "🔊 Audio Quality / အသံအရည်အသွေး",
    list(quality_options.keys())
)
selected_quality = quality_options[selected_quality_name]

# ===== Settings (Rate & Pitch) =====
col1, col2 = st.columns(2)
with col1:
    rate = st.slider("🔊 Speech Speed", -50, 50, -5, 5)
    rate_str = f"{rate:+d}%"
with col2:
    pitch = st.slider("🎵 Pitch", -12, 12, 0, 1)
    pitch_str = f"{pitch:+d}Hz"

# Text input
text_input = st.text_area(
    "📝 Enter text", 
    height=150, 
    placeholder="Type your text here..."
)

def generate_audio(text, voice, rate, pitch, quality):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            output_file = tmp_file.name
        
        async def run_tts():
            communicate = edge_tts.Communicate(
                text, 
                voice, 
                rate=rate, 
                pitch=pitch,
                output_format=quality  # အရည်အသွေးထည့်ပါ
            )
            await communicate.save(output_file)
        
        asyncio.run(run_tts())
        
        with open(output_file, "rb") as f:
            audio_bytes = f.read()
        os.unlink(output_file)
        return audio_bytes, None
    except Exception as e:
        return None, str(e)

if st.button("🚀 Generate High Quality Speech", use_container_width=True):
    if not text_input.strip():
        st.error("⚠️ Please enter some text!")
    else:
        with st.spinner("🎤 Generating high quality audio..."):
            audio_bytes, error = generate_audio(
                text_input, selected_voice, rate_str, pitch_str, selected_quality
            )
            
            if error:
                st.error(f"❌ Error: {error}")
            else:
                st.audio(audio_bytes, format="audio/mp3")
                st.download_button(
                    label="📥 Download MP3",
                    data=audio_bytes,
                    file_name="tts_output.mp3",
                    mime="audio/mp3",
                    use_container_width=True
                )
                st.success(f"✅ Audio generated successfully! (Quality: {selected_quality_name})")

st.divider()
st.caption("💡 Powered by Microsoft Edge TTS | Free to use")
