import streamlit as st
import edge_tts
import tempfile
import os
import asyncio

st.set_page_config(page_title="Myanmar TTS Pro", page_icon="🎭", layout="centered")

st.title("🎭 Myanmar TTS - Style 15 မျိုး")
st.caption("SSML မပါ - မြန်မာအသံနဲ့ 100% အဆင်ပြေ ✅")

voice_options = {
    "မြန်မာ - Nilar (မိန်းကလေး)": "my-MM-NilarNeural",
    "မြန်မာ - Thiha (ယောက်ျားလေး)": "my-MM-ThihaNeural",
}

selected_voice_name = st.selectbox("🎤 အသံ", list(voice_options.keys()))
selected_voice = voice_options[selected_voice_name]

# Style 15 မျိုး - SSML မသုံးတော့ဘူး၊ Direct Rate/Pitch သုံးမယ်
style_presets = {
    "1. သာမန်": {"rate": "+0%", "pitch": "+0Hz", "volume": "+0%"},
    "2. ပျော်ရွှင်စရာ": {"rate": "+12%", "pitch": "+5Hz", "volume": "+15%"},
    "3. ဝမ်းနည်းစရာ": {"rate": "-30%", "pitch": "-5Hz", "volume": "-15%"},
    "4. ဒေါသထွက်စရာ": {"rate": "+15%", "pitch": "+4Hz", "volume": "+40%"},
    "5. ကြောက်လန့်စရာ": {"rate": "+20%", "pitch": "+6Hz", "volume": "+10%"},
    "6. တိုးတိုးလေး": {"rate": "-15%", "pitch": "-2Hz", "volume": "-50%"},
    "7. သတင်းကြေညာသူ": {"rate": "-8%", "pitch": "-3Hz", "volume": "+10%"},
    "8. ရုပ်ရှင်နမူနာ": {"rate": "-12%", "pitch": "-4Hz", "volume": "+25%"},
    "9. ကလေးအသံ": {"rate": "+22%", "pitch": "+8Hz", "volume": "+5%"},
    "10. အဘိုးကြီးအသံ": {"rate": "-35%", "pitch": "-6Hz", "volume": "-10%"},
    "11. DJ/Host": {"rate": "+5%", "pitch": "+2Hz", "volume": "+20%"},
    "12. ASMR": {"rate": "-20%", "pitch": "-1Hz", "volume": "-60%"},
    "13. ရုံးအစည်းအဝေး": {"rate": "-3%", "pitch": "-1Hz", "volume": "+5%"},
    "14. ပုံပြင်ပြောသူ": {"rate": "-10%", "pitch": "+3Hz", "volume": "+10%"},
    "15. Robot": {"rate": "-5%", "pitch": "-8Hz", "volume": "+0%"},
}

selected_style = st.selectbox("🎭 အသံစတိုင် 15 မျိုး", list(style_presets.keys()))
style_config = style_presets[selected_style]

st.info(f"**{selected_style}**\n\nSpeed: {style_config['rate']} | Pitch: {style_config['pitch']} | Volume: {style_config['volume']}")

# Custom ချိန်မယ်
with st.expander("⚙️ ကိုယ်တိုင်အသေးစိတ်ချိန်မယ်"):
    c1, c2, c3 = st.columns(3)
    with c1:
        custom_rate = st.slider("Speed", -50, 50, int(style_config['rate'].replace('%','').replace('+','')))
    with c2:
        custom_pitch = st.slider("Pitch", -10, 10, int(style_config['pitch'].replace('Hz','').replace('+','')))
    with c3:
        custom_volume = st.slider("Volume", -50, 50, int(style_config['volume'].replace('%','').replace('+','')))
    
    style_config['rate'] = f"{custom_rate:+d}%"
    style_config['pitch'] = f"{custom_pitch:+d}Hz"
    style_config['volume'] = f"{custom_volume:+d}%"

text_input = st.text_area("📝 စာသားထည့်ပါ:", height=200, placeholder="မင်္ဂလာပါ။ ဒီနေ့ ရာသီဥတု အရမ်းကောင်းပါတယ်။")

def add_pause(text):
    """စာကြောင်းကြား ခဏရပ်အောင် . ကို ... ပြောင်းမယ်"""
    text = text.replace("။", "။ ... ")
    text = text.replace(".", ". ... ")
    text = text.replace("!", "! ... ")
    text = text.replace("?", "? ... ")
    return text

def generate_audio_sync(text, voice, rate, pitch, volume):
    async def _generate():
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            output_file = tmp_file.name

        # SSML မသုံးတော့ဘူး - Direct parameter သုံးမယ် ✅
        communicate = edge_tts.Communicate(
            text, 
            voice,
            rate=rate,
            pitch=pitch,
            volume=volume
        )
        await communicate.save(output_file)

        with open(output_file, "rb") as f:
            audio_bytes = f.read()
        os.unlink(output_file)
        return audio_bytes
    
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(_generate())

# ခလုတ်က ဒီမှာရှိတယ် ✅
if st.button("🚀 အသံထုတ်မယ်", use_container_width=True, type="primary"):
    if not text_input.strip():
        st.error("⚠️ စာသားအရင်ထည့်ပါ!")
    else:
        with st.spinner(f'{selected_style} စတိုင်နဲ့ ထုတ်နေတယ်...'):
            try:
                # Pause ထည့်မယ်
                processed_text = add_pause(text_input)
                
                audio_bytes = generate_audio_sync(
                    processed_text, 
                    selected_voice,
                    style_config['rate'],
                    style_config['pitch'],
                    style_config['volume']
                )
                st.success("✅ ရပြီ! SSML မပါတော့ဘူး")
                st.audio(audio_bytes, format="audio/mp3")
                st.download_button(
                    "📥 MP3 Download",
                    audio_bytes,
                    f"tts_{selected_style[:2]}.mp3",
                    "audio/mp3",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

st.divider()
st.markdown("""
### 💡 ဘာပြောင်းလိုက်လဲ?
1. **SSML လုံးဝဖြုတ်ထားတယ်** → Code မဖတ်တော့ဘူး
2. **Direct Rate/Pitch/Volume သုံးထားတယ်** → မြန်မာအသံနဲ့ 100% အဆင်ပြေ
3. **... ထည့်ပြီး Pause တုလုပ်ထားတယ်**
