import streamlit as st
import asyncio, edge_tts, tempfile, textwrap
from pydub import AudioSegment

st.set_page_config(page_title="Prompt TTS Pro + Clone", layout="wide")
st.title("🎙️ Myanmar TTS Pro")

tab1, tab2 = st.tabs(["📖 Long Story (1647+ Unlimited)", "🎤 Voice Clone (200)"])

# === TAB 1: UNLIMITED - မင်းရဲ့ 1647 လုံး story အတွက် ===
with tab1:
    st.success("✅ ဒီ Tab က စာလုံးရေ Unlimited - 5000 လုံးထိ ရတယ်")
    text = st.text_area("စာ ထည့်ပါ - Ben, Cora story", height=300, key="long")
    voice = st.selectbox("အသံ", ["my-MM-NilarNeural", "my-MM-ThihaNeural"])
    
    if st.button("🚀 Long Audio ထုတ်မယ်", type="primary", use_container_width=True):
        if text:
            async def gen():
                chunks = textwrap.wrap(text, 400)
                st.info(f"{len(text)} လုံး -> {len(chunks)} ပိုင်း")
                audios = []
                prog = st.progress(0)
                for i, ch in enumerate(chunks):
                    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
                    comm = edge_tts.Communicate(ch, voice)
                    await comm.save(tmp)
                    audios.append(AudioSegment.from_file(tmp))
                    prog.progress((i+1)/len(chunks))
                final = sum(audios, AudioSegment.empty())
                out = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
                final.export(out, format="mp3")
                st.audio(out)
                st.download_button("📥 Download MP3", open(out,'rb'), "myanmar_long.mp3", use_container_width=True)
            
            asyncio.run(gen())

# === TAB 2: Clone - Short only ===
with tab2:
    st.warning("Clone က 200 လုံး limit ရှိတယ် - စာတို အတွက်ပဲ")
    st.components.v1.iframe("https://voxcpm.app", height=800)
