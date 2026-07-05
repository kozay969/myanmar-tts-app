import streamlit as st
from openai import OpenAI
import io

# 1. App Configuration
st.set_page_config(page_title="Studio-Grade Myanmar AI TTS", page_icon="🇲🇲")
st.title("Studio-Grade မြန်မာ AI အသံထွက်စနစ်")
st.markdown("---")

# OpenAI Client Initialization (Securely fetching API key)
# Streamlit secrets ကိုသုံးခြင်းဖြင့် GitHub ပေါ်တွင် Key များ ပေါက်ကြားမှုကို ၁၀၀% ကာကွယ်ပေးသည်
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# 2. Advanced Voice Matrix (Premium Human-like Voices)
# OpenAI ၏ HD Models များသည် စကားလုံးအဖြတ်အတောက်နှင့် လေယူလေသိမ်းကို လူသားအတိုင်း ဖန်တီးပေးသည်
VOICES = {
    "🎙️ Alloy (သဘာဝကျသော အသံစုံ)": "alloy",
    "🎙️ Echo (ပီသပြတ်သားသော အမျိုးသားသံ)": "echo",
    "🎙️ Shimmer (ကြည်လင်သော အမျိုးသမီးသံ)": "shimmer"
}

# 3. User Interface Layout
user_text = st.text_area(
    "မြန်မာစာသားများကို ဒီနေရာမှာ ရိုက်ထည့်ပါ -", 
    height=180,
    placeholder="ဥပမာ။ ။ နည်းပညာ တိုးတက်လာတာနဲ့အမျှ AI စနစ်တွေဟာ နေ့စဉ်ဘဝမှာ ပိုမို အရေးပါလာနေပါတယ်။"
)

selected_voice = st.selectbox("အသုံးပြုမည့် Premium Voice ကို ရွေးချယ်ပါ -", list(VOICES.keys()))
voice_id = VOICES[selected_voice]

# 4. Core Audio Generation Pipeline
def generate_studio_audio(text: str, voice: str) -> bytes:
    """
    OpenAI TTS-1-HD model ကိုသုံးပြီး Buffer အဖြစ် Memory ပေါ်တွင် တိုက်ရိုက်အသံထုတ်လုပ်ပေးသည့် Core Logic။
    HD model သည် Compression rate နည်းပြီး Audio frequency ပိုမိုမြင့်မားသဖြင့် Studio အရည်အသွေး ရရှိစေသည်။
    """
    response = client.audio.speech.create(
        model="tts-1-hd", # High-Definition Model အား အသုံးပြုထားသည်
        voice=voice,
        input=text
    )
    
    # Binary Response ကို Memory ပေါ်တွင် တိုက်ရိုက် Stream လုပ်ခြင်း
    return response.content

# 5. Execution Logic
if st.button("Premium AI အသံဖန်တီးမယ်", type="primary", use_container_width=True):
    if not user_text.strip():
        st.warning("⚠️ ကျေးဇူးပြု၍ စာသားရိုက်ထည့်ပေးပါ။")
    else:
        with st.spinner("⏳ Studio Quality ဖြင့် အသံဖိုင်ကို အကောင်းဆုံး ချက်လုပ်နေပါသည်..."):
            try:
                # API Call & Memory Handling
                audio_bytes = generate_studio_audio(user_text, voice_id)
                
                st.success("🎉 အဆင့်မြင့် Premium အသံဖိုင် ထွက်ပေါ်လာပါပြီ။")
                st.audio(audio_bytes, format="audio/mp3")
                
                # Fileless Download Mechanism
                st.download_button(
                    label="📥 Premium အသံဖိုင်ကို ရယူရန် (Download)",
                    data=audio_bytes,
                    file_name="myanmar_premium_speech.mp3",
                    mime="audio/mp3",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"❌ စနစ်အတွင်း ချို့ယွင်းချက် ရှိနေပါသည်။ API Key မှန်မမှန် ပြန်စစ်ပေးပါ။ အကြောင်းရင်း: {str(e)}")
    
