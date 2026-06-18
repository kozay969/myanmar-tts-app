import streamlit as st
import requests

# --- PAGE CONFIG ---
st.set_page_config(page_title="Myanmar ElevenLabs AI TTS", page_icon="🎙️")
st.title("🎙️ Myanmar ElevenLabs AI TTS")
st.write("ElevenLabs အခမဲ့စနစ်ဖြင့် သဘာဝကျကျ မြန်မာအသံပြောင်းစနစ်")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("🔑 API & Settings")

# ElevenLabs API Key ထည့်ရန်နေရာ
api_key = st.sidebar.text_input("သင့် ElevenLabs API Key ကို ထည့်ပါ-", type="password")

# Free အကောင့်များတွင် API သုံးခွင့်ရသော တရားဝင် Default Voice ID များ
voice_option = st.sidebar.selectbox(
    "အသံရွေးချယ်ပါ (Voices)",
    [
        "အမျိုးသမီးသံ (Rachel - သဘာဝကျကျ စကားပြောသံ)",
        "အမျိုးသမီးသံ (Clyde - အေးဆေးငြိမ့်ညောင်းသံ)",
        "အမျိုးသားသံ (Drew - ပြတ်သားသွက်လက်သံ)",
        "အမျိုးသားသံ (Paul - သြဇာရှိ အစီရင်ခံသံ)"
    ]
)

# Free အကောင့်တိုင်း 100% သုံးရမည့် တရားဝင် Voice IDs
if "Rachel" in voice_option:
    voice_id = "21m00Tcm4TlvDq8ikWAM"
elif "Clyde" in voice_option:
    voice_id = "2EiwWnXF2V4Rhe6bEA60"
elif "Drew" in voice_option:
    voice_id = "29vD33N1CtxCmqQRPOHJ"
else:
    voice_id = "5Q0t7uCAlwvnST9v87ee"

st.sidebar.caption("💡 အခမဲ့ဗားရှင်းဖြစ်သဖြင့် အသံ Tone များကို AI က စာသားအလိုက် သဘာဝကျအောင် အလိုအလျောက် ချိန်ညှိပေးပါမည်။")

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
            
            # Unicode Error မတက်စေရန် header တွင် utf-8 သတ်မှတ်ခြင်း
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json; charset=utf-8",
                "xi-api-key": api_key
            }
            
            # စာသားကို JSON အဖြစ် မပို့မီ UTF-8 သို့ သေချာပြောင်းလဲခြင်း
            payload = {
                "text": text_input,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.45,
                    "similarity_boost": 0.8
                }
            }
            
            try:
                # json=payload သုံးမည့်အစား သေချာအောင် json.dumps() ဖြင့် string ပြောင်းပြီးမှ ပို့သည်
                import json
                json_data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
                
                response = requests.post(url, data=json_data, headers=headers)
                
                if response.status_code == 200:
                    output_file = "elevenlabs_free_output.mp3"
                    with open(output_file, "wb") as f:
                        f.write(response.content)
                    
                    st.success("🎉 ElevenLabs သဘာဝအသံဖိုင် ရပါပြီ။")
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
                    
