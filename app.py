import streamlit as st
import edge_tts
import tempfile
import os
import asyncio
import re

st.set_page_config(page_title="Myanmar TTS", page_icon="🔊", layout="centered")

st.markdown("""
<style>
    .stTextArea textarea { font-size: 18px !important; min-height: 150px !important; }
    .stButton button { width: 100% !important; padding: 15px !important; font-size: 18px !important; border-radius: 10px !important; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important; color: white !important; font-weight: bold !important; }
    .stSelectbox { font-size: 16px !important; }
    @media (max-width: 768px) { .stApp { padding: 10px !important; } }
</style>
""", unsafe_allow_html=True)

st.title("🔊 Myanmar TTS")
st.caption("SSML Tag များကို အလိုအလျောက်ဖယ်ရှားပြီး အသံပြောင်းပေးသည်")

# Voice options
voice_options = {
    "မြန်မာ - Nilar (အမျိုးသမီး)": "my-MM-NilarNeural",
    "မြန်မာ - Thiha (အမျိုးသား)": "my-MM-ThihaNeural",
    "US English - Jenny": "en-US-JennyNeural",
    "US English - Guy": "en-US-GuyNeural",
    "UK English - Sonia": "en-GB-SoniaNeural",
}

selected_voice_name = st.selectbox("🎤 Select Voice", list(voice_options.keys()))
selected_voice = voice_options[selected_voice_name]

# Quality
quality_options = {
    "📀 Standard (48 kbps)": "Standard",
    "💿 High (96 kbps)": "High",
    "🎵 Premium (160 kbps)": "Premium",
}
selected_quality_name = st.selectbox("🔊 Audio Quality", list(quality_options.keys()))

col1, col2 = st.columns(2)
with col1:
    rate = st.slider("🔊 Speed", -50, 50, -5)
    rate_str = f"{rate:+d}%"
with col2:
    pitch = st.slider("🎵 Pitch", -12, 12, 0)
    pitch_str = f"{pitch:+d}Hz"

# ===== SSML Tag ဖယ်ရှားပေးမယ့် Function =====
def remove_ssml_tags(text):
    """SSML Tag အားလုံးကို ဖယ်ရှားပြီး စာသားသက်သက်ကိုပဲ ထုတ်ပေးမယ်"""
    # XML/SGML Tag တွေကို ဖယ်ရှားမယ်
    # <...> ပုံစံအားလုံးကို ရှာပြီး ဖယ်မယ်
    cleaned = re.sub(r'<[^>]+>', '', text)
    # နေရာလွတ်တွေကို သန့်ရှင်းအောင်လုပ်မယ်
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

# ===== Text Input =====
text_input = st.text_area(
    "📝 Enter text (SSML Tags ပါလည်းရပါတယ်)", 
    height=150,
    placeholder="""
ဥပမာ:
<speak>
    <prosody rate="slow">
        မင်္ဂလာပါ။ ဒီနေ့ ရာသီဥတု ကောင်းပါတယ်။
    </prosody>
</speak>
"""
)

# ===== SSML ဖယ်ရှားပြီး စာသားကို ပြသမယ် =====
if text_input:
    cleaned_text = remove_ssml_tags(text_input)
    if cleaned_text != text_input:
        st.info(f"📄 SSML Tag များကိုဖယ်ရှားပြီး စာသားသက်သက်: **{cleaned_text[:100]}...**")

def generate_audio(text, voice, rate, pitch):
    try:
        # SSML Tag တွေကို ဖယ်ရှားပါ
        clean_text = remove_ssml_tags(text)
        
        if not clean_text:
            return None, "စာသားမရှိပါ"
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            output_file = tmp_file.name
        
        async def run_tts():
            communicate = edge_tts.Communicate(
                clean_text, 
                voice,
                rate=rate,
                pitch=pitch
            )
            await communicate.save(output_file)
        
        asyncio.run(run_tts())
        
        with open(output_file, "rb") as f:
            audio_bytes = f.read()
        os.unlink(output_file)
        return audio_bytes, None
    except Exception as e:
        return None, str(e)

if st.button("🚀 Generate Speech", use_container_width=True):
    if not text_input.strip():
        st.error("⚠️ Please enter some text!")
    else:
        with st.spinner("🎤 Generating..."):
            audio_bytes, error = generate_audio(
                text_input, selected_voice, rate_str, pitch_str
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
                st.success(f"✅ Done! (Quality: {selected_quality_name})")

st.divider()
st.caption("💡 SSML Tag များကို အလိုအလျောက်ဖယ်ရှားပြီး စာသားသက်သက်ကိုသာ အသံပြောင်းပေးသည်")
