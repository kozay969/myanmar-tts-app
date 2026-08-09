import streamlit as st
import asyncio
import edge_tts
import tempfile
import textwrap

st.set_page_config(page_title="Myanmar TTS Pro", layout="wide")
st.title("🎙️ Myanmar TTS Pro - Unlimited")

tab1, tab2 = st.tabs(["📖 Long Story (Unlimited)", "🎤 Clone (200)"])

with tab1:
    st.success("✅ 1647 လုံး, 5000 လုံး Unlimited - pydub မလို")
    text = st.text_area("စာထည့်ပါ (Ben, Cora story)", height=300)
    voice = st.selectbox("အသံ", ["my-MM-NilarNeural", "my-MM-ThihaNeural"])

    if st.button("🚀 Unlimited ထုတ်မယ်", type="primary", use_container_width=True):
        if not text:
            st.warning("စာ ထည့်ဦး")
        else:
            async def gen_long():
                # 400 လုံးစီ ခွဲပြီး တစ်ဖိုင်တည်း ဆက်တိုက်ရေး - pydub မလို
                chunks = textwrap.wrap(text, 600, break_long_words=False) if len(text) > 600 else [text]
                st.info(f"{len(text)} လုံး -> {len(chunks)} ပိုင်း ပေါင်းထုတ်မယ်")

                out_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
                # edge-tts ကို chunk တစ်ခုချင်း append လုပ်နည်း
                with open(out_path, "wb") as final_file:
                    prog = st.progress(0)
                    for i, chunk in enumerate(chunks):
                        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
                        comm = edge_tts.Communicate(chunk, voice)
                        await comm.save(tmp)
                        with open(tmp, "rb") as f:
                            final_file.write(f.read())
                        prog.progress((i+1)/len(chunks))

                st.success("ပြီးပြီ!")
                st.audio(out_path)
                st.download_button("📥 MP3 Download", open(out_path,'rb'), "myanmar_unlimited.mp3", "audio/mp3", use_container_width=True)

            asyncio.run(gen_long())

with tab2:
    st.warning("Clone က 200 limit - voxcpm.app သုံး")
    st.components.v1.iframe("https://voxcpm.app", height=800)
