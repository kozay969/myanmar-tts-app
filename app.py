import streamlit as st
import io
import re
import time
import asyncio
import zipfile
import edge_tts

st.set_page_config(page_title="Myanmar Edge TTS", page_icon="🔊")

st.title("🔊 Myanmar Edge TTS (12 Voices)")
st.caption("GitHub + Streamlit Cloud Ready • Free TTS")

# ---------- MYANMAR VOICES ----------
MY_VOICES = [
    "my-MM-NilarNeural",
    "my-MM-ThazinNeural",
    "my-MM-AyeAyeNeural",
    "my-MM-KhinNeural",
    "my-MM-HninNeural",
    "my-MM-YadanarNeural",
    "my-MM-SandaNeural",
    "my-MM-MyaNeural",
    "my-MM-HlaNeural",
    "my-MM-SuSuNeural",
    "my-MM-KhayNeural",
    "my-MM-WutyiNeural",
]

voice = st.selectbox("🎙️ Myanmar Voice", MY_VOICES)

text_input = st.text_area("📝 Text ထည့်ပါ", height=250)

max_chars = st.slider("Chunk size", 300, 4000, 1200)

# ---------- SPLIT ----------
def split_text(text, max_len):
    text = text.strip()
    sentences = re.split(r"(?<=[.!?။])\s+", text)
    chunks, cur = [], ""

    for s in sentences:
        if len(cur) + len(s) <= max_len:
            cur += " " + s
        else:
            chunks.append(cur.strip())
            cur = s

    if cur:
        chunks.append(cur.strip())

    return chunks


# ---------- EDGE TTS ----------
async def tts(text, voice):
    communicate = edge_tts.Communicate(text=text, voice=voice)
    audio = io.BytesIO()

    async for msg in communicate.stream():
        if msg["type"] == "audio":
            audio.write(msg["data"])

    return audio.getvalue()


def run_tts(text, voice):
    return asyncio.run(tts(text, voice))


# ---------- MAIN ----------
if st.button("🚀 Generate Speech"):

    if not text_input.strip():
        st.error("Text ထည့်ပါ")
        st.stop()

    chunks = split_text(text_input, max_chars)
    st.info(f"Chunks: {len(chunks)}")

    results = []
    progress = st.progress(0)

    for i, c in enumerate(chunks):
        try:
            audio = run_tts(c, voice)
            results.append((f"part_{i+1}.mp3", audio))
        except Exception as e:
            st.error(f"Error chunk {i+1}: {e}")

        progress.progress((i+1)/len(chunks))
        time.sleep(0.3)

    # ---------- OUTPUT ----------
    for name, audio in results:
        st.audio(audio, format="audio/mp3")
        st.download_button("⬇️ Download " + name, audio, name, "audio/mp3")

    # ZIP
    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w") as z:
        for name, audio in results:
            z.writestr(name, audio)

    st.download_button(
        "⬇️ Download All ZIP",
        zip_buf.getvalue(),
        "myanmar_tts.zip",
        "application/zip"
    )
