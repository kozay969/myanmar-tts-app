import streamlit as st
import edge_tts
import asyncio
import tempfile
import os

st.set_page_config(page_title="Myanmar TTS Pro", page_icon="🎭")

st.title("🎭 Myanmar TTS Pro - Style 15 မျိုး")
st.caption("အလုပ်လုပ်တာ သေချာတဲ့ Version ✅")

voice_options = {
    "Nilar - မိန်းကလေး": "my-MM-NilarNeural",
    "Thiha - ယောက်ျားလေး": "my-MM-ThihaNeural",
}

voice_name = st.selectbox("🎤 အသံရွေး", list(voice_options.keys()))
voice = voice_options[voice_name]

styles = {
    "1. သာမန်": {"rate": "+0%", "pitch": "+0Hz", "vol": "+0%"},
    "2. ပျော်ရွှင်စရာ": {"rate": "+12%", "pitch": "+5Hz", "vol": "+15%"},
    "3. ဝမ်းနည်းစရာ": {"rate": "-30%", "pitch": "-5Hz", "vol": "-15%"},
    "4. ဒေါသထွက်စရာ": {"rate": "+15%", "pitch": "+4Hz", "vol": "+40%"},
    "5. ကြောက်လန့်စရာ": {"rate": "+20%", "pitch": "+6Hz", "vol": "+10%"},
    "6. တိုးတိုးလေး": {"rate": "-15%", "pitch": "-2Hz", "vol": "-50%"},
    "7. သတင်းကြေညာသူ": {"rate": "-8%", "pitch": "-3Hz", "vol": "+10%"},
    "8. ရုပ်ရှင်နမူနာ": {"rate": "-12%", "pitch": "-4Hz", "vol": "+25%"},
    "9. ကလေးအသံ": {"rate": "+22%", "pitch": "+8Hz", "vol": "+5%"},
    "10. အဘိုးကြီးအသံ": {"rate": "-35%", "pitch": "-6Hz", "vol": "-10%"},
    "11. DJ/Host": {"rate": "+5%", "pitch": "+2Hz", "vol": "+20%"},
    "12. ASMR": {"rate": "-20%", "pitch": "-1Hz", "vol": "-60%"},
    "13. ရုံးအစည်းအဝေး": {"rate": "-3%", "pitch": "-1Hz", "vol": "+5%"},
    "14. ပုံပြင်ပြောသူ": {"rate": "-10%", "pitch": "+3Hz", "vol": "+10%"},
    "15. Robot": {"rate": "-5%", "pitch": "-8Hz", "vol": "+0%"},
}

style_name = st.select
