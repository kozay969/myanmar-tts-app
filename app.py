import streamlit as st
import asyncio
import edge_tts
import io
import re
import zipfile

st.set_page_config(page_title="Edge TTS Pro", page_icon="🎙️", layout="centered")

st.title("🎙️ မြန်မာအသံ (၁၂) မျိုး - Edge TTS")

# ---------- အသံ (၁၂) မျိုး စနစ် ----------
voice_options = {}
# အမျိုးသမီးအသံ ၆ မျိုး (Nilar)
for speed in [0.8, 0.9, 1.0, 1.1, 1.2, 1.3]:
    voice_options[f"Nilar (Female) - အမြန်နှုန်း {speed}x"] = ("my-MM-NilarNeural", f"{int((speed-1)*100)}%")
# အမျိုးသားအသံ ၆ မျိုး (Win Tun)
for speed in [0.8, 0.9, 1.0, 1.1, 1.2, 1.3]:
    voice_options[f"Win Tun (Male) - အမြန်နှုန်း {speed}x"] = ("my-MM-WinTunNeural", f"{int((speed-1)*100)}%")

selected_label = st.selectbox("အသံ (၁၂) မျိုးမှ ရွေးချယ်ပါ", list(voice_options.keys()))
voice_id, speed_rate = voice_options[selected_label]

max_chars = st.number_input("စာသားအပိုင်းအခြား (Characters)", min_value=500, max_value=5000, value=2000)
text_input = st.text_area("စာသားထည့်ပါ:", height=200, placeholder="ဒီနေရာမှာ စာသားရိုက်ထည့်ပါ...")

# ---------- Helper Functions ----------
def split_text(text: str, max_len: int) -> list[str]:
    text = text.strip()
    if not text: return []
    sentences = re.split(r"(?<=[.!?။])\s+", text)
    chunks, current = [], ""
    for sentence in sentences:
        if len(current) + len(sentence) + 1 <= max_len:
            current = f"{current} {sentence}".strip()
        else:
            if current: chunks.append(current)
            current = sentence
    if current: chunks.append(current)
    return chunks

async def generate_edge_tts(text: str, voice: str, rate: str) -> bytes:
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    audio_buffer = io.BytesIO()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_buffer.write(chunk["data"])
    return audio_buffer.getvalue()

# ---------- Main Action ----------
if st.button("🚀 GENERATE & ZIP", type="primary", use_container_width=True):
    if not text_input.strip():
        st.warning("စာသားထည့်ပေးပါ")
    else:
        chunks = split_text(text_input, max_chars)
        st.info(f"အပိုင်း {len(chunks)} ပိုင်းခွဲ၍ အသံထုတ်နေပါသည်...")
        
        audio_files = []
        progress_bar = st.progress(0)
        
        try:
            for i, chunk in enumerate(chunks):
                progress_bar.progress((i + 1) / len(chunks), text=f"အပိုင်း {i+1} ကို အသံထုတ်နေသည်...")
                audio_bytes = asyncio.run(generate_edge_tts(chunk, voice_id, speed_rate))
                audio_files.append((f"part_{i+1}.mp3", audio_bytes))
            
            st.success("အောင်မြင်စွာ ဖန်တီးပြီးပါပြီ!")
            
            # ZIP ပြုလုပ်ခြင်း
            zip_buf = io.BytesIO()
            with zipfile.ZipFile(zip_buf, "w") as zf:
                for fname, data in audio_files:
                    zf.writestr(fname, data)
            
            st.download_button("⬇️ Download ZIP", zip_buf.getvalue(), "tts_output.zip", "application/zip", use_container_width=True)
            st.audio(audio_files[0][1], format="audio/mp3")
            
        except Exception as e:
            st.error(f"Error ဖြစ်ပေါ်သည်: {e}")

