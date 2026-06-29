import streamlit as st
import asyncio
import edge_tts
import tempfile
import os

# App ရဲ့ ခေါင်းစဉ်နဲ့ ဖော်ပြချက်
st.set_page_config(page_title="Edge TTS စမ်းသပ်မှု", page_icon="🔊")
st.title("🔊 Edge TTS ဖြင့် စာသားမှ အသံပြောင်းခြင်း")
st.caption("Microsoft Edge ရဲ့ အခမဲ့ TTS ဝန်ဆောင်မှုကို အသုံးပြုထားသည်။")

# အသုံးပြုနိုင်မယ့် နမူနာအသံများ (အားလုံးကို `edge-tts --list-voices` နဲ့ ကြည့်နိုင်ပါတယ်)
voice_options = {
    "အမေရိကန် အင်္ဂလိပ် - Jenny (အမျိုးသမီး)": "en-US-JennyNeural",
    "အမေရိကန် အင်္ဂလိပ် - Guy (အမျိုးသား)": "en-US-GuyNeural",
    "ဗြိတိသျှ အင်္ဂလိပ် - Sonia (အမျိုးသမီး)": "en-GB-SoniaNeural",
    "စပိန် - Alvaro (အမျိုးသား)": "es-ES-AlvaroNeural",
    "ပြင်သစ် - Denise (အမျိုးသမီး)": "fr-FR-DeniseNeural",
}

# ဘေးဘားမှာ အသံရွေးချယ်မှုများ
with st.sidebar:
    st.header("အသံရွေးချယ်မှုများ")
    selected_voice_name = st.selectbox("အသံအမျိုးအစား", list(voice_options.keys()))
    selected_voice = voice_options[selected_voice_name]
    
    rate = st.slider("စကားပြောနှုန်း", -50, 100, 0, 5, help="-50% မှ +100% အထိ ချိန်ညှိနိုင်သည်။")
    rate_str = f"{rate:+d}%"  # +0%, -20%, +30% စသဖြင့်
    
    pitch = st.slider("အသံအနိမ့်အမြင့်", -12, 12, 0, 1, help="-12Hz မှ +12Hz အထိ ချိန်ညှိနိုင်သည်။")
    pitch_str = f"{pitch:+d}Hz"  # +0Hz, -5Hz, +8Hz စသဖြင့်

# စာသားထည့်ရန် နေရာ
text_input = st.text_area("အသံဖိုင်အဖြစ် ပြောင်းလိုသော စာသားကို ရိုက်ထည့်ပါ။", height=200)

# အသံပြောင်းရန် ခလုတ်
if st.button("အသံဖိုင် ထုတ်ယူမည်", type="primary"):
    if not text_input:
        st.warning("ကျေးဇူးပြု၍ စာသားတစ်ခုခု ရိုက်ထည့်ပါ။")
    else:
        with st.spinner("အသံဖိုင် ပြင်ဆင်နေသည်... ကျေးဇူးပြု၍ စောင့်ပါ။"):
            try:
                # ယာယီဖိုင် တစ်ခု ဖန်တီးပါ
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                    output_file = tmp_file.name
                
                # edge_tts ကို asynchronous ဖြင့် ခေါ်ပါ
                communicate = edge_tts.Communicate(text_input, selected_voice, rate=rate_str, pitch=pitch_str)
                await communicate.save(output_file)
                
                # ဖိုင်ကို ဖတ်ပြီး ပြသရန်
                with open(output_file, "rb") as f:
                    audio_bytes = f.read()
                
                # အသံဖိုင်ကို ဖွင့်ပြပါ
                st.audio(audio_bytes, format="audio/mp3")
                
                # Download ခလုတ် ထည့်ပါ
                st.download_button(
                    label="📥 အသံဖိုင် ဒေါင်းလုဒ်လုပ်မည် (MP3)",
                    data=audio_bytes,
                    file_name="output.mp3",
                    mime="audio/mp3",
                )
                
                # ယာယီဖိုင်ကို ဖျက်ပါ
                os.unlink(output_file)
                
                st.success("အသံဖိုင် အောင်မြင်စွာ ထုတ်ယူပြီးပါပြီ။")
                
            except Exception as e:
                st.error(f"အမှားတစ်ခု ဖြစ်ပွားခဲ့ပါသည်။ အသေးစိတ်: {e}")

