import streamlit as st
import requests
import json

# --- PAGE CONFIG ---
st.set_page_config(page_title="Myanmar ElevenLabs AI TTS", page_icon="🎙️")
st.title("🎙️ Myanmar ElevenLabs AI TTS")
st.write("ElevenLabs အခမဲ့စနစ်ဖြင့် သဘာဝကျကျ မြန်မာအသံပြောင်းစနစ်")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("🔑 API & Settings")
api_key = st.sidebar.text_input("သင့် ElevenLabs API Key ကို ထည့်ပါ-", type="password")

# --- LOAD VOICES ---
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
            st.sidebar.error("API Key မှားနေသည် သို့မဟုတ် voice ရယူမရပါ။")
    except Exception as e:
        st.sidebar.error(f"Voice ရယူရာတွင် အမှားရှိသည်: {e}")

if voice_options:
    selected_voice_name = st.sidebar.selectbox("🎤 အသံရွေးချယ်ပါ-", list(voice_options.keys()))
    voice_id = voice_options[selected_voice_name]
    st.sidebar.caption(f"Voice ID: `{voice_id}`")
else:
    voice_id = None
    if api_key:
        st.sidebar.warning("Voice list ရယူ၍ မရသေးပါ။")

# --- MAIN TEXT INPUT ---
text_input = st.text_area(
    "မြန်မာစာသားများကို ဒီမှာရိုက်ထည့်ပါ (အများဆုံး စာလုံးရေ ၁၀,၀၀၀):",
    height=250,
    max_chars=10000
)
st.write(f"စာလုံးရေ: {len(text_input)} / 10000")

# --- PROCESS BUTTON ---
if st.button("🔊 ElevenLabs AI အသံဖိုင်ထုတ်မည်"):
    if not api_key:
        st.error("⚠️ Sidebar တွင် သင့် ElevenLabs API Key ကို အရင်ထည့်ပေးပါ။")
    elif not voice_id:
        st.error("⚠️ အသံတစ်ခု ရွေးချယ်ပေးပါ။")
    elif not text_input.strip():
        st.warning("စာသားတစ်ခုခု ရိုက်ထည့်ပါ။")
    else:
        with st.spinner("AI က သဘာဝအသံ ဖန်တီးပေးနေပါတယ်..."):
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

            try:
                json_data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
                response = requests.post(url, data=json_data, headers=headers)

                if response.status_code == 200:
                    output_file = "elevenlabs_output.mp3"
                    with open(output_file, "wb") as f:
                        f.write(response.content)

                    st.success("🎉 ElevenLabs အဆင့်မြင့်အသံဖိုင် ရပါပြီ။")
                    st.audio(output_file, format="audio/mp3")

                    with open(output_file, "rb") as f:
                        st.download_button(
                            label="📥 အသံဖိုင်ကိုရယူရန် (Download MP3)",
                            data=f,
                            file_name="elevenlabs_myanmar.mp3",
                            mime="audio/mp3"
                        )
                else:
                    st.error(f"Error တက်သွားပါသည်: {response.text}")

            except Exception as e:
                st.error(f"ကုဒ်ပိုင်းဆိုင်ရာ အမှားအယွင်းရှိပါသည်: {str(e)}")
