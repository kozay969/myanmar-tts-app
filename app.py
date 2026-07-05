import streamlit as st
import asyncio
import edge_tts
from openai import OpenAI
import io

# 1. APPLICATION SETUP & CONFIGURATION
st.set_page_config(
    page_title="Advanced Myanmar AI TTS Pro", 
    page_icon="🇲🇲", 
    layout="centered"
)

st.title("Advanced Hybrid မြန်မာ AI အသံထွက်စနစ် (Pro)")
st.markdown("---")
st.write("အသံနှုန်းထား (Speed) နှင့် လေယူလေသိမ်း (Tone) ကိုပါ စိတ်ကြိုက်ထိန်းချုပ်နိုင်သော လုပ်ငန်းသုံးအဆင့် TTS စနစ် ဖြစ်ပါသည်။")

# 2. CONFIGURATION MATRICES
OPENAI_VOICES = {
    "🎙️ Alloy (သဘာဝကျသော အသံစုံ)": "alloy",
    "🎙️ Echo (အမျိုးသားသံပြတ်သား)": "echo",
    "🎙️ Shimmer (အမျိုးသမီးသံကြည်လင်)": "shimmer"
}

EDGE_VOICES = {
    "🧑 ပြုံးချို (အမျိုးသားသံ - Free)": "my-MM-ThihaNeural",
    "👩 နန်းခင်ဇာ (အမျိုးသမီးသံ - Free)": "my-MM-NilarNeural"
}

# OpenAI TTS ၏ လေယူလေသိမ်းကို လမ်းညွှန်ရန်အတွက် အသုံးပြုမည့် Tone Prompt Contexts
TONE_PROMPTS = {
    "😊 ပုံမှန် လေယူလေသိမ်း (Default)": "",
    "📢 တက်ကြွလှုံ့ဆော်သော သံ (Energetic/Advertisement)": "[Tone: Energetic, enthusiastic, and clear. Expressive and high energy.] ",
    "📰 တည်ငြိမ်သော သတင်းဖတ်သံ (Professional News/Documentary)": "[Tone: Professional, calm, authoritative, and steady. Formal news anchoring style.] ",
    "🧘 အေးဆေးသိမ်မွေ့သော ပုံပြင်ပြောသံ (Calm/Storytelling)": "[Tone: Soft, warm, soothing, and slow-paced. Emotional and storytelling style.] "
}

# 3. USER INTERFACE (UI) ELEMENTS
user_text = st.text_area(
    "မြန်မာစာသားများကို ဒီနေရာမှာ ရိုက်ထည့်ပါ -", 
    height=150,
    placeholder="စာသားများ ရိုက်ထည့်ပါ..."
)

engine_mode = st.radio(
    "အသံထုတ်လုပ်မည့် စနစ်ကို ရွေးချယ်ပါ -",
    ["🆓 အခမဲ့စနစ် (Standard Free)", "✨ စတူဒီယိုအဆင့်မြင့်စနစ် (OpenAI Premium)"],
    horizontal=True
)

# 🎛️ Advanced Control Panel
st.subheader("🎛️ အသံချိန်ညှိမှု Panel")
col1, col2 = st.columns([1, 1])

with col1:
    if engine_mode == "🆓 အခမဲ့စနစ် (Standard Free)":
        selected_voice_label = st.selectbox("အသုံးပြုမည့် AI အသံကို ရွေးချယ်ပါ -", list(EDGE_VOICES.keys()))
        voice_id = EDGE_VOICES[selected_voice_label]
    else:
        selected_voice_label = st.selectbox("အသုံးပြုမည့် Premium Voice ကို ရွေးချယ်ပါ -", list(OPENAI_VOICES.keys()))
        voice_id = OPENAI_VOICES[selected_voice_label]

with col2:
    speech_speed = st.slider(
        "စကားပြောနှုန်း အနှေးအမြန် (Speed) -",
        min_value=0.5, max_value=1.5, value=0.9, step=0.1, format="%fx"
    )

# Tone Selection UI (OpenAI Premium မုဒ်တွင်သာ ၎င်းစနစ်ကို အပြည့်အဝ အသုံးချနိုင်မည်)
selected_tone_label = st.selectbox(
    "အသံ၏ လေယူလေသိမ်း (Tone Style) ကို ရွေးချယ်ပါ -", 
    list(TONE_PROMPTS.keys()),
    disabled=(engine_mode == "🆓 အခမဲ့စနစ် (Standard Free)")  # Free mode တွင် ပိတ်ထားမည်
)
tone_prefix = TONE_PROMPTS[selected_tone_label]

if engine_mode == "🆓 အခမဲ့စနစ် (Standard Free)":
    st.caption("💡 *မှတ်ချက်: အသံ Tone စနစ်သည် OpenAI Premium တွင်သာ စွမ်းဆောင်ရည် အပြည့်အဝရရှိပါမည်။*")

# 4. CORE ENGINE PIPELINES
async def generate_edge_tts(text: str, voice: str, speed_multiplier: float) -> bytes:
    percentage_change = int((speed_multiplier - 1.0) * 100)
    rate_string = f"{'+' if percentage_change >= 0 else ''}{percentage_change}%"
    
    communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate_string)
    audio_buffer = io.BytesIO()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_buffer.write(chunk["data"])
    audio_buffer.seek(0)
    return audio_buffer.getvalue()

def generate_openai_tts(text: str, voice: str, speed_value: float, tone_context: str) -> bytes:
    client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY", ""))
    
    # Context Injection Technique: စာသား၏အရှေ့တွင် Tone Prompt ကို ပေါင်းစပ်ပေးခြင်းဖြင့် AI ၏ လေယူလေသိမ်းကို ထိန်းချုပ်သည်
    full_input = f"{tone_context}{text}"
    
    response = client.audio.speech.create(
        model="tts-1-hd",
        voice=voice,
        input=full_input,
        speed=speed_value
    )
    return response.content

# 5. CONTROLLER EXECUTION PIPELINE
if st.button("AI အသံဖန်တီးမယ်", type="primary", use_container_width=True):
    if not user_text.strip():
        st.warning("⚠️ ကျေးဇူးပြု၍ စာသားအရင်ရိုက်ထည့်ပါ။")
    else:
        with st.spinner("⏳ စိတ်ကြိုက်ပြင်ဆင်ထားသော Tone ဖြင့် AI အသံဖိုင်ကို ချက်လုပ်နေပါသည်..."):
            audio_bytes = None
            mode_info = f"Speed: {speech_speed}x | {selected_tone_label.split(' ')[1]}"
            
            if engine_mode == "✨ စတူဒီယိုအဆင့်မြင့်စနစ် (OpenAI Premium)":
                try:
                    audio_bytes = generate_openai_tts(user_text, voice_id, speech_speed, tone_prefix)
                    success_info = f"Premium Studio ({mode_info})"
                except Exception as e:
                    st.info("ℹ️ OpenAI Quota ပြည့်နေသဖြင့် အခမဲ့ Edge-TTS စနစ်ဖြင့် အလိုအလျောက် အစားထိုးပေးထားပါသည်။")
                    audio_bytes = asyncio.run(generate_edge_tts(user_text, "my-MM-ThihaNeural", speech_speed))
                    success_info = f"Standard Free Fallback (Speed: {speech_speed}x)"
            else:
                audio_bytes = asyncio.run(generate_edge_tts(user_text, voice_id, speech_speed))
                success_info = f"Standard Free (Speed: {speech_speed}x)"
            
            # OUTPUT DISPLAY
            if audio_bytes:
                st.success(f"🎉 အသံဖိုင်ပြောင်းလဲခြင်း အောင်မြင်ပါသည် ({success_info})")
                st.audio(audio_bytes, format="audio/mp3")
                
                st.download_button(
                    label="📥 အသံဖိုင်ကို ရယူရန် (Download)",
                    data=audio_bytes,
                    file_name="myanmar_ai_speech_custom.mp3",
                    mime="audio/mp3",
                    use_container_width=True
        )
                
