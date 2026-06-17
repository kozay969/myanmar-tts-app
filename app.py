import streamlit as st
import asyncio
import edge_tts
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="Myanmar AI Text-to-Speech", page_icon="🎙️")
st.title("🎙️ Myanmar AI Text-to-Speech")
st.write("Storytelling နှင့် Movie Recap များအတွက် မြန်မာအသံပြောင်းစနစ်")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("🎛️ Settings")

# မြန်မာအသံ ရွေးချယ်မှု (edge-tts တွင် ပါဝင်သော voice များ)
voice_option = st.sidebar.selectbox(
    "အသံရွေးချယ်ပါ",
    ["မြန်မာ အမျိုးသမီး (Nilar)", "မြန်မာ အမျိုးသား (Thiha)"]
)

voice_id = "my-MM-NilarNeural" if "Nilar" in voice_option else "my-MM-ThihaNeural"

# အသံ Tone ပုံစံများ (Speed နှင့် Pitch ကို ကစားထားခြင်း)
tone_option = st.sidebar.selectbox(
    "အသံ Tone ရွေးချယ်ပါ",
    ["Normal (ပုံမှန်)", "Movie Recap (မြန်မြန်နှင့် စိတ်ဝင်စားစရာ)", "Scary/Thriller (အသံတုန်/ခြောက်ခြားဖွယ်)", "Documentary (အေးဆေးပြတ်သား)"]
)

# Speed & Pitch settings base on Tone
if tone_option == "Movie Recap (မြန်မြန်နှင့် စိတ်ဝင်စားစရာ)":
    speed, pitch = "+15%", "+0Hz"
elif tone_option == "Scary/Thriller (အသံတုန်/ခြောက်ခြားဖွယ်)":
    speed, pitch = "-10%", "-5Hz"
elif tone_option == "Documentary (အေးဆေးပြတ်သား)":
    speed, pitch = "+0%", "-2Hz"
else:
    speed, pitch = "+0%", "+0Hz"

# --- MAIN INPUT ---
text_input = st.text_area("မြန်မာစာသားများကို ဒီမှာရိုက်ထည့်ပါ (အများဆုံး စာလုံးရေ ၁၀,၀၀၀):", height=250, max_chars=10000)
st.write(f"စာလုံးရေ: {len(text_input)} / 10000")

# --- TTS FUNCTION ---
async def generate_tts(text, voice, speed, pitch, output_path):
    communicate = edge_tts.Communicate(text, voice, rate=speed, pitch=pitch)
    await communicate.save(output_path)

# --- PROCESS ---
if st.button("🔊 အသံဖိုင်ထုတ်မည်"):
    if not text_input.strip():
        st.warning("စာသားတစ်ခုခု ရိုက်ထည့်ပါ။")
    else:
        with st.spinner("AI က အသံဖိုင် လုပ်ပေးနေပါတယ်..."):
            output_file = "output.mp3"
            
            # Run async function
            asyncio.run(generate_tts(text_input, voice_id, speed, pitch, output_file))
            
            if os.path.exists(output_file):
                st.success("🎉 အသံဖိုင် ထွက်လာပါပြီ။")
                
                # အသံနားထောင်ရန် Player
                st.audio(output_file, format="audio/mp3")
                
                # အသံဒေါင်းလုဒ်လုပ်ရန် ခလုတ်
                with open(output_file, "rb") as f:
                    st.download_button(
                        label="📥 အသံဖိုင်ကိုရယူရန် (Download MP3)",
                        data=f,
                        file_name=f"myanmar_voice_{tone_option}.mp3",
                        mime="audio/mp3"
                    )
                  
