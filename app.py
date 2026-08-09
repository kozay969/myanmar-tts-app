import streamlit as st
import edge_tts
import asyncio
import tempfile
import os

st.set_page_config(page_title="Prompt TTS Pro + Clone", page_icon="🎙️", layout="wide")
st.title("🎙️ Prompt TTS Pro + Clone Unlimited")

tab1, tab2 = st.tabs(["🗣️ Edge TTS (မူရင်း)", "🎤 Unlimited Clone (Fixed)"])

# TAB 1 - မင်းရဲ့ မူရင်း (မထိဘူး)
with tab1:
    # ... မင်းရဲ့ အရင် Tab1 code အကုန် ဒီမှာ ပြန်ထည့် ...
    st.write("Edge TTS Tab")

# TAB 2 - Unlimited Clone - No External API
with tab2:
    st.markdown("### 🎤 Unlimited Clone - Server ပေါ်မှာတင် လုပ်မယ်")
    st.success("200 limit မရှိ, HF Space block မရှိ - 1647 လုံးလည်း ရတယ်")
    
    from TTS.api import TTS
    
    @st.cache_resource
    def load_model():
        return TTS("tts_models/multilingual/multi-dataset/your_tts", gpu=False)
    
    ref_audio = st.file_uploader("🎙️ Reference အသံ (5-10s) - နမုနာဖိုင်.flac", type=['mp3','wav','flac','m4a'], key="ref_final")
    clone_text = st.text_area("📝 စာ (1000+ လုံး ရတယ်)", height=250, value="", key="txt_final")
    lang = st.selectbox("Language", ["my", "en", "my-mm"], index=0)
    
    if st.button("🚀 Unlimited ထုတ်မယ် (1647 လုံး)", type="primary", use_container_width=True):
        if not ref_audio or not clone_text.strip():
            st.warning("အသံနဲ့ စာ ထည့်ပါ")
        else:
            with st.spinner("Model loading... ပထမအကြိမ် 1-2 မိနစ်ကြာမယ်"):
                try:
                    tts = load_model()
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                        tmp.write(ref_audio.read())
                        ref_path = tmp.name
                    
                    # Auto chunk 1647 -> 300 တစ်ပိုင်း
                    import textwrap
                    chunks = textwrap.wrap(clone_text, width=300, break_long_words=False)
                    st.info(f"{len(clone_text)} လုံး -> {len(chunks)} ပိုင်း ခွဲထုတ်နေတယ်")
                    
                    final_files = []
                    progress = st.progress(0)
                    for i, chunk in enumerate(chunks):
                        out_path = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
                        tts.tts_to_file(text=chunk, speaker_wav=ref_path, language=lang if lang!='my-mm' else 'en', file_path=out_path)
                        final_files.append(out_path)
                        progress.progress((i+1)/len(chunks))
                    
                    # Merge with pydub
                    from pydub import AudioSegment
                    combined = AudioSegment.empty()
                    for f in final_files:
                        combined += AudioSegment.from_wav(f) + AudioSegment.silent(duration=300)
                    
                    final_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
                    combined.export(final_path, format="mp3")
                    
                    st.success("✅ ပြီးပြီ - Unlimited!")
                    st.audio(final_path)
                    with open(final_path, 'rb') as f:
                        st.download_button("📥 MP3 Download", f, "cloned_unlimited.mp3", "audio/mp3", use_container_width=True)
                        
                except Exception as e:
                    st.error(f"Error: {e}")
                    st.code(str(e))
    
