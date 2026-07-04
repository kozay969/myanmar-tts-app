import streamlit as st
import edge_tts
import tempfile
import os
import asyncio
import re

st.set_page_config(page_title="Myanmar TTS Pro", page_icon="🎭", layout="centered")

st.title("🎭 Myanmar TTS - Card မလို")
st.caption("Edge-TTS + SSML Style - အလကား 100%")

voice_options = {
    "မြန်မာ - Nilar (မိန်းကလေး)": "my-MM-NilarNeural",
    "မြန်မာ - Thiha (ယောက်ျားလေး)": "my-MM-ThihaNeural",
}

selected_voice_name = st.selectbox("🎤 အသံ", list(voice_options.keys()))
selected_voice = voice_options[selected_voice_name]

# ===== Style Preset 8 မျိုး - Card မလိုပဲအကုန်ရ =====
style_presets = {
    "1. သာမန် - သတင်းဖတ်သလို": {
        "rate": "-5%", "pitch": "-2Hz", "volume": "+0%",
        "break": "300ms", "desc": "တည်ငြိမ်၊ ရှင်းလင်း"
    },
    "2. ပျော်ရွှင်စရာ - သူငယ်ချင်းပြောသလို": {
        "rate": "+8%", "pitch": "+4Hz", "volume": "+10%",
        "break": "200ms", "desc": "မြန်မြန်၊ အသံမြင့်၊ စိတ်လှုပ်ရှား"
    },
    "3. ဝမ်းနည်းစရာ - ငိုသံပါ": {
        "rate": "-25%", "pitch": "-4Hz", "volume": "-10%",
        "break": "600ms", "desc": "ဖြည်းဖြည်း၊ အသံနိမ့်၊ ရပ်နားများများ"
    },
    "4. ဒေါသထွက်စရာ - အော်သလို": {
        "rate": "+12%", "pitch": "+3Hz", "volume": "+30%",
        "break": "150ms", "desc": "မြန်မြန်၊ ကျယ်ကျယ်၊ ပြတ်ပြတ်"
    },
    "5. တိုးတိုးလေး - လျှို့ဝှက်ပြောသလို": {
        "rate": "-15%", "pitch": "-1Hz", "volume": "-40%",
        "break": "400ms", "desc": "ဖြည်းဖြည်း၊ တိုးတိုး"
    },
    "6. ရုပ်ရှင်နမူနာ - Drama ဆန်ဆန်": {
        "rate": "-10%", "pitch": "-3Hz", "volume": "+15%",
        "break": "800ms", "desc": "ဖြည်းဖြည်း၊ လေးလေး၊ ရပ်နားရှည်"
    },
    "7. ကလေးအသံ - ချစ်စရာကောင်းအောင်": {
        "rate": "+18%", "pitch": "+7Hz", "volume": "+5%",
        "break": "250ms", "desc": "မြန်မြန်၊ အသံမြင့်မြင့်"
    },
    "8. အဘိုးကြီးအသံ - အေးအေးဆေးဆေး": {
        "rate": "-30%", "pitch": "-5Hz", "volume": "-5%",
        "break": "700ms", "desc": "အရမ်းဖြည်း၊ အသံနိမ့်"
    },
}

col1, col2 = st.columns([2, 1])
with col1:
    selected_style = st.selectbox("🎭 အသံစတိုင်", list(style_presets.keys()))
    style_config = style_presets[selected_style]
with col2:
    st.write("")
    st.write("")
    show_ssml = st.checkbox("SSML ပြမယ်")

st.info(f"**{selected_style}**\n\n{style_config['desc']}")

# Custom ချိန်ချင်ရင်
with st.expander("⚙️ ကိုယ်တိုင်ချိန်မယ်"):
    custom_rate = st.slider("Speed", -50, 50, int(style_config['rate'].replace('%','').replace('+','')))
    custom_pitch = st.slider("Pitch", -10, 10, int(style_config['pitch'].replace('Hz','').replace('+','')))
    custom_volume = st.slider("Volume", -50, 50, int(style_config['volume'].replace('%','').replace('+','')))
    style_config['rate'] = f"{custom_rate:+d}%"
    style_config['pitch'] = f"{custom_pitch:+d}Hz"
    style_config['volume'] = f"{custom_volume:+d}%"

text_input = st.text_area("📝 စာသား:", height=200, placeholder="မင်္ဂလာပါ။ ဒီနေ့ ရာသီဥတု အရမ်းကောင်းပါတယ်။")

def create_pro_ssml(text, voice, style_cfg):
    """စာကြောင်းတိုင်းကို Break + Emphasis Auto ထည့်မယ်"""
    # စာကြောင်းခွဲမယ်
    sentences = re.split(r'([။.!?])', text)
    processed = []
    
    for i in range(0, len(sentences)-1, 2):
        sentence = sentences[i].strip()
        punct = sentences[i+1] if i+1 < len(sentences) else ""
        
        if sentence:
            # အရေးကြီးစကားလုံးတွေ Auto Emphasis
            keywords = ['အရမ်း', 'အရမ်းကို', 'တကယ်', 'လုံးဝ', 'မင်္ဂလာပါ', 'ကျေးဇူးတင်ပါတယ်']
            for kw in keywords:
                sentence = sentence.replace(kw, f'<emphasis level="moderate">{kw}</emphasis>')
            
            # စာကြောင်းအဆုံးမှာ Break ထည့်
            processed.append(f"{sentence}{punct}<break time='{style_cfg['break']}'/>")
    
    full_text = " ".join(processed)
    
    ssml = f"""<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="my-MM">
    <voice name="{voice}">
        <prosody rate="{style_cfg['rate']}" pitch="{style_cfg['pitch']}" volume="{style_cfg['volume']}">
            {full_text}
        </prosody>
    </voice>
</speak>"""
    return ssml

async def generate_audio(ssml_text):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
        output_file = tmp_file.name
    communicate = edge_tts.Communicate(ssml_text, selected_voice)
    await communicate.save(output_file)
    with open(output_file, "rb") as f:
        audio_bytes = f.read()
    os.unlink(output_file)
    return audio_bytes

if st.button("🚀 အသံထုတ်မယ်", use_container_width=True, type="primary"):
    if not text_input.strip():
        st.error("⚠️ စာသားထည့်ပါ!")
    else:
        with st.spinner(f'{selected_style} စတိုင်နဲ့ ထုတ်နေတယ်...'):
            try:
                ssml = create_pro_ssml(text_input, selected_voice, style_config)
                
                if show_ssml:
                    with st.expander("🔍 SSML Code"):
                        st.code(ssml, language="xml")
                
                audio_bytes = asyncio.run(generate_audio(ssml))
                st.success("✅ ရပြီ!")
                st.audio(audio_bytes, format="audio/mp3")
                st.download_button("📥 MP3 Download", audio_bytes, f"tts_{selected_style[:2]}.mp3", "audio/mp3", use_container_width=True)
            except Exception as e:
                st.error(f"❌ Error: {e}")

st.divider()
st.markdown("""
### 💡 အသံကောင်းအောင် Tips
1. **"ဝမ်းနည်းစရာ"** Style = ငိုသံပါသလို ဖြစ်မယ်
2. **"ရုပ်ရှင်နမူနာ"** Style = Movie Trailer လိုဖြစ်မယ် 
3. **စာကြောင်းတိုတိုရေး** = ပိုသဘာဝကျတယ်
4. **သတ်ပုံ (။) ထည့်ပါ** = Auto Break ရမယ်
5. **ကိုယ်တိုင်ချိန်မယ်** = ကိုယ့်နားထောင်ကောင်းတဲ့အထိ ချိန်လို့ရတယ်
""")
st.caption("✅ Card မလို | ✅ API Key မလို | ✅ Unlimited အလကား")
