import streamlit as st
import asyncio
import edge_tts
from openai import OpenAI
import io

# 1. APPLICATION SETUP
st.set_page_config(
    page_title="Hybrid Myanmar AI TTS", 
    page_icon="🇲🇲", 
    layout="centered"
)

st.title("Advanced Hybrid မြန်မာ AI အသံထွက်စနစ်")
st.markdown("---")
st.write("Premium OpenAI (Studio) နှင့် Free Edge-TTS အင်ဂျင်နှစ်ခုလုံးကို ဉာဏ်ရည်ထက်မြက်စွာ ပေါင်းစပ်ထားသော စနစ်ဖြစ်ပါသည်။")

# 2. VOICE DEFINITIONS MATCHING
OPENAI_VOICES = {
    "🎙️ Alloy (သဘာဝကျသော အသံစုံ)": "alloy",
    "🎙️ Echo (အမျိုးသားသံပြတ်သား)": "echo",
    "🎙️ Shimmer (အမျိုးသမီးသံကြည်လင်)": "shimmer"
}

EDGE_VOICES = {
    "🧑 ပြုံးချို (အမျိုးသားသံ - Free)": "my-MM-ThihaNeural",
    "👩 နန်းခင်ဇာ (အမျိုးသမီးသံ - Free)": "my-MM-NilarNeural"
}

# 3. USER INTERFACE (UI) LAYOUT
user_text = st.text_area(
    "မြန်မာစာသားများကို ဒီနေရာမှာ ရိုက်ထည့်ပါ -", 
    height=180,
    placeholder="စာသားများ ရိုက်ထည့်ပါ..."
)

# အင်ဂျင်ရွေးချယ်မှုအပိုင်း
engine_mode = st.radio(
    "အသံထုတ်လုပ်မည့် စနစ်ကို ရွေးချယ်ပါ -",
    ["🆓 အခမဲ့စနစ် (Standard Free)", "✨ စတူဒီယိုအဆင့်မြင့်စနစ် (OpenAI Premium)"],
    horizontal=True
)

if engine_mode == "🆓 အခမဲ့စနစ် (Standard Free)":
    selected_voice_label = st.selectbox("အသုံးပြုမည့် AI အသံကို ရွေးချယ်ပါ -", list(EDGE_VOICES.keys()))
    voice_id = EDGE_VOICES[selected_voice_label]
else:
    selected_voice_label = st.selectbox("အသုံးပြုမည့် Premium Voice ကို ရွေးချယ်ပါ -", list(OPENAI_VOICES.keys()))
    voice_id = OPENAI_VOICES[selected_voice_label]

# 4. CORE ENGINE PIPELINES
async def generate_edge_tts(text: str, voice: str) -> bytes:
    """အလကားရပြီး စိတ်ချရသော Edge-TTS Engine"""
    communicate = edge_tts.Communicate(text=text, voice=voice, rate="-10%")
    audio_buffer = io.BytesIO()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_buffer.write(chunk["data"])
    audio_buffer.seek(0)
    return audio_buffer.getvalue()

def generate_openai_tts(text: str, voice: str) -> bytes:
    """အသံအကောင်းဆုံး OpenAI Premium Engine"""
    client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY", ""))
    response = client.audio.speech.create(
        model="tts-1-hd",
        voice=voice,
        input=text
    )
    return response.content

# 5. EXECUTION CONTROLLER
if st.button("AI အသံဖန်တီးမယ်", type="primary", use_container_width=True):
    if not user_text.strip():
        st.warning("⚠️ ကျေးဇူးပြု၍ စာသားအရင်ရိုက်ထည့်ပါ။")
    else:
        with st.spinner("⏳ AI စနစ်မှ အသံဖိုင်ကို အကောင်းဆုံး ချက်လုပ်နေပါသည်..."):
            audio_bytes = None
            success_mode = ""
            
            # အသုံးပြုသူက Premium ရွေးထားလျှင်
            if engine_mode == "✨ စတူဒီယိုအဆင့်မြင့်စနစ် (OpenAI Premium)":
                try:
                    audio_bytes = generate_openai_tts(user_text, voice_id)
                    success_mode = "Premium Studio Quality"
                except Exception as e:
                    # OpenAI တွင် ပိုက်ဆံကုန်ခြင်း သို့မဟုတ် Error တက်ပါက အလကားစနစ်သို့ အလိုအလျောက် ပြောင်းလဲခြင်း (Smart Fallback Architecture)
                    st.info("ℹ️ OpenAI Quota ကုန်နေသဖြင့် အခမဲ့ Edge-TTS စနစ်ဖြင့် အလိုအလျောက် ပြောင်းလဲထုတ်လုပ်ပေးနေပါသည်။")
                    audio_bytes = asyncio.run(generate_edge_tts(user_text, "my-MM-ThihaNeural"))
                    success_mode = "Standard Free (Auto-Fallback)"
            
            # အသုံးပြုသူက Free စနစ်ရွေးထားလျှင်
            else:
                audio_bytes = asyncio.run(generate_edge_tts(user_text, voice_id))
                success_mode = "Standard Free Quality"
            
            # OUTPUT DISPLAY & DOWNLOAD
            if audio_bytes:
                st.success(f"🎉 အသံဖိုင်ပြောင်းလဲခြင်း အောင်မြင်ပါသည် ({success_mode})")
                st.audio(audio_bytes, format="audio/mp3")
                
                st.download_button(
                    label="📥 အသံဖိုင်ကို ရယူရန် (Download)",
                    data=audio_bytes,
                    file_name="myanmar_ai_speech.mp3",
                    mime="audio/mp3",
                    use_container_width=True
)
    
