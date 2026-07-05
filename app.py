"""
Advanced Myanmar Text-to-Speech (TTS) Web Application
Engine: Microsoft Edge Neural TTS with Standard SSML
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
    page_title="Advanced Myanmar SSML TTS", 
    page_icon="🇲🇲", 
    layout="centered"
)

st.title("Advanced မြန်မာ AI အသံထွက်စနစ် (SSML Enabled)")
st.markdown("---")
st.write("SSML နည်းပညာကို အသုံးပြုထားသဖြင့် ပုဒ်ဖြတ်ပုဒ်ရပ်များတွင် သဘာဝကျကျ ရပ်နားပြီး လေယူလေသိမ်း ပိုမိုကောင်းမွန်ပါသည်။")

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
# 4. ASYNC CORE PROCESSING LOGIC WITH SSML
# ==========================================
async def process_tts_conversion_with_ssml(text: str, voice: str, output_path: str) -> None:
    """
    Standard SSML Method:
    - xml:lang, voice name များကို စနစ်တကျ သတ်မှတ်ထားသည်။
    - prosody rate='-10%' ဖြင့် စက်ရုပ်ဆန်မှုကို လျှော့ချထားသည်။
    """
    # XML Parsing Error မတက်စေရန် စာသားများကို သန့်စင်ခြင်း
    clean_text = text.replace("<", "&lt;").replace(">", "&gt;").replace("&", "&amp;")
    
    # ပြည့်စုံသော SSML Structure တည်ဆောက်ခြင်း
    # ⚠️ ၎င်းကို ဖွင့်သည့်အခါ Communicate တွင် 'ssml' ဟု မသုံးဘဲ 'text' ထဲသို့သာ တိုက်ရိုက်ထည့်ရသော်လည်း 
    # voice parameter ကို ထပ်မံ မထည့်သွင်းရပါ။ (Voice ကို SSML Tag ထဲတွင် သတ်မှတ်ပြီးသားဖြစ်၍)
    ssml_structure = f"""<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='my-MM'>
<voice name='{voice}'>
<prosody rate='-10%' volume='max'>
<break time='250ms'/>
{clean_text}
</prosody>
</voice>
</speak>"""
    
    # Fix: voice parameter ကို ဖယ်ထုတ်ပြီး text parameter တစ်ခုတည်းဖြင့် SSML ကို မောင်းနှင်ခြင်း
    communicate = edge_tts.Communicate(text=ssml_structure)
    await communicate.save(output_path)

# ==========================================
# 5. CONTROLLER & EXECUTION PIPELINE
# ==========================================
if st.button("AI SSML အသံဖန်တီးမယ်", type="primary", use_container_width=True):
    if not user_text.strip():
        st.warning("⚠️ ကျေးဇူးပြု၍ ပြောင်းလဲလိုသော မြန်မာစာသားများကို အရင်ဆုံး ရိုက်ထည့်ပေးပါ။")
    else:
        output_filename = "ssml_fixed_voice.mp3"
        
        with st.spinner("⏳ AI SSML Engine မှ အသံဖိုင်ကို စနစ်တကျ အကောင်းဆုံး ချက်လုပ်နေပါသည်..."):
            try:
                # Event Loop မောင်းနှင်ခြင်း
                asyncio.run(process_tts_conversion_with_ssml(user_text, voice_id, output_filename))
                
                st.success("🎉 SSML စနစ်ဖြင့် အသံဖိုင်ပြောင်းလဲခြင်း အောင်မြင်ပါသည်။")
                st.audio(output_filename, format="audio/mp3")
                
                with open(output_filename, "rb") as file:
                    st.download_button(
                        label="📥 အသံဖိုင်ကို စက်ထဲသို့ သိမ်းဆည်းရန် (Download)",
                        data=file,
                        file_name="myanmar_ai_ssml_speech.mp3",
                        mime="audio/mp3",
                        use_container_width=True
                    )
                
                if os.path.exists(output_filename):
                    os.remove(output_filename)
                    
            except Exception as e:
                st.error(f"❌ စနစ်အတွင်း အမှားအယွင်း ဖြစ်ပွားခဲ့ပါသည်။ အကြောင်းရင်း: {str(e)}")
                                           
