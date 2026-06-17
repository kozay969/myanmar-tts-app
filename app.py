import streamlit as st
import asyncio
import edge_tts
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="Myanmar AI Text-to-Speech PRO", page_icon="🎙️")
st.title("🎙️ Myanmar AI Text-to-Speech PRO")
st.write("Storytelling နှင့် Movie Recap များအတွက် အဆင့်မြင့် မြန်မာအသံပြောင်းစနစ်")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("🎛️ အသံပြင်ဆင်မှုများ")

# ၁။ မြန်မာအသံ အမျိုးသား ၃ ယောက် နှင့် အမျိုးသမီး ၃ ယောက် (စုစုပေါင်း ၆ ယောက်) အတွက် သတ်မှတ်ခြင်း
voice_option = st.sidebar.selectbox(
    "မြန်မာအသံ ရွေးချယ်ပါ (Voices)",
    [
        "အမျိုးသမီး ၁ (Nilar - ပုံမှန်သံ)",
        "အမျိုးသမီး ၂ (Mya - အေးဆေးနူးညံ့သံ)",
        "အမျိုးသမီး ၃ (Chaw - ပြတ်သားသောသံ)",
        "အမျိုးသား ၁ (Thiha - သြဇာရှိ အဝေရာသံ)",
        "အမျိုးသား ၂ (Kyaw - တက်ကြွလှုံ့ဆော်သံ)",
        "အမျိုးသား ၃ (Aung - သဘာဝပြောသံ)"
    ]
)

# Edge-TTS ရဲ့ အခြေခံအသံကို Base ယူပြီး ကစားပါမည်
if "Thiha" in voice_option or "Kyaw" in voice_option or "Aung" in voice_option:
    base_voice = "my-MM-ThihaNeural"  # အမျိုးသားအသံအခြေခံ
else:
    base_voice = "my-MM-NilarNeural"  # အမျိုးသမီးအသံအခြေခံ


# ၂။ အသံ Tone ၅ မျိုး ရွေးချယ်ခြင်း
tone_option = st.sidebar.selectbox(
    "အသံ Tone ရွေးချယ်ပါ (Tones)",
    [
        "Normal (ပုံမှန်အတိုင်း)", 
        "Movie Recap (မြန်မြန်နှင့် စိတ်ဝင်စားစရာ)", 
        "Horror/Thriller (ခြောက်ခြားဖွယ်ရာ)", 
        "Documentary (အေးဆေးတည်ငြိမ်သော)",
        "Emotional/Drama (ဝမ်းနည်း ကြေကွဲဖွယ်)"
    ]
)

# ၃။ အနှေးအမြန်ကို Manual စိတ်ကြိုက်ထပ်ချိန်နိုင်အောင် Slider ထည့်ပေးခြင်း
manual_speed = st.sidebar.slider("အနှေးအမြန် စိတ်ကြိုက်ထပ်ချိန်ရန် (Speed)", min_value=0.5, max_value=1.5, value=1.0, step=0.1)

# Tone များအလိုက် Speed နှင့် Pitch (အသံအနိမ့်အမြင့်) ကို Dynamic ပြောင်းလဲခြင်း
speed_modifier = 0
pitch_modifier = 0

if tone_option == "Movie Recap (မြန်မြန်နှင့် စိတ်ဝင်စားစရာ)":
    speed_modifier = 15  # ၁၅ ရာခိုင်နှုန်း မြန်မယ်
    pitch_modifier = 1
elif tone_option == "Horror/Thriller (ခြောက်ခြားဖွယ်ရာ)":
    speed_modifier = -15 # ၁၅ ရာခိုင်နှုန်း နှေးမယ်
    pitch_modifier = -5  # အသံ အောသွားမယ်
elif tone_option == "Documentary (အေးဆေးတည်ငြိမ်သော)":
    speed_modifier = -5
    pitch_modifier = -2
elif tone_option == "Emotional/Drama (ဝမ်းနည်း ကြေကွဲဖွယ်)":
    speed_modifier = -10
    pitch_modifier = 2

# Voice ၆ ယောက်စာ ဖြစ်သွားအောင် Pitch ကို ထပ်မံကွဲပြားစေခြင်း
if "Mya" in voice_option: pitch_modifier += 3
elif "Chaw" in voice_option: pitch_modifier -= 3
elif "Kyaw" in voice_option: pitch_modifier += 4
elif "Aung" in voice_option: pitch_modifier -= 4

# Final Speed Calculation (Slider အပြင် Tone ပါ ပေါင်းစပ်တွက်ချက်မှု)
final_speed_percent = int((manual_speed - 1.0) * 100) + speed_modifier
final_speed_str = f"{'+' if final_speed_percent >= 0 else ''}{final_speed_percent}%"
final_pitch_str = f"{'+' if pitch_modifier >= 0 else ''}{pitch_modifier}Hz"

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
            
            asyncio.run(generate_tts(text_input, base_voice, final_speed_str, final_pitch_str, output_file))
            
            if os.path.exists(output_file):
                st.success("🎉 အသံဖိုင် ထွက်လာပါပြီ။")
                st.audio(output_file, format="audio/mp3")
                
                with open(output_file, "rb") as f:
                    st.download_button(
                        label="📥 အသံဖိုင်ကိုရယူရန် (Download MP3)",
                        data=f,
                        file_name=f"myanmar_voice_{voice_option}_{tone_option}.mp3",
                        mime="audio/mp3"
)
                    
