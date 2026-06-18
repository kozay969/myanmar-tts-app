import streamlit as st
import requests
import json

# --- PAGE CONFIG ---
st.set_page_config(page_title="Myanmar ElevenLabs AI TTS", page_icon="🎙️")
st.title("🎙️ Myanmar ElevenLabs AI TTS")
st.write("ElevenLabs အခမဲ့စနစ်ဖြင့် သဘာဝကျကျ မြန်မာအသံပြောင်းစနစ်")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("🔑 API & Settings")

# ElevenLabs API Key ထည့်ရန်နေရာ
api_key = st.sidebar.text_input("သင့် ElevenLabs API Key ကို ထည့်ပါ-", type="password")

# အခမဲ့အကောင့်တိုင်းတွင် Voice ID အမှားအယွင်း လုံးဝမရှိစေရန် တရားဝင် အခြေခံအကျဆုံး Rachel (ပုံသေ) ကို သုံးပါမည်
voice_id = "21m00Tcm4TlvDq8ikWAM"

st.sidebar.success("✅ အခမဲ့စနစ်သုံး သဘာဝအသံ (Rachel) ကို ချိတ်ဆက်ထားပါသည်။")
st.sidebar.caption("💡 အခမဲ့ဗားရှင်းဖြစ်သဖြင့် အသံ Tone ကို AI က စာသားအလိုက် သဘာဝကျအောင် အလိုအလျောက် ချိန်ညှိပေးပါမည်။")

# --- MAIN TEXT INPUT ---
text_input = st.text_area("မြန်မာစာသားများကို ဒီမှာရိုက်ထည့်ပါ (အများဆုံး စာလုံးရေ ၁၀,၀၀၀):", height=250, max_chars=10000)
st.write(f"စာလုံးရေ: {len(text_input)} / 10000")

# --- PROCESS BUTTON ---
if st.button("🔊 ElevenLabs AI အသံဖိုင်ထုတ်မည်"):
    if not api_key:
        st.error("⚠️ ကျေးဇူးပြု၍ Sidebar တွင် သင့် ElevenLabs API Key ကို အရင်ထည့်ပေးပါ။")
    elif not text_input.strip():
        st.warning("စာသားတစ်ခုခု ရိုက်ထည့်ပါ။")
    else:
        with st.spinner("AI က အသက်ရှူသံပါဝင်သော သဘာဝအသံ ဖန်တီးပေးနေပါတယ်..."):
            
            # API URL
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json; charset=utf-8",
                "xi-api-key": api_key
            }
            
            payload = {
                "text": text_input,
                "model_id": "eleven_multilingual_v2",  # မြန်မာစာလုံး ပံ့ပိုးပေးသော ဗားရှင်း
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75
                }
            }
            
            try:
                # Unicode Encoding Error မတက်စေရန် UTF-8 သို့ encode လုပ်ခြင်း
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
                # အကယ်၍ အပေါ်က Voice ID က အကောင့်သစ်တွေမှာ ရှာမတွေ့ပါက ဒုတိယအရန်စနစ် (Default text-to-speech) ဖြင့် ထပ်မံကြိုးစားခြင်း
                elif response.status_code == 404:
                    # အကောင့်တိုင်းမှာ မဖြစ်မနေပါတဲ့ 'rachel' ဆိုတဲ့ အမည်နဲ့ တိုက်ရိုက်ထပ်မံခေါ်ယူခြင်း
                    fallback_url = "https://api.elevenlabs.io/v1/text-to-speech/rachel"
                    fallback_response = requests.post(fallback_url, data=json_data, headers=headers)
                    
                    if fallback_response.status_code == 200:
                        output_file = "elevenlabs_output.mp3"
                        with open(output_file, "wb") as f:
                            f.write(fallback_response.content)
                        
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
                        st.error(f"Error တက်သွားပါသည်: {fallback_response.text}")
                else:
                    st.error(f"Error တက်သွားပါသည်: {response.text}")
                    
            except Exception as e:
                st.error(f"ကုဒ်ပိုင်းဆိုင်ရာ အမှားအယွင်းရှိပါသည်: {str(e)}")
                
