import streamlit as st
import edge_tts
import tempfile
import os
import re

st.set_page_config(page_title="Myanmar TTS Pro", page_icon="🎭", layout="centered")

st.title("🎭 Myanmar TTS - Style 15 မျိုး")
st.caption("Button Error ပြင်ပြီးသား ✅")

voice_options = {
    "မြန်မာ - Nilar (မိန်းကလေး)": "my-MM-NilarNeural",
    "မြန်မာ - Thiha (ယောက်ျားလေး)": "my-MM-ThihaNeural",
}

selected_voice_name = st.selectbox("🎤 အသံ", list(voice_options.keys()))
selected_voice = voice_options[selected_voice_name]

style_presets = {
    "1. သာမန်": {"rate": "0%", "pitch": "0Hz", "volume": "+0%", "break": "300ms"},
    "2. ပျော်ရွှင်စရာ": {"rate": "+12%", "pitch": "+5Hz", "volume": "+15%", "break": "200ms"},
    "3. ဝမ်းနည်းစရာ": {"rate": "-30%", "pitch": "-5Hz", "volume": "-15%", "break": "700ms"},
    "4. ဒေါသထွက်စရာ": {"rate": "+15%", "pitch": "+4Hz", "volume": "+40%", "break": "100ms"},
    "5. ကြောက်လန့်စရာ": {"rate": "+20%", "pitch": "+6Hz", "volume": "+10%", "break": "150ms"},
    "6. တိုးတိုးလေး": {"rate": "-15%", "pitch": "-2Hz", "volume": "-50%", "break": "400ms"},
    "7. သတင်းကြေညာသူ": {"rate": "-8%", "pitch": "-3Hz", "volume": "+10%", "break": "500ms"},
    "8. ရုပ်ရှင်နမူနာ": {"rate": "-12%", "pitch": "-4Hz", "volume": "+25%", "break": "900ms"},
    "9. ကလေးအသံ": {"rate": "+22%", "pitch": "+8Hz", "volume": "+5%", "break": "250ms"},
    "10. အဘိုးကြီးအသံ": {"rate": "-35%", "pitch": "-6Hz", "volume": "-10%", "break": "800ms"},
    "11. DJ/Host": {"rate": "+5%", "pitch": "+2Hz", "volume": "+20%", "break": "350ms"},
    "12. ASMR": {"rate": "-20%", "pitch": "-1Hz", "volume": "-60%", "break": "600ms"},
    "13. ရုံးအစည်းအဝေး": {"rate": "-3%", "pitch": "-1Hz", "volume": "+5%", "break": "400ms"},
    "14. ပုံပြင်ပြောသူ": {"rate": "-10%", "pitch": "+3Hz", "volume": "+10%", "break": "550ms"},
    "15. Robot": {"rate": "-5%", "pitch": "-8Hz", "volume": "+0%", "break": "100ms"},
}

selected_style = st.selectbox("🎭 အသံစတိုင်", list(style_presets.keys()))
style_config = style_presets[selected_style]

auto_emphasis = st.checkbox("Auto အလေးပေး", value=True)

text_input = st.text_area("📝 စာသားထည့်ပါ:", height=200, placeholder="မင်္ဂလာပါ။ ဒီနေ့ ရာသီဥတု အရမ်းကောင်းပါတယ်။")

def create_pro_ssml(text, voice, style_cfg, auto_emp):
    sentences = re.split(r'([။.!?])', text)
    processed = []

    for i in range(0, len(sentences)-1, 2):
        sentence = sentences[i].strip()
        punct = sentences[i+1] if i+1 < len(sentences) else ""

        if sentence:
            if auto_emp:
                keywords = ['အရမ်း', 'အရမ်းကို', 'တကယ်', 'လုံးဝ', 'အံ့သြ', 'မင်္ဂလာပါ', 'ကျေးဇူးတင်ပါတယ်', 'ချစ်တယ်', 'မုန်းတယ်']
                for kw in keywords:
                    sentence = sentence.replace(kw, f'<emphasis level="moderate">{kw}</emphasis>')

            processed.append(f"{sentence}{punct}<break time='{style_cfg['break']}'/>")

    full_text = " ".join(processed)

    ssml = f"""<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="http://www.w3.org/2001/mstts" xml:lang="my-MM">
    <voice name="{voice}">
        <prosody rate="{style_cfg['rate']}" pitch="{style_cfg['pitch']}" volume="{style_cfg['volume']}">
            {full_text}
        </prosody>
    </voice>
</speak>"""
    return ssml

# ဒါက အရေးကြီးတယ် - asyncio မသုံးတော့ဘူး
def generate_audio_sync(ssml_text, voice):
    import asyncio
    
    async def _generate():
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            output_file = tmp_file.name

        communicate = edge_tts.Communicate(ssml_text, voice)
        await communicate.save(output_file)

        with open(output_file, "rb") as f:
            audio_bytes = f.read()
        os.unlink(output_file)
        return audio_bytes
    
    # Streamlit နဲ့ အဆင်ပြေအောင် loop အသစ်ဆောက်မယ်
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
                ssml = create_pro_ssml(text_input, selected_voice, style_config, auto_emphasis)
                
                with st.expander("🔍 SSML Code ကြည့်မယ်"):
                    st.code(ssml, language="xml")

                audio_bytes = generate_audio_sync(ssml, selected_voice)
                st.success("✅ ရပြီ!")
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

st.caption("✅ Button Error Fix ပြီးသား | SSML မဖတ်တော့ဘူး")
