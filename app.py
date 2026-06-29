import streamlit as st
import os
import io
import re
import time
import wave
import zipfile
from google import genai
from google.genai import types

st.set_page_config(page_title="Gemini TTS Generator", page_icon="🔊", layout="centered")

st.title("🔊 Gemini TTS Generator")
st.caption("Gemini 2.5 Flash Preview TTS — Auto Split • WAV • ZIP Download")

# ---------- API KEY ----------
api_key = st.text_input(
    "Google AI Studio API Key",
    type="password",
    value=os.environ.get("GEMINI_API_KEY", ""),
    help="Get a key from https://aistudio.google.com/apikey",
)

VOICES = [
    "Zephyr", "Puck", "Charon", "Kore", "Fenrir", "Leda",
    "Orus", "Aoede", "Callirrhoe", "Autonoe", "Enceladus", "Iapetus",
]
voice = st.selectbox("Voice", VOICES, index=0)

max_chars = st.number_input(
    "Auto-split chunk size (characters)",
    min_value=200, max_value=4000, value=1000, step=100,
    help="Long text is automatically split into chunks of roughly this size, splitting at sentence boundaries.",
)

delay_seconds = st.number_input(
    "Chunk တစ်ခုနဲ့တစ်ခုကြား Delay (seconds)",
    min_value=0, max_value=60, value=21, step=1,
    help="Free tier limit က 1 မိနစ်ထဲ request 3 ခုပါ။ 429 error မရှောင်လို့ ဒီ delay ကို မြှင့်ပါ (default 21s = မိနစ်ထဲ ~3 requests)။",
)

text_input = st.text_area("Text to convert to speech", height=250, placeholder="Paste or type your text here...")

# ---------- HELPERS ----------
def split_text(text: str, max_len: int) -> list[str]:
    """Split text into chunks <= max_len, breaking on sentence boundaries."""
    text = text.strip()
    if not text:
        return []
    sentences = re.split(r"(?<=[.!?။])\s+", text)
    chunks, current = [], ""
    for sentence in sentences:
        if not sentence:
            continue
        if len(current) + len(sentence) + 1 <= max_len:
            current = f"{current} {sentence}".strip()
        else:
            if current:
                chunks.append(current)
            # If a single sentence itself exceeds max_len, hard-split it
            if len(sentence) > max_len:
                for i in range(0, len(sentence), max_len):
                    chunks.append(sentence[i:i + max_len])
                current = ""
            else:
                current = sentence
    if current:
        chunks.append(current)
    return chunks


def pcm_to_wav_bytes(pcm_data: bytes, channels=1, rate=24000, sample_width=2) -> bytes:
    """Wrap raw PCM data returned by Gemini TTS into a valid WAV file."""
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm_data)
    return buf.getvalue()


def generate_tts(client: genai.Client, text: str, voice_name: str, max_retries: int = 3) -> bytes:
    """Call Gemini TTS for a single chunk and return WAV bytes. Retries on 429 with backoff."""
    last_error = None
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash-preview-tts",
                contents=text,
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice_name)
                        )
                    ),
                ),
            )
            pcm_data = response.candidates[0].content.parts[0].inline_data.data
            return pcm_to_wav_bytes(pcm_data)
        except Exception as e:
            last_error = e
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                wait = 40 * (attempt + 1)
                time.sleep(wait)
                continue
            raise
    raise last_error


# ---------- MAIN ACTION ----------
if st.button("Generate Speech", type="primary", use_container_width=True):
    if not api_key:
        st.error("API key ထည့်ပါ — Google AI Studio key လိုအပ်ပါတယ်။")
    elif not text_input.strip():
        st.error("Text တစ်ခု ထည့်ပါ။")
    else:
        chunks = split_text(text_input, max_chars)
        st.info(f"Text ကို {len(chunks)} chunk(s) အဖြစ် split လုပ်ပါမယ်။")

        try:
            client = genai.Client(api_key=api_key)
        except Exception as e:
            st.error(f"Client ဖန်တီးရာတွင် အမှားရှိပါသည်: {e}")
            st.stop()

        progress_bar = st.progress(0, text="Starting...")
        wav_files = []
        errors = []

        for idx, chunk in enumerate(chunks):
            try:
                progress_bar.progress(
                    idx / len(chunks),
                    text=f"Generating chunk {idx + 1} / {len(chunks)}...",
                )
                wav_bytes = generate_tts(client, chunk, voice)
                wav_files.append((f"part_{idx + 1:03d}.wav", wav_bytes))
            except Exception as e:
                errors.append(f"Chunk {idx + 1}: {e}")

            # Respect free-tier rate limit between requests (skip after the last chunk)
            if idx < len(chunks) - 1 and delay_seconds > 0:
                progress_bar.progress(
                    (idx + 1) / len(chunks),
                    text=f"Waiting {delay_seconds}s before next chunk (rate limit)...",
                )
                time.sleep(delay_seconds)

        progress_bar.progress(1.0, text="Done!")

        if errors:
            st.warning("အချို့ chunk တွေတွင် error ဖြစ်ပါသည်:")
            for err in errors:
                st.text(err)

        if wav_files:
            st.success(f"{len(wav_files)} / {len(chunks)} chunk(s) အောင်မြင်စွာ generate ပြီးပါပြီ။")

            # Individual downloads
            st.subheader("Individual WAV files")
            for fname, data in wav_files:
                st.audio(data, format="audio/wav")
                st.download_button(
                    label=f"⬇️ Download {fname}",
                    data=data,
                    file_name=fname,
                    mime="audio/wav",
                    key=f"dl_{fname}",
                )

            # ZIP of everything
            zip_buf = io.BytesIO()
            with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
                for fname, data in wav_files:
                    zf.writestr(fname, data)
            zip_buf.seek(0)

            st.subheader("All files together")
            st.download_button(
                label="⬇️ Download All as ZIP",
                data=zip_buf,
                file_name="tts_output.zip",
                mime="application/zip",
                use_container_width=True,
            )
        else:
            st.error("WAV file တစ်ခုမှ generate မဖြစ်ပါ — error log ကို ကြည့်ပါ။")

st.divider()
st.caption("Powered by Gemini 2.5 Flash Preview TTS · Built with Streamlit")
