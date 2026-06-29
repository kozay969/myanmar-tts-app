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
# Speed 0.8x to 1.3x 
# Note: edge-tts uses strings like "+30%" or "-20%"
speeds = [0.8, 0.9, 1.0, 1.1, 1.2, 1.3]
for speed in speeds:
    # Calculate percentage difference from 1.0 (e.g., 1.3 is +30%)
    rate_val = int((speed - 1) * 100)
    rate_str = f"{rate_val:+d}%" # formats as +30%, -20%, etc.
    
    voice_options[f"Nilar (Female) - Speed {speed}x"] = ("my-MM-NilarNeural", rate_str)
    voice_options[f"Win Tun (Male) - Speed {speed}x"] = ("my-MM-WinTunNeural", rate_str)

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
                # Run the async function
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

