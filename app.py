"""
Advanced Myanmar Text-to-Speech (TTS) Web Application
Engine: Microsoft Edge Neural TTS (Clean Text Implementation)
Framework: Streamlit
"""

import streamlit as st
import asyncio
import edge_tts
import os

# ==========================================
# 1. APPLICATION SETUP & CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Advanced Myanmar AI TTS", 
    page_icon="🇲🇲", 
    layout="centered"
)

st.title("Advanced မြန်မာ AI အသံထွက်စနစ်")
st.markdown("---")
st.write("ကုဒ်အမှားများ ကင်းစင်ပြီး လေယူလေသိမ်း ပီသသော မြန်မာ AI အသံထွက်စနစ် ဖြစ်ပါသည်။")

# ==========================================
# 2. VOICE MATRIX DEFINITIONS
# ==========================================
VOICES = {
    "🧑 ပြုံးချို (အမျိုးသားသံ - Male)": "my-MM-ThihaNeural",
    "👩 နန်းခင်ဇာ (အမျိုးသမီးသံ - Female)": "my-MM-NilarNeural"
}

# ==========================================
# 3. USER INTERFACE (UI) ELEMENTS
# ==========================================
user_text = st.text_area(
    "မြန်မာစာသားများကို ဒီနေရာမှာ ရိုက်ထည့်ပါ (Unicode Format Only):", 
    height=180,
    placeholder="ဥပမာ။ ။ နည်းပညာ တိုးတက်လာတာနဲ့အမျှ AI စနစ်တွေဟာ နေ့စဉ်ဘဝမှာ ပိုမို အရေးပါလာနေပါတယ်။"
)

selected_voice_label = st.selectbox("အသုံးပြုမည့် AI အသံကို ရွေးချယ်ပါ -", list(VOICES.keys()))
voice_id = VOICES[selected_voice_label]

# ==========================================
# 4. ASYNC CORE PROCESSING LOGIC (CLEAN PARAMETERS)
# ==========================================
async def process_tts_conversion(text: str, voice: str, output_path: str) -> None:
    """
    SSML Tags များ သုံးစရာမလိုဘဲ Python API parameters များဖြင့်သာ အသံကို ထိန်းချုပ်ခြင်း။
    ၎င်းသည် Tag များ လိုက်ဖတ်သည့် ပြဿနာကို ၁၀၀% ကာကွယ်ပေးသည်။
    """
    # စကားပြောနှုန်းကို ၁၀% လျှော့ချ၍ ပိုမိုပီသအောင် လုပ်ဆောင်ခြင်း
    # rate="-10%" သည် စက်ရုပ်ဆန်မှုကို လျှော့ချပေးပြီး သဘာဝကျစေသည်
    communicate = edge_tts.Communicate(
        text=text, 
        voice=voice,
        rate="-10%",
        volume="+0%"
    )
    await communicate.save(output_path)

# ==========================================
# 5. CONTROLLER & EXECUTION PIPELINE
# ==========================================
if st.button("AI အသံဖန်တီးမယ်", type="primary", use_container_width=True):
    if not user_text.strip():
        st.warning("⚠️ ကျေးဇူးပြု၍ ပြောင်းလဲလိုသော မြန်မာစာသားများကို အရင်ဆုံး ရိုက်ထည့်ပေးပါ။")
    else:
        output_filename = "clean_myanmar_voice.mp3"
        
        with st.spinner("⏳ AI Engine မှ အသံဖိုင်ကို စနစ်တကျ အကောင်းဆုံး ချက်လုပ်နေပါသည်..."):
            try:
                # Event Loop မောင်းနှင်ခြင်း
                asyncio.run(process_tts_conversion(user_text, voice_id, output_filename))
                
                st.success("🎉 အသံဖိုင်ပြောင်းလဲခြင်း အောင်မြင်ပါသည်။")
                st.audio(output_filename, format="audio/mp3")
                
                with open(output_filename, "rb") as file:
                    st.download_button(
                        label="📥 အသံဖိုင်ကို စက်ထဲသို့ သိမ်းဆည်းရန် (Download)",
                        data=file,
                        file_name="myanmar_ai_speech.mp3",
                        mime="audio/mp3",
                        use_container_width=True
                    )
                
                # Cleanup ယာယီဖိုင်ဖျက်ခြင်း
                if os.path.exists(output_filename):
                    os.remove(output_filename)
                    
            except Exception as e:
                st.error(f"❌ စနစ်အတွင်း အမှားအယွင်း ဖြစ်ပွားခဲ့ပါသည်။ အကြောင်းရင်း: {str(e)}")
                                 
