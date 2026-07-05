import streamlit as st
import asyncio
import edge_tts
import io

# App Layout Configuration
st.set_page_config(
    page_title="Advanced Myanmar AI TTS", 
    page_icon="🇲🇲", 
    layout="centered"
)

st.title("Advanced မြန်မာ AI အသံထွက်စနစ်")
st.markdown("---")
st.write("ကုဒ်အမှားများ ကင်းစင်ပြီး လုပ်ငန်းသုံးအဆင့် (Production-ready) ဖြစ်သော အဆင့်မြင့် မြန်မာ AI TTS စနစ် ဖြစ်ပါသည်။")

# Voice Configuration Matrix
VOICES = {
    "🧑 ပြုံးချို (အမျိုးသားသံ - Male)": "my-MM-ThihaNeural",
    "👩 နန်းခင်ဇာ (အမျိုးသမီးသံ - Female)": "my-MM-NilarNeural"
}

# User Interface
user_text = st.text_area(
    "မြန်မာစာသားများကို ဒီနေရာမှာ ရိုက်ထည့်ပါ (Unicode Format Only):", 
    height=180,
    placeholder="ဥပမာ။ ။ နည်းပညာ တိုးတက်လာတာနဲ့အမျှ AI စနစ်တွေဟာ နေ့စဉ်ဘဝမှာ ပိုမို အရေးပါလာနေပါတယ်။"
)

selected_voice_label = st.selectbox("အသုံးပြုမည့် AI အသံကို ရွေးချယ်ပါ -", list(VOICES.keys()))
voice_id = VOICES[selected_voice_label]

# Core Async Engine Processing via Memory Stream
async def generate_tts_binary(text: str, voice: str) -> bytes:
    """
    SSML tag များကြောင့် error တက်ခြင်းကို ကာကွယ်ရန် Clean Text Parameter ကိုသုံးပြီး
    အော်ဒီယိုဖိုင်ကို Memory (Bytes) အဖြစ် တိုက်ရိုက်ထုတ်ပေးသည့် လုပ်ငန်းသုံး Core Logic ဖြစ်သည်။
    """
    communicate = edge_tts.Communicate(
        text=text, 
        voice=voice,
        rate="-10%",  # သဘာဝကျသော လေယူလေသိမ်းရရှိရန် စကားပြောနှုန်း ၁၀% လျှော့ချထားသည်
        volume="+0%"
    )
    
    audio_buffer = io.BytesIO()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_buffer.write(chunk["data"])
            
    audio_buffer.seek(0)
    return audio_buffer.getvalue()

# Execution Pipeline
if st.button("AI အသံဖန်တီးမယ်", type="primary", use_container_width=True):
    if not user_text.strip():
        st.warning("⚠️ ကျေးဇူးပြု၍ ပြောင်းလဲလိုသော မြန်မာစာသားများကို အရင်ဆုံး ရိုက်ထည့်ပေးပါ။")
    else:
        with st.spinner("⏳ AI Engine မှ အသံဖိုင်ကို စနစ်တကျ အကောင်းဆုံး ချက်လုပ်နေပါသည်..."):
            try:
                # Async event loop အား memory buffering ဖြင့် မောင်းနှင်ခြင်း
                audio_bytes = asyncio.run(generate_tts_binary(user_text, voice_id))
                
                st.success("🎉 အသံဖိုင်ပြောင်းလဲခြင်း အောင်မြင်ပါသည်။")
                
                # UI သို့ ဒေတာကို တိုက်ရိုက် Stream လုပ်၍ ပြသခြင်း
                st.audio(audio_bytes, format="audio/mp3")
                
                # Local Storage ထဲတွင် ဖိုင်သိမ်းဆည်းစရာမလိုဘဲ Memory မှ တိုက်ရိုက်ဒေါင်းလုဒ်ရယူခြင်း
                st.download_button(
                    label="📥 အသံဖိုင်ကို စက်ထဲသို့ သိမ်းဆည်းရန် (Download)",
                    data=audio_bytes,
                    file_name="myanmar_ai_speech.mp3",
                    mime="audio/mp3",
                    use_container_width=True
                )
                    
            except Exception as e:
                st.error(f"❌ စနစ်အတွင်း အမှားအယွင်း ဖြစ်ပွားခဲ့ပါသည်။ အကြောင်းရင်း: {str(e)}")
                
