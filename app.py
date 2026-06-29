import streamlit as st
import zipfile
import io
import time
from google import genai
from google.genai import types

# 1. UI Styling (လန်းဆန်းသော UI အတွက်)
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .stButton>button { width: 100%; border-radius: 20px; background: linear-gradient(90deg, #ff4b4b, #ff9e4b); color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. Page Setup
st.set_page_config(page_title="Gemini TTS Pro", page_icon="🎙️", layout="centered")
st.title("🎙️ Gemini 2.5 Flash TTS Pro")
st.markdown("---")

# 3. API Key Check
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("❌ GEMINI_API_KEY ကို Streamlit Secrets တွင် စစ်ဆေးပါ")
    st.stop()
client = genai.Client(api_key=api_key)

# 4. Helper Function (စာသားခွဲခြင်း)
def split_text(text, max_chars=800):
    text = text.strip()
    if len(text) <= max_chars: return [text]
    chunks = []
    while len(text) > max_chars:
        pos = text.rfind("။", 0, max_chars)
        if pos == -1: pos = text.rfind(" ", 0, max_chars)
        if pos == -1: pos = max_chars
        chunks.append(text[:pos + 1].strip())
        text = text[pos + 1:].strip()
    if text: chunks.append(text)
    return chunks

# 5. UI Elements
voice = st.selectbox("🎙️ Voice Select", ["Kore", "Aoede", "Charon", "Fenrir", "Puck"])
text_input = st.text_area("စာသားများ ထည့်သွင်းပါ:", height=200, placeholder="ဒီနေရာမှာ စာသားရိုက်ထည့်ပါ...")

# 6. Generation Logic (Error Handling + Delay ပါဝင်သည်)
if st.button("🚀 GENERATE & ZIP"):
    if not text_input.strip():
        st.warning("စာသားအနည်းငယ် ထည့်သွင်းပေးပါ")
    else:
        try:
            chunks = split_text(text_input)
            progress_bar = st.progress(0)
            zip_buffer = io.BytesIO()
            
            with zipfile.ZipFile(zip_buffer, 'w') as zf:
                for i, chunk in enumerate(chunks):
                    # Rate Limit ကျော်လွှားရန် 30 စက္ကန့် စောင့်ခြင်း
                    if i > 0:
                        st.info(f"Limit မကျော်အောင် အပိုင်း {i+1} အတွက် 30 စက္ကန့် စောင့်နေပါသည်...")
                        time.sleep(30)
                    
                    response = client.models.generate_content(
                        model="gemini-2.5-flash-preview-tts",
                        contents=chunk,
                        config=types.GenerateContentConfig(
                            response_modalities=["AUDIO"],
                            speech_config=types.SpeechConfig(
                                voice_config=types.VoiceConfig(
                                    prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice)
                                )
                            ),
                        ),
                    )
                    audio_data = response.candidates[0].content.parts[0].inline_data.data
                    zf.writestr(f"audio_part_{i+1}.wav", audio_data)
                    progress_bar.progress((i + 1) / len(chunks))
            
            st.balloons()
            st.success("✅ အောင်မြင်စွာ ဖန်တီးပြီးပါပြီ!")
            st.download_button("📥 Download ZIP", zip_buffer.getvalue(), "gemini_tts.zip", "application/zip", use_container_width=True)
            
        except Exception as e:
            st.error(f"🛡️ Error ဖြစ်ပေါ်ပါသည်: {e}")

