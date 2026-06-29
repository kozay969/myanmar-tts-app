import streamlit as st
import io
import re
import time
import asyncio
import zipfile
import edge_tts

st.set_page_config(page_title="Myanmar Edge TTS", page_icon="🔊")

st.title("🔊 Myanmar Edge TTS Pro")
st.caption("Voice Preview • Phonetic Fallback • GitHub Ready")

# ---------------- VOICES ----------------
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

EN_FALLBACK = "en-US-AriaNeural"

voice = st.selectbox("🎙️ Voice", MY_VOICES)

text_input = st.text_area("📝 Text ထည့်ပါ", height=200)

max_chars = st.slider("Chunk size", 300, 4000, 1200)

# ---------------- SAMPLE ----------------
SAMPLE_TEXT = "မင်္ဂလာပါ။ ဒီဟာက voice preview စမ်းသပ်ခြင်းဖြစ်ပါတယ်။"

# ---------------- PHONETIC ENGINE ----------------
def myanmar_to_phonetic(text: str) -> str:
    rules = {
        "က": "ka","ခ": "kha","ဂ": "ga","င": "nga",
        "စ": "sa","ဆ": "hsa","ဇ": "za",
        "တ": "ta","ထ": "hta","ဒ": "da","န": "na",
        "ပ": "pa","ဖ": "pha","ဗ": "ba","မ": "ma",
        "ယ": "ya","ရ": "ra","လ": "la","ဝ": "wa",
        "သ": "tha","ဟ": "ha","အ": "a",
        "ါ": "a","ာ": "a","ိ": "i","ီ": "i","ု": "u","ူ": "u",
        "ေ": "e","ဲ": "ae","့":"","း":"",
    }

    for k, v in rules.items():
        text = text.replace(k, v)

    return text


# ---------------- SPLIT ----------------
def split_text(text, max_len):
    text = text.strip()
    sentences = re.split(r"(?<=[.!?။])\s+", text)
    chunks, cur = [], ""

    for s in sentences:
        if len(cur) + len(s) <= max_len:
            cur += " " + s
        else:
            if cur:
                chunks.append(cur.strip())
            cur = s

    if cur:
        chunks.append(cur.strip())

    return chunks


# ---------------- EDGE TTS ----------------
async def tts(text, voice):
    audio = io.BytesIO()

    try:
        comm = edge_tts.Communicate(text=text, voice=voice)
    except:
        text = myanmar_to_phonetic(text)
        comm = edge_tts.Communicate(text=text, voice=EN_FALLBACK)

    async for msg in comm.stream():
        if msg["type"] == "audio":
            audio.write(msg["data"])

    return audio.getvalue()


def run_tts(text, voice):
    return asyncio.run(tts(text, voice))


# ---------------- VOICE PREVIEW ----------------
st.subheader("🎧 Voice Preview")

col1, col2 = st.columns(2)

with col1:
    if st.button("🔊 Preview Voice"):
        audio = run_tts(SAMPLE_TEXT, voice)
        st.audio(audio, format="audio/mp3")

with col2:
    st.info("Voice မရွေးခင် စမ်းနားထောင်ပါ")


# ---------------- MAIN ----------------
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
            st.error(f"Error {i+1}: {e}")

        progress.progress((i+1)/len(chunks))
        time.sleep(0.2)

    # ---------------- OUTPUT ----------------
    st.subheader("🎧 Output")

    for name, audio in results:
        st.audio(audio, format="audio/mp3")
        st.download_button("⬇️ " + name, audio, name, "audio/mp3")

    # ---------------- ZIP ----------------
    zip_buf = io.BytesIO()

    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as z:
        for name, audio in results:
            z.writestr(name, audio)

    st.download_button(
        "⬇️ Download All ZIP",
        zip_buf.getvalue(),
        "myanmar_tts.zip",
        "application/zip"
    )
