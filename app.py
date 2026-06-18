import streamlit as st
import requests
import json
from gtts import gTTS
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="Myanmar AI TTS", page_icon="🎙️")
st.title("🎙️ Myanmar AI TTS")
st.write("မြန်မာအသံပြောင်းစနစ် (ElevenLabs + gTTS)")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("⚙️ Settings")

# TTS Engine ရွေးချယ်ရန်
engine = st.sidebar.radio(
    "TTS Engine ရွေးပါ-",
    ["🇲🇲 gTTS (မြန်မာ - အခမဲ့)", "🌍 ElevenLabs (အခြားဘာသာ)"]
)

# --- ElevenLabs Settings ---
if "ElevenLabs" in engine:
    api_key = st.sidebar.text_input("ElevenLabs API Key-", type="password")
    voice_options = {}

    if api_key:
        try:
            voice_resp = requests.get(
                "https://api.elevenlabs.io/v1/voices",
                headers={"xi-api-key": api_key}
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
    else:
        voice_id = None
else:
    api_key = None
    voice_id = None
    # gTTS speed option
    slow_mode = st.sidebar.checkbox("🐢 နှေးနှေးဖတ်မည်", value=False)

# --- MAIN TEXT INPUT ---
text_input = st.text_area(
    "စာသားများကို ဒီမှာရိုက်ထည့်ပါ (အများဆုံး စာလုံးရေ ၁၀,၀၀၀):",
    height=250,
    max_chars=10000
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
                tts = gTTS(text=text_input, lang='my', slow=slow_mode)
                output_file = "gtts_output.mp3"
                tts.save(output_file)

                st.success("🎉 မြန်မာအသံဖိုင် ရပါပြီ။")
                st.audio(output_file, format="audio/mp3")

                with open(output_file, "rb") as f:
                    st.download_button(
                        label="📥 အသံဖိုင်ရယူရန် (Download MP3)",
                        data=f,
                        file_name="myanmar_tts.mp3",
                        mime="audio/mp3"
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
                        "xi-api-key": api_key
                    }
                    payload = {
                        "text": text_input,
                        "model_id": "eleven_multilingual_v2",
                        "voice_settings": {
                            "stability": 0.5,
                            "similarity_boost": 0.75
                        }
                    }

                    json_data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
                    response = requests.post(url, data=json_data, headers=headers)

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
                                mime="audio/mp3"
                            )
                    else:
                        st.error(f"Error: {response.text}")

                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    
