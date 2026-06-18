import streamlit as st
import requests
import json
import re
import time
from xml.sax.saxutils import escape as xml_escape
from gtts import gTTS

# --- PAGE CONFIG ---
st.set_page_config(page_title="Myanmar AI TTS", page_icon="🎙️")
st.title("🎙️ Myanmar AI TTS")
st.write("မြန်မာအသံပြောင်းစနစ် (gTTS + Azure Neural TTS + ElevenLabs)")

# --- AZURE CONFIG ---
AZURE_VOICES = {
    "Nilar (အမျိုးသမီးအသံ)": "my-MM-NilarNeural",
    "Thiha (အမျိုးသားအသံ)": "my-MM-ThihaNeural",
}
# Azure REST API has no hard documented char cap, but very long single
# requests can time out / fail. We split into safe chunks and stitch
# the resulting MP3s together.
AZURE_CHUNK_SIZE = 1500


def azure_get_token(subscription_key: str, region: str) -> str:
    """Fetch (and cache in session_state) an Azure Speech access token.
    Tokens are valid for 10 minutes; we refresh after 9 to be safe."""
    cache_key = f"{subscription_key}::{region}"
    now = time.time()
    cached = st.session_state.get("_azure_token_cache")
    if cached and cached["key"] == cache_key and (now - cached["time"]) < 540:
        return cached["token"]

    token_url = f"https://{region}.api.cognitive.microsoft.com/sts/v1.0/issueToken"
    resp = requests.post(
        token_url,
        headers={"Ocp-Apim-Subscription-Key": subscription_key},
        timeout=15,
    )
    if resp.status_code != 200:
        raise RuntimeError(
            f"Azure token ရယူခြင်း မအောင်မြင်ပါ (status {resp.status_code}). "
            f"API Key/Region မှန်/မမှန် စစ်ပါ။"
        )
    token = resp.text
    st.session_state["_azure_token_cache"] = {"key": cache_key, "time": now, "token": token}
    return token


def split_text_for_azure(text: str, max_len: int = AZURE_CHUNK_SIZE):
    """Split text into chunks at sentence boundaries (Myanmar ။ / ၊ / line breaks)
    so each chunk stays under max_len characters."""
    # Split keeping the delimiter attached to the preceding sentence.
    parts = re.split(r"(?<=[။၊\n])", text)
    chunks = []
    current = ""
    for part in parts:
        if len(current) + len(part) <= max_len:
            current += part
        else:
            if current.strip():
                chunks.append(current.strip())
            # If a single part itself is too long, hard-split it.
            if len(part) > max_len:
                for i in range(0, len(part), max_len):
                    chunks.append(part[i:i + max_len].strip())
                current = ""
            else:
                current = part
    if current.strip():
        chunks.append(current.strip())
    return [c for c in chunks if c]


def azure_synthesize_chunk(text_chunk: str, voice_name: str, subscription_key: str,
                            region: str, rate_pct: int, pitch_pct: int) -> bytes:
    token = azure_get_token(subscription_key, region)
    tts_url = f"https://{region}.tts.speech.microsoft.com/cognitiveservices/v1"

    safe_text = xml_escape(text_chunk)
    ssml = (
        "<speak version='1.0' xml:lang='my-MM'>"
        f"<voice xml:lang='my-MM' name='{voice_name}'>"
        f"<prosody rate='{rate_pct}%' pitch='{pitch_pct}%'>{safe_text}</prosody>"
        "</voice></speak>"
    )

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/ssml+xml",
        "X-Microsoft-OutputFormat": "audio-16khz-128kbitrate-mono-mp3",
        "User-Agent": "MyanmarAITTS",
    }
    resp = requests.post(tts_url, headers=headers, data=ssml.encode("utf-8"), timeout=30)
    if resp.status_code == 401:
        raise RuntimeError("Azure API Key မမှန်ကန်ပါ (Unauthorized)။")
    if resp.status_code == 400:
        raise RuntimeError("Azure request ပုံစံ မှားနေသည် (Region မှားနိုင်သည်)။")
    if resp.status_code == 429:
        raise RuntimeError("Azure rate limit ထိရောက်နေသည်။ ခဏစောင့်ပြီး ထပ်စမ်းပါ။")
    if resp.status_code != 200:
        raise RuntimeError(f"Azure TTS error (status {resp.status_code}): {resp.text[:300]}")
    return resp.content


def azure_synthesize(text: str, voice_name: str, subscription_key: str,
                      region: str, rate_pct: int, pitch_pct: int) -> bytes:
    chunks = split_text_for_azure(text)
    audio_bytes = b""
    progress = st.progress(0.0)
    for i, chunk in enumerate(chunks):
        audio_bytes += azure_synthesize_chunk(
            chunk, voice_name, subscription_key, region, rate_pct, pitch_pct
        )
        progress.progress((i + 1) / len(chunks))
    progress.empty()
    return audio_bytes


# --- SIDEBAR CONTROLS ---
st.sidebar.header("⚙️ Settings")

engine = st.sidebar.radio(
    "TTS Engine ရွေးပါ-",
    [
        "🇲🇲 gTTS (Myanmar - အခမဲ့)",
        "🇲🇲 Azure Neural TTS (Myanmar - အရည်အသွေးမြင့်)",
        "🌍 ElevenLabs (အခြားဘာသာ)",
    ],
)

# --- gTTS settings ---
slow_mode = False
if "gTTS" in engine:
    slow_mode = st.sidebar.checkbox("🐢 နှေးနှေးဖတ်မည်", value=False)

# --- Azure settings ---
azure_key = None
azure_region = None
azure_voice_id = None
azure_rate = 0
azure_pitch = 0
if "Azure" in engine:
    azure_key = st.sidebar.text_input("Azure Speech API Key:", type="password")
    azure_region = st.sidebar.text_input(
        "Azure Region (ဥပမာ- southeastasia, eastus):", value="southeastasia"
    )
    voice_label = st.sidebar.selectbox("🎤 အသံရွေးချယ်ပါ-", list(AZURE_VOICES.keys()))
    azure_voice_id = AZURE_VOICES[voice_label]
    with st.sidebar.expander("🎛️ အသံ Fine-tune (Optional)"):
        azure_rate = st.slider("မြန်နှုန်း (Speed %)", -50, 50, 0, step=5)
        azure_pitch = st.slider("အသံအနိမ့်အမြင့် (Pitch %)", -50, 50, 0, step=5)
    st.sidebar.caption(
        "Azure Speech key ကို Azure Portal → Speech service resource → "
        "'Keys and Endpoint' တွင် ရယူပါ။ Free tier (F0) ဖြင့်လည်း စတင်စမ်းသပ်နိုင်ပါသည်။"
    )

# --- ElevenLabs Settings ---
api_key = None
voice_id = None
if "ElevenLabs" in engine:
    api_key = st.sidebar.text_input("ElevenLabs API Key-", type="password")
    voice_options = {}

    if api_key:
        try:
            voice_resp = requests.get(
                "https://api.elevenlabs.io/v1/voices",
                headers={"xi-api-key": api_key},
                timeout=15,
            )
            if voice_resp.status_code == 200:
                voices = voice_resp.json().get("voices", [])
                voice_options = {v["name"]: v["voice_id"] for v in voices}
                st.sidebar.success(f"✅ အသံ {len(voice_options)} ခု တွေ့ပါသည်။")
            else:
                st.sidebar.error("API Key မှားနေသည်။")
        except Exception as e:
            st.sidebar.error(f"Error: {e}")

    if voice_options:
        selected_voice_name = st.sidebar.selectbox("🎤 အသံရွေးချယ်ပါ-", list(voice_options.keys()))
        voice_id = voice_options[selected_voice_name]

    st.sidebar.caption(
        "⚠️ ElevenLabs ၏ official ဘာသာစာရင်းတွင် မြန်မာစာ မပါသေးပါ — "
        "အခြားဘာသာစကားများအတွက်သာ အကြံပြုပါသည်။"
    )

# --- MAIN TEXT INPUT ---
text_input = st.text_area(
    "စာသားများကို ဒီမှာရိုက်ထည့်ပါ (အများဆုံး စာလုံးရေ ၁၀,၀၀၀):",
    height=250,
    max_chars=10000,
)
st.write(f"စာလုံးရေ: {len(text_input)} / 10000")

# --- PROCESS BUTTON ---
if st.button("🔊 အသံဖိုင်ထုတ်မည်"):
    if not text_input.strip():
        st.warning("စာသားတစ်ခုခု ရိုက်ထည့်ပါ။")

    # --- gTTS ---
    elif "gTTS" in engine:
        with st.spinner("မြန်မာအသံ ဖန်တီးပေးနေပါတယ်..."):
            try:
                tts = gTTS(text=text_input, lang="my", slow=slow_mode)
                output_file = "gtts_output.mp3"
                tts.save(output_file)

                st.success("🎉 မြန်မာအသံဖိုင် ရပါပြီ။")
                st.audio(output_file, format="audio/mp3")

                with open(output_file, "rb") as f:
                    st.download_button(
                        label="📥 အသံဖိုင်ရယူရန် (Download MP3)",
                        data=f,
                        file_name="myanmar_tts.mp3",
                        mime="audio/mp3",
                    )
            except Exception as e:
                st.error(f"Error: {str(e)}")

    # --- Azure Neural TTS ---
    elif "Azure" in engine:
        if not azure_key:
            st.error("⚠️ Azure Speech API Key ထည့်ပေးပါ။")
        elif not azure_region.strip():
            st.error("⚠️ Azure Region ထည့်ပေးပါ။")
        else:
            with st.spinner("Azure Neural အသံ ဖန်တီးပေးနေပါတယ်... (စာသားရှည်ရင် အချိန်ပိုကြာနိုင်ပါသည်)"):
                try:
                    audio_bytes = azure_synthesize(
                        text_input, azure_voice_id, azure_key.strip(),
                        azure_region.strip(), azure_rate, azure_pitch,
                    )
                    output_file = "azure_output.mp3"
                    with open(output_file, "wb") as f:
                        f.write(audio_bytes)

                    st.success("🎉 Azure Neural အသံဖိုင် ရပါပြီ။")
                    st.audio(output_file, format="audio/mp3")

                    with open(output_file, "rb") as f:
                        st.download_button(
                            label="📥 အသံဖိုင်ရယူရန် (Download MP3)",
                            data=f,
                            file_name="myanmar_azure_tts.mp3",
                            mime="audio/mp3",
                        )
                except Exception as e:
                    st.error(f"Error: {str(e)}")

    # --- ElevenLabs ---
    elif "ElevenLabs" in engine:
        if not api_key:
            st.error("⚠️ ElevenLabs API Key ထည့်ပေးပါ။")
        elif not voice_id:
            st.error("⚠️ အသံတစ်ခု ရွေးချယ်ပေးပါ။")
        else:
            with st.spinner("ElevenLabs အသံ ဖန်တီးပေးနေပါတယ်..."):
                try:
                    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
                    headers = {
                        "Accept": "audio/mpeg",
                        "Content-Type": "application/json; charset=utf-8",
                        "xi-api-key": api_key,
                    }
                    payload = {
                        "text": text_input,
                        "model_id": "eleven_multilingual_v2",
                        "voice_settings": {
                            "stability": 0.5,
                            "similarity_boost": 0.75,
                        },
                    }

                    json_data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
                    response = requests.post(url, data=json_data, headers=headers, timeout=60)

                    if response.status_code == 200:
                        output_file = "elevenlabs_output.mp3"
                        with open(output_file, "wb") as f:
                            f.write(response.content)

                        st.success("🎉 ElevenLabs အသံဖိုင် ရပါပြီ။")
                        st.audio(output_file, format="audio/mp3")

                        with open(output_file, "rb") as f:
                            st.download_button(
                                label="📥 အသံဖိုင်ရယူရန် (Download MP3)",
                                data=f,
                                file_name="elevenlabs_output.mp3",
                                mime="audio/mp3",
                            )
                    else:
                        st.error(f"Error: {response.text}")

                except Exception as e:
                    st.error(f"Error: {str(e)}")
