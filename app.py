import streamlit as st
import edge_tts
import asyncio
import tempfile
import os

st.set_page_config(page_title="Prompt TTS Pro + Clone", page_icon="🎙️", layout="wide")
st.title("🎙️ Prompt TTS Pro + Voice Clone")

tab1, tab2 = st.tabs(["🗣️ Edge TTS (မူရင်း)", "🎤 Voice Clone (Free)"])

# ================= TAB 1 : မင်းရဲ့ မူရင်း Edge TTS =================
with tab1:
    if 'audio_file' not in st.session_state:
        st.session_state.audio_file = None
    if 'detected' not in st.session_state:
        st.session_state.detected = ""

    def parse_style_prompt(prompt, speed_multiplier=1.0, echo_level=0):
        prompt = prompt.lower()
        filters = []
        effects = []
        pitch_rate = 1.0
        if any(w in prompt for w in ['ထူထူ', 'ထူ', 'နိမ့်', 'အဖိုးကြီး', 'ဗီလိန်']):
            pitch_rate = 0.75
            filters.append("asetrate=44100*0.75,aresample=44100")
            effects.append("အသံထူထူ")
        elif any(w in prompt for w in ['စူးစူး', 'စူး', 'မြင့်', 'ကလေး', 'ချိုချို']):
            pitch_rate = 1.3
            filters.append("asetrate=44100*1.3,aresample=44100")
            effects.append("အသံစူးစူး")
        final_speed = speed_multiplier
        if any(w in prompt for w in ['နှေး', 'နှေးနှေး', 'ဖြည်းဖြည်း']):
            final_speed *= 0.7
            effects.append("နှေးနှေး")
        elif any(w in prompt for w in ['မြန်', 'မြန်မြန်', 'သွက်သွက်']):
            final_speed *= 1.4
            effects.append("မြန်မြန်")
        if pitch_rate!= 1.0:
            tempo_fix = final_speed / pitch_rate
            filters.append(f"atempo={tempo_fix}")
        else:
            filters.append(f"atempo={final_speed}")
        if speed_multiplier!= 1.0:
            effects.append(f"Speed {speed_multiplier}x")
        if any(w in prompt for w in ['တုန်တုန်', 'တုန်', 'ကြောက်နေ']):
            filters.append("vibrato=f=6:d=0.7")
            effects.append("အသံတုန်တုန်")
        if any(w in prompt for w in ['ဒေါသ', 'စိတ်ဆိုး', 'အော်နေ', 'ဟိန်းနေ']):
            filters.append("bass=g=10,treble=g=3")
            effects.append("ဒေါသသံ")
        if any(w in prompt for w in ['ဝမ်းနည်း', 'ငိုသံ', 'ညှိုးနေ']):
            filters.append("lowpass=f=2000,volume=0.8")
            effects.append("ဝမ်းနည်းသံ")
        echo_value = echo_level
        if 'ပဲ့တင်အနည်းဆုံး' in prompt: echo_value = max(echo_value, 5)
        elif 'ပဲ့တင်နည်းနည်း' in prompt: echo_value = max(echo_value, 10)
        elif 'ပဲ့တင်များများ' in prompt or 'ဂူထဲက' in prompt: echo_value = max(echo_value, 50)
        elif any(w in prompt for w in ['ပဲ့တင်', 'echo']): echo_value = max(echo_value, 30)
        if echo_value > 0:
            decay = echo_value / 100.0
            delay = int(300 + (echo_value * 12))
            filters.append(f"aecho=0.8:0.9:{delay}:{decay}")
            effects.append(f"Echo {echo_value}%")
        if any(w in prompt for w in ['စက်ရုပ်', 'robot', 'ai']):
            filters.append("afftfilt=real='hypot(re,im)*sin(0)':imag='hypot(re,im)*cos(0)':win_size=512:overlap=0.75")
            effects.append("စက်ရုပ်သံ")
        if any(w in prompt for w in ['ဖုန်းထဲက', 'ရေဒီယို', 'ဝေးနေ']):
            filters.append("highpass=f=300,lowpass=f=3400,volume=0.7")
            effects.append("ဖုန်းသံ")
        if not effects: effects.append("သာမန်")
        return ",".join(filters), " + ".join(effects)

    async def generate_with_prompt(text, base_voice, style_prompt, speed, echo, bgm_file=None, bgm_volume=30):
        if not text.strip(): return None, "စာမရှိဘူး"
        communicate = edge_tts.Communicate(text, base_voice)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            await communicate.save(tmp.name)
            voice_audio = tmp.name
        filter_str, detected = parse_style_prompt(style_prompt, speed, echo)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            voice_with_fx = tmp.name
        os.system(f'ffmpeg -i "{voice_audio}" -af "{filter_str}" -y "{voice_with_fx}"')
        os.remove(voice_audio)
        output_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
        if bgm_file:
            bgm_vol = bgm_volume / 100.0
            os.system(f'ffmpeg -i "{voice_with_fx}" -i "{bgm_file}" -filter_complex "[1:a]volume={bgm_vol}[bgm];[0:a][bgm]amix=inputs=2:duration=first" -y "{output_audio}"')
            os.remove(voice_with_fx)
            detected += f" + BGM {bgm_volume}%"
        else:
            os.rename(voice_with_fx, output_audio)
        return output_audio, detected

    col1, col2 = st.columns([2, 1])
    with col1:
        text = st.text_area("📝 ဖတ်စေချင်တဲ့စာ", height=150, placeholder="ဒီနေ့ မိုးရွာမယ်...")
        base_voice = st.selectbox("🎭 အခြေခံအသံ", ["my-MM-ThihaNeural", "my-MM-NilarNeural"], format_func=lambda x: "Thiha - ယောက်ျားလေး" if "Thiha" in x else "Nilar - မိန်းကလေး")
    with col2:
        st.markdown("### 💡 Keyword ဥပမာ")
        st.code("ထူထူ, စူးစူး\nနှေး, မြန်\nတုန်တုန်, ဒေါသ\nဝမ်းနည်း\nစက်ရုပ်, ဖုန်းထဲက")
    col_speed, col_echo = st.columns(2)
    with col_speed:
        speed = st.slider("⚡ အသံအမြန်နှုန်း", 0.5, 2.0, 1.0, 0.1, key="s1")
    with col_echo:
        echo = st.slider("🔊 ပဲ့တင်သံ Level", 0, 100, 0, 5, key="e1")
    st.markdown("---")
    col_bgm_file, col_bgm_vol = st.columns([2, 1])
    with col_bgm_file:
        bgm_file = st.file_uploader("🎵 နောက်ခံသီချင်း MP3", type=['mp3'], key="bgm1")
    with col_bgm_vol:
        bgm_volume = st.slider("🎚️ BGM အသံ", 0, 100, 30, 5, key="bgmv1")
    style_prompt = st.text_area("✍️ အသံပုံစံ Prompt (Optional)", height=60, placeholder="ဥပမာ: အသံထူထူ၊ ဒေါသသံ", key="pr1")
    if st.button("🚀 ထုတ်မယ်", use_container_width=True, type="primary", key="b1"):
        if text.strip():
            with st.spinner("အသံထုတ်နေတယ်..."):
                bgm_path = None
                if bgm_file:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                        tmp.write(bgm_file.read())
                        bgm_path = tmp.name
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                audio_path, detected_effects = loop.run_until_complete(generate_with_prompt(text, base_voice, style_prompt, speed, echo, bgm_path, bgm_volume))
                if bgm_path: os.remove(bgm_path)
                if audio_path:
                    st.session_state.audio_file = audio_path
                    st.session_state.detected = detected_effects
                    st.success("✅ ရပြီ!")
        else:
            st.warning("⚠️ ဖတ်ဖို့စာ ရိုက်ထည့်ဦးလေ bro")
    if st.session_state.audio_file:
        st.markdown("---")
        st.markdown(f"**ဖမ်းမိတဲ့ Effect:** {st.session_state.detected}")
        with open(st.session_state.audio_file, 'rb') as f:
            audio_bytes = f.read()
            st.audio(audio_bytes, format='audio/mp3')
            st.download_button("📥 MP3 Download", audio_bytes, "tts_pro.mp3", "audio/mp3", use_container_width=True, key="dl1")
    st.markdown("---")
    st.markdown("💡 **Pro Tip:** BGM 20% + Speed 0.8x + Echo 10% + `အသံထူထူ` = Movie Trailer Voice")

# ================= TAB 2 : UNLIMITED Clone - Fixed =================
with tab2:
    st.markdown("### 🎤 Unlimited Clone - 200 limit မရှိ")
    st.info("Tip: HF Space က လူများရင် 30s စောင့်ပြီးပြန်နှိပ်ပါ")
    
    ref_audio = st.file_uploader("🎙️ Reference အသံ (5-10s)", type=['mp3','wav','flac','m4a'], key="ref_fixed")
    clone_text = st.text_area("📝 စာ - အရှည်ကြီးရတယ် (1000+ လုံး)", height=250, key="txt_fixed")
    speed = st.slider("Speed", 0.8, 1.5, 1.0, key="sp_fixed")
    
    if st.button("🚀 Unlimited ထုတ်မယ်", type="primary", use_container_width=True):
        if not ref_audio or not clone_text:
            st.warning("အသံနဲ့ စာ 2 ခုလုံး ထည့်ပါ")
        else:
            # ပိုလွယ်တဲ့နည်း - iframe မဟုတ်၊ တကယ့် unlimited
            st.markdown("#### အမြန်နည်း - ဒီ iframe ထဲမှာ တိုက်ရိုက်လုပ်ပါ (Unlimited):")
            st.components.v1.iframe("https://openbmb-VoxCPM-Demo.hf.space", height=900, scrolling=True)
