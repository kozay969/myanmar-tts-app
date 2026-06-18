import streamlit as st
import requests

# --- PAGE CONFIG ---
st.set_page_config(page_title="Myanmar ElevenLabs AI TTS", page_icon="🎙️")
st.title("🎙️ Myanmar ElevenLabs AI TTS")
st.write("ElevenLabs သဘာဝအကျဆုံး AI စနစ်သုံး မြန်မာအသံပြောင်းစနစ်")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("🔑 API & Settings")

# ElevenLabs API Key ထည့်ရန်နေရာ
api_key = st.sidebar.text_input("သင့် ElevenLabs API Key ကို ထည့်ပါ-", type="password")

# ၁။ မြန်မာအသံ ရွေးချယ်မှု (ElevenLabs ရဲ့ နာမည်ကြီး Multi-lingual voice များ)
# ElevenLabs တွင် ဤ Voice ID များသည် မြန်မာလို အကောင်းဆုံး ထွက်ပါသည်။
voice_option = st.sidebar.selectbox(
    "အသံရွေးချယ်ပါ (Voices)",
    [
        "အမျိုးသမီးသံ (Rachel - သဘာဝကျကျ ပုံပြောသံ)",
        "အမျိုးသမီးသံ (Nicole - သက်သာငြိမ့်ညောင်းသံ)",
        "အမျိုးသားသံ (Adam - သြဇာရှိ Movie Recap သံ)",
        "အမျိုးသားသံ (Antoni - ပြတ်သားသွက်လက်သံ)"
    ]
)

# Voice ID များ သတ်မှတ်ခြင်း
if "Rachel" in voice_option:
    voice_id = "21m00Tcm4TlvDq8ikWAM"
elif "Nicole" in voice_option:
    voice_id = "piTKgcLEGmPEeTBDesST"
elif "Adam" in voice_option:
    voice_id = "pNInz6obpgmo51dJe5mI"
else:
    voice_id = "ERXwobaYiN019vkySvjV"

st.sidebar.caption("💡 ElevenLabs တွင် အနှေးအမြန်နှင့် Tone များကို အသံရွေးချယ်မှုအပေါ် မူတည်၍ AI က အလိုအလျောက် သဘာဝကျအောင် ချိန်ညှိပေးပါသည်။")

# --- MAIN TEXT INPUT ---
text_input = st.text_area("မြန်မာစာသားများကို ဒီမှာရိုက်ထည့်ပါ (အများဆုံး စာလုံးရေ ၁၀,۰۰၀):", height=250, max_chars=10000)
st.write(f"စာလုံးရေ: {len(text_input)} / 10000")

# --- PROCESS BUTTON ---
if st.button("🔊 ElevenLabs AI အသံဖိုင်ထုတ်မည်"):
    if not api_key:
        st.error("⚠️ ကျေးဇူးပြု၍ Sidebar တွင် သင့် ElevenLabs API Key ကို အရင်ထည့်ပေးပါ။")
    elif not text_input.strip():
        st.warning("စာသားတစ်ခုခု ရိုက်ထည့်ပါ။")
    else:
        with st.spinner("AI က အသက်ရှူသံပါဝင်သော သဘာဝအသံ ဖန်တီးပေးနေပါတယ်..."):
            
            # ElevenLabs TTS API URL (Multilingual v2 သုံးထားသဖြင့် မြန်မာစာ 100% ရပါသည်)
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
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
            
            response = requests.post(url, json=payload, headers=headers)
            
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
                        file_name=f"elevenlabs_myanmar.mp3",
                        mime="audio/mp3"
                    )
            else:
                st.error(f"Error တက်သွားပါသည်: {response.text}")
                
