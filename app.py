import streamlit as st
import edge_tts
import asyncio
import tempfile
import os

st.set_page_config(page_title="Prompt TTS", page_icon="🎙️", layout="wide")

st.title("🎙️ Prompt နဲ့ အသံပုံစံပြောင်းမယ်")
st.markdown("---")

# Session state ထဲ audio သိမ်းဖို့
if 'audio_file' not in st.session_state:
    st.session_state.audio_file = None

def parse_style_prompt(prompt):
    """Prompt ထဲက Keyword ဖမ်းပြီး ffmpeg filter ပြောင်းတာ"""
    prompt = prompt.lower()
    filters = []
    effects = []
    
    # 1. Pitch
    if any(w in prompt for w in ['ထူထူ', 'ထူ', 'နိမ့်', 'အဖိုးကြီး', 'ဦးလေးကြီး', 'ဘကြီး', 'ဗီလိန်']):
        filters.append("asetrate=44100*0.75,aresample=44100")
        effects.append("အသံထူထူ")
    elif any(w in prompt for w in ['စူးစူး', 'စူး', 'မြင့်', 'ကလေး', 'မိန်းကလေး', 'ချိုချို', 'anime']):
        filters.append("asetrate=44100*1.3,aresample=44100")
        effects.append("အသံစူးစူး")
    
    # 2. Speed
    if any(w in prompt for w in ['နှေး', 'နှေးနှေး', 'ဖြည်းဖြည်း', 'လေးလေး', 'အေးအေး']):
        filters.append("atempo=0.7")
        effects.append("နှေးနှေး")
    elif any(w in prompt for w in ['မြန်', 'မြန်မြန်', 'သွက်သွက်', 'အမြန်']):
        filters.append("atempo=1.4")
        effects.append("မြန်မြန်")
    else:
        filters.append("atempo=1.0")
    
    # 3. Emotion
    if any(w in prompt for w in ['တုန်တုန်', 'တုန်', 'ကြောက်နေ', 'ငိုနေ', 'တုန်လှုပ်']):
        filters.append("vibrato=f=6:d=0.7")
        effects.append("အသံတုန်တုန်")
    
    if any(w in prompt for w in ['ဒေါသ', 'စိတ်ဆိုး', 'အော်နေ', 'ဟိန်းနေ', 'မာန်ပါပါ']):
        filters.append("bass=g=10,treble=g=3")
        effects.append("ဒေါသသံ")
    
    if any(w in prompt for w in ['ဝမ်းနည်း', 'ငိုသံ', 'ညှိုးနေ', 'မျက်ရည်ကျ']):
        filters.append("lowpass=f=2000,volume=0.8")
        effects.append("ဝမ်းနည်းသံ")
    
    # 4. Special Effects
    if any(w in prompt for w in ['ပဲ့တင်', 'echo', 'ဂူထဲက', 'ခန်းမထဲက']):
        filters.append("aecho=0.8:0.9:1000:0.3")
        effects.append("ပဲ့တင်သံ")
    
    if any(w in prompt for w in ['စက်ရုပ်', 'robot', 'ai', 'ကွန်ပျူတာ']):
        filters.append("afftfilt=real='hypot(re,im)*sin(0)':imag='hypot(re,im)*cos(0)':win_size=512:overlap=0.75")
        effects.append("စက်ရုပ်သံ")
    
    if any(w in prompt for w in ['ဖုန်းထဲက', 'ရေဒီယို', 'ဝေးနေ', 'ဟိုးအဝေးက']):
        filters.append("highpass=f=300,lowpass=f=3400,volume=0.7")
        effects.append("ဖုန်းသံ")
    
    if not filters:
        return "", "သာမန်"
    
    return ",".join(filters), " + ".join(effects)

async def generate_with_prompt(text, base_voice, style_prompt):
    # Step 1: အခြေခံအသံ ထုတ်မယ်
    communicate = edge_tts.Communicate(text, base_voice)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
        await communicate.save(tmp.name)
        base_audio = tmp.name

    # Step 2: Prompt ဖမ်းပြီး Effect ထည့်မယ်
    filter_str, detected = parse_style_prompt(style_prompt)
    
    if not filter_str:
        return base_audio, detected
    
    output_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
    cmd = f'ffmpeg -i "{base_audio}" -af "{filter_str}" -y "{output_audio}"'
    os.system(cmd)
    os.remove(base_audio)
    
    return output_audio, detected

# UI Layout
col1, col2 = st.columns([2, 1])

with col1:
    text = st.text_area("📝 ဖတ်စေချင်တဲ့စာ", height=150, placeholder="ဒီနေ့ မိုးရွာမယ်...")
    
    base_voice = st.selectbox("🎭 အခြေခံအသံ", 
        ["my-MM-ThihaNeural", "my-MM-NilarNeural"],
        format_func=lambda x: "Thiha - ယောက်ျားလေး" if "Thiha" in x else "Nilar - မိန်းကလေး"
    )

with col2:
    st.markdown("### 💡 Keyword ဥပမာများ")
    st.code("""
ထူထူ, စူးစူး
နှေး, မြန်
တုန်တုန်, ဒေါသ
ဝမ်းနည်း, ပဲ့တင်
စက်ရုပ်, ဖုန်းထဲက
ကလေး, အဖိုးကြီး
    """)

style_prompt = st.text_area(
    "✍️ အသံပုံစံ Prompt", 
    height=80, 
    placeholder="ဥပမာ: အသံထူထူ၊ နှေးနှေး၊ ဒေါသထွက်နေတဲ့ပုံစံ",
    help="Keyword တွေ ကော်မာ နဲ့ တွဲရေးလို့ရတယ်"
)

if st.button("🚀 Prompt နဲ့ ထုတ်မယ်", use_container_width=True, type="primary"):
    if text.strip():
        with st.spinner("အသံထုတ်နေတယ်... ခဏစောင့်"):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            audio_path, detected_effects = loop.run_until_complete(
                generate_with_prompt(text, base_voice, style_prompt)
            )
            st.session_state.audio_file = audio_path
            st.session_state.detected = detected_effects
            st.success("✅ ရပြီ!")
    else:
        st.warning("⚠️ စာရိုက်ထည့်ဦးလေ bro")

# Audio Player
if st.session_state.audio_file:
    st.markdown("---")
    st.markdown(f"**ဖမ်းမိတဲ့ Effect:** {st.session_state.detected}")
    
    with open(st.session_state.audio_file, 'rb') as f:
        audio_bytes = f.read()
        st.audio(audio_bytes, format='audio/mp3')
        
        st.download_button(
            label="📥 MP3 Download",
            data=audio_bytes,
            file_name="prompt_voice.mp3",
            mime="audio/mp3",
            use_container_width=True
        )

# Footer
st.markdown("---")
st.markdown("💡 **Tip:** `အသံထူထူ၊ ပဲ့တင်၊ နှေးနှေး` လို တွဲရေးကြည့်")
