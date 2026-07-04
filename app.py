import streamlit as st
import edge_tts
import tempfile
import os
import asyncio
import re

st.set_page_config(page_title="Myanmar TTS Pro", page_icon="🎭", layout="centered")

st.title("🎭 Myanmar TTS Pro - Style 15 မျိုး")
st.caption("Edge-TTS + SSML | Card မလို | API Key မလို | Unlimited")

voice_options = {
    "မြန်မာ - Nilar (မိန်းကလေး)": "my-MM-NilarNeural",
    "မြန်မာ - Thiha (ယောက်ျားလေး)": "my-MM-ThihaNeural",
}

selected_voice_name = st.selectbox("🎤 အသံရွေးပါ", list(voice_options.keys()))
selected_voice = voice_options[selected_voice_name]

# ===== Style 15 မျိုး - အကုန်လုံးတု SSML နဲ့ =====
style_presets = {
    "1. သာမန် - နေ့စဉ်စကားပြော": {
        "rate": "0%", "pitch": "0Hz", "volume": "+0%",
        "break": "300ms", "desc": "ပုံမှန်အတိုင်း သဘာဝကျကျ"
    },
    "2. ပျော်ရွှင်စရာ - ရယ်မောသံ": {
        "rate": "+12%", "pitch": "+5Hz", "volume": "+15%",
        "break": "200ms", "desc": "မြန်မြန်၊ အသံမြင့်၊ စိတ်လှုပ်ရှားသံ"
    },
    "3. ဝမ်းနည်းစရာ - ငိုသံပါ": {
        "rate": "-30%", "pitch": "-5Hz", "volume": "-15%",
        "break": "700ms", "desc": "အရမ်းဖြည်း၊ အသံနိမ့်၊ ရပ်နားများများ"
    },
    "4. ဒေါသထွက်စရာ - အော်သံ": {
        "rate": "+15%", "pitch": "+4Hz", "volume": "+40%",
        "break": "100ms", "desc": "မြန်မြန်၊ ကျယ်ကျယ်၊ ပြတ်ပြတ်"
    },
    "5. ကြောက်လန့်စရာ - တုန်လှုပ်သံ": {
        "rate": "+20%", "pitch": "+6Hz", "volume": "+10%",
        "break": "150ms", "desc": "မြန်မြန်၊ အသံတုန်၊ မတည်ငြိမ်သံ"
    },
    "6. တိုးတိုးလေး - လျှို့ဝှက်ပြောသံ": {
        "rate": "-15%", "pitch": "-2Hz", "volume": "-50%",
        "break": "400ms", "desc": "ဖြည်းဖြည်း၊ တိုးတိုး၊ လေသံပါပါ"
    },
    "7. သတင်းကြေညာသူ - MRTV စတိုင်": {
        "rate": "-8%", "pitch": "-3Hz", "volume": "+10%",
        "break": "500ms", "desc": "တည်တည်ငြိမ်ငြိမ်၊ ရှင်းရှင်းလင်းလင်း"
    },
    "8. ရုပ်ရှင်နမူနာ - Epic Drama": {
        "rate": "-12%", "pitch": "-4Hz", "volume": "+25%",
        "break": "900ms", "desc": "လေးလေး၊ ခမ်းနား၊ ရပ်နားရှည်ရှည်"
    },
    "9. ကလေးအသံ - ချစ်စရာ": {
        "rate": "+22%", "pitch": "+8Hz", "volume": "+5%",
        "break": "250ms", "desc": "အရမ်းမြန်၊ အသံအမြင့်ဆုံး"
    },
    "10. အဘိုးကြီးအသံ - ဖြည်းဖြည်း": {
        "rate": "-35%", "pitch": "-6Hz", "volume": "-10%",
        "break": "800ms", "desc": "အရမ်းဖြည်း၊ အသံနိမ့်၊ မောသံပါ"
    },
    "11. DJ/Host - ပွဲဦးဆောင်သူ": {
        "rate": "+5%", "pitch": "+2Hz", "volume": "+20%",
        "break": "350ms", "desc": "တက်တက်ကြွကြွ၊ စည်းချက်ကျကျ"
    },
    "12. ASMR - နားထဲတိုးတိုးလေး": {
        "rate": "-20%", "pitch": "-1Hz", "volume": "-60%",
        "break": "600ms", "desc": "အရမ်းတိုးတိုး၊ ဖြည်းဖြည်း၊ အသက်ရှူသံပါ"
    },
    "13. ရုံးအစည်းအဝေး - Professional": {
        "rate": "-3%", "pitch": "-1Hz", "volume": "+5%",
        "break": "400ms", "desc": "ပီပီသသ၊ ယုံကြည်မှုရှိရှိ"
    },
    "14. ပုံပြင်ပြောသူ - ကလေးပုံပြင်": {
        "rate": "-10%", "pitch": "+3Hz", "volume": "+10%",
        "break": "550ms", "desc": "နွေးထွေးတယ်၊ ဇာတ်လမ်းဆန်တယ်"
    },
    "15. Robot - စက်ရုပ်အသံ": {
        "rate": "-5%", "pitch": "-8Hz", "volume": "+0%",
        "break": "100ms", "desc": "ပြတ်ပြတ်၊ စက်ရုပ်ဆန်ဆန်၊ စိတ်ခံစားမှုမပါ"
    },
}

col1, col2 = st.columns([2, 1])
with col1:
    selected_style = st.selectbox("🎭 အသံစတိုင် 15 မျိုးထဲကရွေးပါ", list(style_presets.keys()))
    style_config = style_presets[selected_style]
with col2:
    st.write("")
    st.write("")
    auto_emphasis = st.checkbox("Auto အလေးပေး", value=True, help="အရေးကြီးစကား Auto Emphasis ထည့်မယ်")

st.info(f"**{selected_style}**\n\n{style_config['desc']}\n\nSpeed: {style_config['rate']} | Pitch: {style_config['pitch']} | Volume: {style_config['volume']}")

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

text_input = st.text_area(
    "📝 စာသားထည့်ပါ:", 
    height=200, 
    placeholder="မင်္ဂလာပါ။ ဒီနေ့ ရာသီဥတု အရမ်းကောင်းပါတယ်။ စိတ်ချမ်းသာစရာပဲ။"
)

def create_pro_ssml(text, voice, style_cfg, auto_emp):
    """SSML အပြည့်အစုံနဲ့ Style တုလုပ်မယ်"""
    
    # 1. စာကြောင်းခွဲပြီး Break ထည့်မယ်
    sentences = re.split(r'([။.!?])', text)
    processed = []
    
    for i in range(0, len(sentences)-1, 2):
        sentence = sentences[i].strip()
        punct = sentences[i+1] if i+1 < len(sentences) else ""
        
        if sentence:
            # 2. Auto Emphasis - အရေးကြီးစကားလုံး
            if auto_emp:
                keywords = ['အရမ်း', 'အရမ်းကို', 'တကယ်', 'လုံးဝ', 'အံ့သြ', 'မင်္ဂလာပါ', 'ကျေးဇူးတင်ပါတယ်', 'ချစ်တယ်', 'မုန်းတယ်', 'ကြောက်တယ်', 'ပျော်တယ်']
                for kw in keywords:
                    sentence = sentence.replace(kw, f'<emphasis level="moderate">{kw}</emphasis>')
            
            # 3. Break ထည့်မယ်
            processed.append(f"{sentence}{punct}<break time='{style_cfg['break']}'/>")
    
    full_text = " ".join(processed)
    
    # 4. SSML အပြည့်အစုံထုတ်မယ်
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

if st.button("🚀 Style နဲ့ အသံထုတ်မယ်", use_container_width=True, type="primary"):
    if not text_input.strip():
        st.error("⚠️ စာသားအရင်ထည့်ပါ!")
    else:
        with st.spinner(f'{selected_style} စတိုင်နဲ့ ထုတ်နေတယ်...'):
            try:
                ssml = create_pro_ssml(text_input, selected_voice, style_config, auto_emphasis)
                
                with st.expander("🔍 SSML Code ကြည့်မယ်"):
                    st.code(ssml, language="xml")
                
                audio_bytes = asyncio.run(generate_audio(ssml))
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
                st.error(f"❌ Error: {e}")

st.divider()
st.markdown("""
### 🎯 Style တစ်ခုချင်း ရှင်းပြချက်

| Style | သုံးသင့်တဲ့နေရာ |
| --- | --- |
| **ပျော်ရွှင်စရာ** | TikTok, Reels, ပျော်စရာဗီဒီယို |
| **ဝမ်းနည်းစရာ** | Drama, သီချင်း, ခံစားချက်ပြင်းထန်တဲ့စာ |
| **ရုပ်ရှင်နမူနာ** | Movie Trailer, Game Trailer |
| **ASMR** | အိပ်ရာဝင်ပုံပြင်, Meditation |
| **DJ/Host** | ပွဲအခမ်းအနား, YouTube Intro |
| **သတင်းကြေညာသူ** | သတင်း, Documentary |
| **ကလေးအသံ** | ကလေးပုံပြင်, ကာတွန်း |

**Tips:** စာကြောင်းအဆုံးမှာ (။) သေချာထည့်ပါ။ Auto Break ရမယ်။
""")
st.caption("✅ Card မလို | ✅ API Key မလို | ✅ Unlimited | ✅ 15 Styles")
