import streamlit as st
import edge_tts
import tempfile
import os
import asyncio
import re

st.set_page_config(page_title="Myanmar TTS - SSML", page_icon="🔊", layout="centered")

st.markdown("""
<style>
    .stTextArea textarea { font-size: 18px !important; min-height: 150px !important; }
    .stButton button { width: 100% !important; padding: 15px !important; font-size: 18px !important; border-radius: 10px !important; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important; color: white !important; font-weight: bold !important; }
    .stSelectbox { font-size: 16px !important; }
    .stInfo { background-color: #f0f2f6 !important; padding: 10px !important; border-radius: 8px !important; }
    @media (max-width: 768px) { .stApp { padding: 10px !important; } }
</style>
""", unsafe_allow_html=True)

st.title("🔊 Myanmar TTS - SSML")
st.caption("SSML အားလုံးကို ထောက်ပံ့ပေးသည် (အလေးပေး၊ ရပ်နား၊ အမြန်နှုန်း၊ အသံအနိမ့်အမြင့်)")

# Voice options
voice_options = {
    "မြန်မာ - Nilar": "my-MM-NilarNeural",
    "မြန်မာ - Thiha": "my-MM-ThihaNeural",
    "US English - Jenny": "en-US-JennyNeural",
    "US English - Guy": "en-US-GuyNeural",
}

selected_voice_name = st.selectbox("🎤 Select Voice", list(voice_options.keys()))
selected_voice = voice_options[selected_voice_name]

# ===== SSML Converter Function =====
def ssml_to_edge_tts(text):
    """
    SSML Tag တွေကို edge-tts နားလည်မယ့် ပုံစံပြောင်းပေးမယ်
    """
    # 1. <emphasis> ကို ပြောင်းမယ် (အလေးပေးပြောချင်ရင် စာလုံးကြီးနဲ့ရေးမယ်)
    def emphasis_replace(match):
        level = match.group(1) or "moderate"
        content = match.group(2)
        if level in ["strong", "moderate"]:
            return content.upper()  # စာလုံးကြီးနဲ့ အလေးပေးပြမယ်
        return content
    
    text = re.sub(r'<emphasis level="([^"]*)">(.*?)</emphasis>', emphasis_replace, text)
    text = re.sub(r'<emphasis>(.*?)</emphasis>', r'\1', text)
    
    # 2. <break> ကို ပြောင်းမယ် (ရပ်နားချင်ရင် အချိန်နဲ့အညီ စာကြောင်းခွဲမယ်)
    def break_replace(match):
        time = match.group(1) or "500ms"
        # ms ကို စက္ကန့်ပြောင်းမယ် (ရပ်နားချိန်အတွက်)
        if "ms" in time:
            ms = int(time.replace("ms", ""))
            if ms >= 500:
                return "\n\n"  # ရပ်နားချိန်ရှည်ရင် စာကြောင်းခွဲမယ်
            else:
                return "\n"    # ရပ်နားချိန်တိုရင် စာကြောင်းခွဲမယ်
        return ""
    
    text = re.sub(r'<break time="([^"]*)"/>', break_replace, text)
    
    # 3. <prosody> ကို ပြောင်းမယ် (rate, pitch, volume)
    def prosody_replace(match):
        rate = match.group(1) or "medium"
        pitch = match.group(2) or "0Hz"
        volume = match.group(3) or "0%"
        content = match.group(4)
        
        # Rate ပြောင်းမယ်
        rate_map = {
            "x-slow": "very slow",
            "slow": "slow",
            "medium": "normal",
            "fast": "fast",
            "x-fast": "very fast"
        }
        rate_text = rate_map.get(rate, "normal")
        
        # Pitch ပြောင်းမယ် (အသံအနိမ့်အမြင့်အတွက်)
        pitch_text = ""
        if pitch and pitch != "0Hz":
            pitch_text = f" (pitch {pitch})"
        
        # Volume ပြောင်းမယ် (အသံကျယ်လောင်မှုအတွက်)
        volume_text = ""
        if volume and volume != "0%":
            volume_text = f" (volume {volume})"
        
        return f"{content} [{rate_text}{pitch_text}{volume_text}]"
    
    text = re.sub(
        r'<prosody(?: rate="([^"]*)")?(?: pitch="([^"]*)")?(?: volume="([^"]*)")?>(.*?)</prosody>',
        prosody_replace,
        text
    )
    
    # 4. <speak> နဲ့ </speak> ကိုဖယ်မယ်
    text = re.sub(r'<speak>', '', text)
    text = re.sub(r'</speak>', '', text)
    
    # 5. နေရာလွတ်တွေကို သန့်ရှင်းအောင်လုပ်မယ်
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

# ===== Text Input =====
st.subheader("📝 SSML Text Input")
st.caption("အောက်ပါ SSML Tag တွေကို သုံးနိုင်ပါတယ်: `<emphasis>`, `<break>`, `<prosody>`")

text_input = st.text_area(
    "",
    height=150,
    placeholder="""
SSML ဥပမာ:
<speak>
    <prosody rate="slow">
        <emphasis level="strong">မင်္ဂလာပါ</emphasis>
        <break time="500ms"/>
        ဒီနေ့ ရာသီဥတု ကောင်းပါတယ်။
    </prosody>
</speak>
"""
)

# ===== SSML ပြောင်းလဲပြီး ပြသမယ် =====
if text_input:
    converted_text = ssml_to_edge_tts(text_input)
    if converted_text != text_input:
        with st.expander("📋 SSML → Plain Text (ပြောင်းလဲထားတဲ့ စာသား)", expanded=False):
            st.code(converted_text, language="text")
            st.caption("💡 အထက်ပါစာသားကို TTS နဲ့ အသံပြောင်းပေးမှာပါ")

# ===== Quality & Settings =====
col1, col2 = st.columns(2)
with col1:
    rate = st.slider("🔊 Speed", -50, 50, 0)
    rate_str = f"{rate:+d}%"
with col2:
    pitch = st.slider("🎵 Pitch", -12, 12, 0)
    pitch_str = f"{pitch:+d}Hz"

def generate_audio(text, voice, rate, pitch):
    try:
        # SSML ကို ပြောင်းလဲပါ
        clean_text = ssml_to_edge_tts(text)
        
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

if st.button("🚀 Generate with SSML", use_container_width=True):
    if not text_input.strip():
        st.error("⚠️ Please enter some text!")
    else:
        with st.spinner("🎤 Generating with SSML effects..."):
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
                    file_name="tts_ssml.mp3",
                    mime="audio/mp3",
                    use_container_width=True
                )
                st.success("✅ Done!")

# ===== SSML Quick Reference =====
st.divider()
st.subheader("📚 SSML Tag အသုံးပြုနည်း")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**🔊 Emphasis (အလေးပေးပြောခြင်း)**")
    st.code('<emphasis level="strong">စာသား</emphasis>', language="xml")
    st.caption("strong, moderate, none")

with col2:
    st.markdown("**⏸️ Break (ရပ်နားခြင်း)**")
    st.code('<break time="500ms"/>', language="xml")
    st.caption("100ms, 500ms, 1s")

with col3:
    st.markdown("**🎛️ Prosody (အသံထွက်ထိန်းချုပ်ခြင်း)**")
    st.code('''
<prosody rate="slow" pitch="+2Hz">
    စာသား
</prosody>
''', language="xml")
    st.caption("rate: slow/fast, pitch: +2Hz/-2Hz")

st.divider()
st.caption("💡 SSML Tag များကို Convert လုပ်ပြီး အသံထွက်ပေးပါသည်")
