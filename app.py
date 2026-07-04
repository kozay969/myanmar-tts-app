import streamlit as st
import edge_tts
import tempfile
import os
import asyncio

st.set_page_config(page_title="Myanmar TTS Pro", page_icon="🎭", layout="centered")

st.title("🎭 Myanmar TTS - Style 15 မျိုး")
st.caption("SyntaxError Fix ပြီးသား ✅")

voice_options = {
    "မြန်မာ - Nilar (မိန်းကလေး)": "my-MM-NilarNeural",
    "မြန်မာ - Thiha (ယောက်ျားလေး)": "my-MM-ThihaNeural",
}

selected_voice_name = st.selectbox("🎤 အသံ", list(voice_options.keys()))
selected_voice = voice_options[selected_voice_name]

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

selected_style = st.selectbox("🎭 အသံစတိုင်", list(style_presets.keys()))
style_config = style_presets[selected_style]

st.info(f"**{selected_style}** | Speed: {style_config['rate']} | Pitch: {style_config['pitch']} | Volume: {style_config['volume']}")

with st.expander("⚙️ ကိုယ်တိုင်ချိန်မယ်"):
    c1, c2, c3 = st.columns(3)
    with c1:
        custom_rate = st.slider("Speed", -50, 50, int(style_config['rate'].replace('%','').replace('+','')))
    with c2:
        custom_pitch = st.slider("Pitch", -10, 10, int(style_config['pitch'].replace('Hz','').replace('+','')))
    with c3:
        custom_volume = st.slider("Volume", -50, 50, int(style_config['volume'].replace('%','').replace('+','')))
    
    style_config['rate
