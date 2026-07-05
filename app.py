"""
Myanmar Text-to-Speech (TTS) Web Application
Engine: Microsoft Edge Neural TTS (edge-tts)
Framework: Streamlit
Author: AI Developer & Engineer
"""

import streamlit as st
import asyncio
import edge_tts
import os

# ==========================================
# 1. APPLICATION SETUP & CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Advanced Myanmar TTS", 
    page_icon="🇲🇲", 
    layout="centered"
)

# UI Header Sections
st.title("Advanced မြန်မာ AI အသံထွက်စနစ် (Edge-TTS)")
st.markdown("---")
st.write("Microsoft Neural AI နည်းပညာကို အသုံးပြုထားသဖြင့် အသံထွက် လေယူလေသိမ်း ပီသပြီး သဘာဝကျလှပါသည်။")

# ==========================================
# 2. VOICE MATRIX DEFINITIONS
# ==========================================
# Microsoft Edge တွင် သတ်မှတ်ထားသော မြန်မာ Neural Voice IDs များ
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

# အသံရွေးချယ်ရန် Dropdown Box
selected_voice_label = st.selectbox("အသုံးပြုမည့် AI အသံကို ရွေးချယ်ပါ -", list(VOICES.keys()))
voice_id = VOICES[selected_voice_label]

# ==========================================
# 4. ASYNC CORE CORE PROCESSING LOGIC
# ==========================================
async def process_tts_conversion(text: str, voice: str, output_path: str) -> None:
    """
    Edge-TTS SDK ကို အသုံးပြု၍ သတ်မှတ်ထားသော Voice ID ဖြင့် စာသားကို အသံဖိုင်သို့ ပြောင်းလဲပေးသည့်
    Asynchronous အဓိက လုပ်ဆောင်ချက် Function ဖြစ်သည်။
    """
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)

# ==========================================
# 5. CONTROLLER & EXECUTION PIPELINE
# ==========================================
if st.button("AI အသံဖန်တီးမယ်", type="primary", use_container_width=True):
    # စာသား အလွတ်ဖြစ်နေပါက ဆက်မလုပ်ရန် Guard Clause ဖြင့် စစ်ဆေးခြင်း
    if not user_text.strip():
        st.warning("⚠️ ကျေးဇူးပြု၍ ပြောင်းလဲလိုသော မြန်မာစာသားများကို အရင်ဆုံး ရိုက်ထည့်ပေးပါ။")
    else:
        output_filename = "generated_myanmar_voice.mp3"
        
        with st.spinner("⏳ AI Neural Engine မှ အသံဖိုင်ကို စနစ်တကျ ထုတ်လုပ်နေပါသည်..."):
            try:
                # Synchronous Streamlit Environment ထဲမှ Asynchronous Task ကို Event Loop ဖြင့် မောင်းနှင်ခြင်း
                asyncio.run(process_tts_conversion(user_text, voice_id, output_filename))
                
                # အောင်မြင်မှု ပြသခြင်းနှင့် အသံဖွင့်စနစ် (Audio Player)
                st.success("🎉 အသံဖိုင် ပြောင်းလဲခြင်း အောင်မြင်ပါသည်။ အောက်တွင် နားဆင်နိုင်ပါပြီ။")
                st.audio(output_filename, format="audio/mp3")
                
                # Binary Mode ဖြင့် ဖတ်၍ Download ရယူနိုင်ရန် စီစဉ်ခြင်း
                with open(output_filename, "rb") as file:
                    st.download_button(
                        label="📥 အသံဖိုင်ကို စက်ထဲသို့ သိမ်းဆည်းရန် (Download)",
                        data=file,
                        file_name="myanmar_ai_speech.mp3",
                        mime="audio/mp3",
                        use_container_width=True
                    )
                
                # Data Ephemerality Rule: ဆာဗာတွင် Storage ပွပွမှု မရှိစေရန် ယာယီဖိုင်ကို ချက်ချင်း ဖျက်ပစ်ခြင်း
                if os.path.exists(output_filename):
                    os.remove(output_filename)
                    
            except Exception as e:
                st.error(f"❌ စနစ်အတွင်း အမှားအယွင်း ဖြစ်ပွားခဲ့ပါသည်။ အကြောင်းရင်း: {str(e)}")
                
