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

st.title("🔊 Myanmar TTS - SSML Control")
st.caption("SSML အဆင့်မြင့်ထိန်းချုပ်မှုများဖြင့် အသံထွက်ကို ပိုမိုကောင်းမွန်အောင် ပြုလုပ်နိုင်သည်")

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

# ===== SSML Control Section =====
st.subheader("🎛️ SSML Advanced Controls")
st.caption("အောက်ပါခလုတ်များကို စာသားထဲမှာ ထည့်သုံးနိုင်သည်")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🔊 Emphasis", use_container_width=True):
        st.code("""<emphasis level="strong">ဒီစာသား</emphasis>""", language="xml")

with col2:
    if st.button("⏸️ Pause", use_container_width=True):
        st.code("""<break time="500ms"/>""", language="xml")

with col3:
    if st.button("🔉 Volume", use_container_width=True):
        st.code("""<prosody volume="+20%">ဒီစာသား</prosody>""", language="xml")

with col4:
    if st.button("📝 SSML Example", use_container_width=True):
        st.code("""
<speak>
    <prosody rate="slow" pitch="+2Hz">
        <emphasis level="strong">အရေးကြီးသော</emphasis> စာသား
        <break time="300ms"/>
        နောက်ထပ် စာသား
    </prosody>
</speak>
""", language="xml")

st.divider()

# Text input with SSML help
text_input = st.text_area(
    "📝 Enter text (SSML tags များထည့်သုံးနိုင်သည်)", 
    height=150, 
    placeholder="""
SSML ဥပမာ:
<speak>
    <prosody rate="slow" pitch="+2Hz">
        <emphasis level="strong">မင်္ဂလာပါ</emphasis>
        <break time="500ms"/>
        ဒီနေ့ ရာသီဥတု ကောင်းပါတယ်။
    </prosody>
</speak>
"""
)

# ===== SSML Settings =====
with st.expander("⚙️ SSML Settings", expanded=False):
    st.info("အောက်ပါ Settings များကို စာသားတစ်ခုလုံးအတွက် အသုံးပြုနိုင်သည်")
    
    col1, col2 = st.columns(2)
    with col1:
        rate = st.slider("🔊 Speech Speed", -50, 50, 0, 5)
        rate_str = f"{rate:+d}%"
    with col2:
        pitch = st.slider("🎵 Pitch", -12, 12, 0, 1)
        pitch_str = f"{pitch:+d}Hz"
    
    volume = st.slider("🔉 Volume", -50, 50, 0, 5)
    volume_str = f"{volume:+d}%"

# ===== SSML Functions =====
def create_ssml(text, rate, pitch, volume):
    """Create SSML wrapper for text"""
    # Check if text already contains SSML tags
    if "<speak>" in text and "</speak>" in text:
        return text
    
    # Wrap with SSML prosody
    return f"""<speak>
    <prosody rate="{rate}" pitch="{pitch}" volume="{volume}">
        {text}
    </prosody>
</speak>"""

def extract_plain_text(ssml_text):
    """Extract plain text from SSML (for preview)"""
    # Remove SSML tags
    plain = re.sub(r'<[^>]+>', '', ssml_text)
    return plain.strip()

# Preview plain text
if text_input:
    plain_text = extract_plain_text(text_input)
    if plain_text and plain_text != text_input:
        st.caption(f"📄 Plain text preview: {plain_text[:100]}...")

# ===== Quality Selection =====
quality_options = {
    "📀 Standard (48 kbps)": "Standard",
    "💿 High (96 kbps)": "High",
    "🎵 Premium (160 kbps)": "Premium",
}
selected_quality_name = st.selectbox("🔊 Audio Quality", list(quality_options.keys()))

def generate_audio(text, voice, rate, pitch, volume):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            output_file = tmp_file.name
        
        # Create SSML
        ssml_text = create_ssml(text, rate, pitch, volume)
        
        async def run_tts():
            communicate = edge_tts.Communicate(
                ssml_text, 
                voice,
                rate=rate,
                pitch=pitch
            )
            await communicate.save(output_file)
        
        asyncio.run(run_tts())
        
        with open(output_file, "rb") as f:
            audio_bytes = f.read()
        os.unlink(output_file)
        return audio_bytes, None, ssml_text
    except Exception as e:
        return None, str(e), None

if st.button("🚀 Generate with SSML", use_container_width=True):
    if not text_input.strip():
        st.error("⚠️ Please enter some text!")
    else:
        with st.spinner("🎤 Generating with SSML controls..."):
            audio_bytes, error, ssml_used = generate_audio(
                text_input, selected_voice, rate_str, pitch_str, volume_str
            )
            
            if error:
                st.error(f"❌ Error: {error}")
            else:
                # Show SSML used
                with st.expander("📋 SSML Generated (Click to view)", expanded=False):
                    st.code(ssml_used, language="xml")
                
                st.audio(audio_bytes, format="audio/mp3")
                st.download_button(
                    label="📥 Download MP3",
                    data=audio_bytes,
                    file_name="tts_ssml.mp3",
                    mime="audio/mp3",
                    use_container_width=True
                )
                st.success(f"✅ Done! (Quality: {selected_quality_name})")

# ===== Quick SSML Examples =====
st.divider()
st.subheader("📚 SSML Quick Examples")
st.caption("အောက်ပါ ဥပမာများကို Copy ကူးပြီး အသုံးပြုနိုင်သည်")

col1, col2 = st.columns(2)

with col1:
    st.code("""
<speak>
    <prosody rate="slow">
        <emphasis level="strong">အလွန်အရေးကြီးသော</emphasis>
        ကြေညာချက်
        <break time="1s"/>
        ကျေးဇူးပြု၍ နားထောင်ပါ။
    </prosody>
</speak>
    """, language="xml")
    
    st.caption("🎯 Emphasis + Pause")

with col2:
    st.code("""
<speak>
    <prosody pitch="+4Hz" volume="+30%">
        မင်္ဂလာပါ ခင်ဗျာ။
        <break time="300ms"/>
        ဒီနေ့ သင်ဘယ်လိုနေလဲ။
    </prosody>
</speak>
    """, language="xml")
    
    st.caption("🎯 Pitch + Volume")

st.divider()
st.caption("💡 SSML Tags: `<emphasis>`, `<break>`, `<prosody>` | Powered by Edge TTS")
