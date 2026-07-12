import streamlit as st
import edge_tts
import asyncio
import tempfile
import os

st.set_page_config(page_title="Prompt TTS Pro", page_icon="🎙️", layout="wide")

st.title("🎙️ Prompt + Speed + Echo Control TTS")
st.markdown("---")

# Session state
if 'audio_file' not in st.session_state:
    st.session_state.audio_file = None
if 'detected' not in st.session_state:
    st.session_state.detected = ""

def parse_style_prompt(prompt, speed_multiplier=1.0, echo_level=0):
    """Prompt ထဲက Keyword + Slider ဖမ်းပြီး ffmpeg filter ပြောင်းတာ"""
    prompt = prompt.lower()
    filters = []
    effects = []
    pitch_rate = 1.0
    
    # 1. Pitch - အသံအနိမ့်အမြင့်
    if any(w in prompt for w in ['ထူထူ', 'ထူ', 'နိမ့်', 'အဖိုးကြီး', 'ဦးလေးကြီး', 'ဘကြီး', 'ဗီလိန်']):
        pitch_rate = 0.75
        filters.append("asetrate=44100*0.75,aresample=44100")
        effects.append("အသံထူထူ")
    elif any(w in prompt for w in ['စူးစူး', 'စူး', 'မြင့်', 'ကလေး', 'မိန်းကလေး', 'ချိုချို', 'anime']):
        pitch_rate = 1.3
        filters.append("asetrate=44100*1.3,aresample=44100")
        effects.append("အသံစူးစူး")
    
    # 2. Speed - Slider ကနေ လာတာ + Prompt မှာပါရင် ပေါင်းမယ်
    final_speed = speed_multiplier
    if any(w in prompt for w in ['နှေး', 'နှေးနှေး', 'ဖြည်းဖြည်း', 'လေးလေး', 'အေးအေး']):
        final_speed *= 0.7
        effects.append("နှေးနှေး")
    elif any(w in prompt for w in ['မြန်', 'မြန်မြန်', 'သွက်သွက်', 'အမြန်']):
        final_speed *= 1.4
        effects.append("မြန်မြန်")
    
    # Pitch ပြောင်းထားရင် Speed ပြန်ထိန်းဖို့
    if pitch_rate != 1.0:
        tempo_fix = final_speed / pitch_rate
        filters.append(f"atempo={tempo_fix}")
    else:
        filters.append(f"atempo={final_speed}")
    
    if speed_multiplier != 1.0:
        effects.append(f"Speed {speed_multiplier}x")
    
    # 3. Emotion Effects
    if any(w in prompt for w in ['တုန်တုန်', 'တုန်', 'ကြောက်နေ', 'ငိုနေ', 'တုန်လှုပ်']):
        filters.append("vibrato=f=6:d=0.7")
        effects.append("အသံတုန်တုန်")
    
    if any(w in prompt for w in ['ဒေါသ', 'စိတ်ဆိုး', 'အော်နေ', 'ဟိန်းနေ', 'မာန်ပါပါ']):
        filters.append("bass=g=10,treble=g=3")
        effects.append("ဒေါသသံ")
    
    if any(w in prompt for w in ['ဝမ်းနည်း', 'ငိုသံ', 'ညှိုးနေ', 'မျက်ရည်ကျ']):
        filters.append("lowpass=f=2000,volume=0.8")
        effects.append("ဝမ်းနည်းသံ")
    
    # 4. Echo - Slider ကနေ လာတာ + Prompt မှာပါရင် ပေါင်းမယ်
    echo_value = echo_level
    if 'ပဲ့တင်အနည်းဆုံး' in prompt or 'echo နည်းနည်း' in prompt:
        echo_value = max(echo_value, 5)  # အနည်းဆုံး 5%
        effects.append("ပဲ့တင်အနည်းဆုံး")
    elif 'ပဲ့တင်နည်းနည်း' in prompt or 'echo နည်း' in prompt or 'echoနည်း' in prompt:
        echo_value = max(echo_value, 10)  # အနည်းဆုံး 10%
        effects.append("ပဲ့တင်နည်းနည်း")
    elif 'ပဲ့တင်များများ' in prompt or 'echo များ' in prompt or 'ဂူထဲက' in prompt or 'echoများ' in prompt:
        echo_value = max(echo_value, 50)  # အနည်းဆုံး 50%
        effects.append("ပဲ့တင်များများ")
    elif any(w in prompt for w in ['ပဲ့တင်', 'echo', 'ခန်းမထဲက']):
        echo_value = max(echo_value, 30)  # အနည်းဆုံး 30%
        effects.append("ပဲ့တင်သံ")
    
    # Echo Slider ထည့်မယ်
    if echo_value > 0:
        decay = echo_value / 100.0  # 0.0 to 1.0
        delay = int(300 + (echo_value * 12))  # 300ms to 1500ms
        filters.append(f"aecho=0.8:0.9:{delay}:{decay}")
        effects.append(f"Echo {echo_value}%")
    
    # 5. Special Effects
    if any(w in prompt for w in ['စက်ရုပ်', 'robot', 'ai', 'ကွန်ပျူတာ']):
        filters.append("afftfilt=real='hypot(re,im)*sin(0)':imag='hypot(re,im)*cos(0)':win_size=512:overlap=0.75")
        effects.append("စက်ရုပ်သံ")
    
    if any(w in prompt for w in ['ဖုန်းထဲက', 'ရေဒီယို', 'ဝေးနေ', 'ဟိုးအဝေးက']):
        filters.append("highpass=f=300,lowpass=f=3400,volume=0.7")
        effects.append("ဖုန်းသံ")
    
    if not effects:
        effects.append("သာမန်")
    
    return ",".join(filters), " + ".join(effects)

async def generate_with_prompt(text, base_voice, style_prompt, speed, echo):
    if not text.strip():
        st.error("❌ ဖတ်ဖို့စာ ရိုက်ထည့်ပါဦး bro")
        return None, "စာမရှိဘူး"
    
    # Step 1: အခြေခံအသံ ထုတ်မယ်
    try:
        communicate = edge_tts.Communicate(text, base_voice)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            await communicate.save(tmp.name)
            base_audio = tmp.name
    except Exception as e:
        st.error(f"❌ Edge TTS Error: {e}")
        return None, "TTS မရဘူး"

    # Step 2: Prompt + Speed + Echo ဖမ်းပြီး Effect ထည့်မယ်
    filter_str, detected = parse_style_prompt(style_prompt, speed, echo)
    
    output_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
    cmd = f'ffmpeg -i "{base_audio}" -af "{filter_str}" -y "{output_audio}"'
    
    result = os.system(cmd)
    os.remove(base_audio)
    
    if result != 0:
        st.error("❌ ffmpeg Error။ packages.txt ထဲမှာ ffmpeg ထည့်ပါ")
        return None, "ffmpeg Error"
    
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
ဝမ်းနည်း
စက်ရုပ်, ဖုန်းထဲက
    """)
    st.caption("ပဲ့တင်/နှေးမြန် က Slider နဲ့ချိန်")

# Speed + Echo Slider 2 ခု
col_speed, col_echo = st.columns(2)

with col_speed:
    speed = st.slider(
        "⚡ အသံအမြန်နှုန်း", 
        min_value=0.5, 
        max_value=2.0, 
        value=1.0, 
        step=0.1,
        help="0.5x = အရမ်းနှေး | 1.0x = ပုံမှန် | 2.0x = အရမ်းမြန်"
    )
    st.markdown(f"<center><b style='color:#52c41a'>Speed: {speed}x</b></center>", unsafe_allow_html=True)

with col_echo:
    echo = st.slider(
        "🔊 ပဲ့တင်သံ Level", 
        min_value=0, 
        max_value=100, 
        value=0, 
        step=5,
        help="0% = မပါ | 30% = ခန်းမထဲ | 100% = ဂူထဲ"
    )
    st.markdown(f"<center><b style='color:#ffa500'>Echo: {echo}%</b></center>", unsafe_allow_html=True)

style_prompt = st.text_area(
    "✍️ အသံပုံစံ Prompt (Optional)", 
    height=60, 
    placeholder="ဥပမာ: အသံထူထူ၊ ဒေါသသံ",
    help="Speed နဲ့ Echo က Slider နဲ့ချိန်၊ ကျန်တာ ဒီမှာ Keyword ရေးပါ"
)

if st.button("🚀 ထုတ်မယ်", use_container_width=True, type="primary"):
    if text.strip():
        with st.spinner("အသံထုတ်နေတယ်... ခဏစောင့်"):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            audio_path, detected_effects = loop.run_until_complete(
                generate_with_prompt(text, base_voice, style_prompt, speed, echo)
            )
            if audio_path:
                st.session_state.audio_file = audio_path
                st.session_state.detected = detected_effects
                st.success("✅ ရပြီ!")
    else:
        st.warning("⚠️ ဖတ်ဖို့စာ ရိုက်ထည့်ဦးလေ bro")

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
st.markdown("💡 **Tip:** Speed 0.8x + Echo 15% + `အသံထူထူ` = ဗီလိန်အသံ ရှယ်")
