import streamlit as st
import edge_tts
import asyncio
import tempfile
import os
import time

# ========== Page Config ==========
st.set_page_config(
    page_title="Myanmar TTS Pro", 
    page_icon="🎭", 
    layout="centered"
)

# ========== Header ==========
st.title("🎭 Myanmar TTS Pro - Unlimited")
st.caption("စာလုံးရေ အကန့်အသတ်မရှိ | Card မလို | 100% Free")

# ========== Instructions ==========
with st.expander("⚠️ Unlimited သုံးမယ်ဆိုရင် ဒါဖတ်ပါ", expanded=True):
    st.warning("""
    ### 🚨 အရေးကြီးသတိပေးချက်
    
    **စာလုံးရေ အကန့်အသတ်မရှိပေမယ့်:**
    
    1. **စာလုံး 1000 အောက်** → 5-10 စက္ကန့်၊ မြန်မြန်ရမယ် ✅
    2. **စာလုံး 1000-3000** → 20-40 စက္ကန့်၊ ခဏစောင့်ရမယ် ⏳
    3. **စာလုံး 3000-5000** → 1-2 မိနစ်၊ Timeout ဖြစ်နိုင်တယ် ⚠️
    4. **စာလုံး 5000 အထက်** → Streamlit Cloud မှာ သေချာပေါက်ရပ်မယ် ❌
    
    **💡 အကောင်းဆုံးနည်း:**
    - စာရှည်ရင် အပိုင်း 1000 လုံးစီခွဲပြီး ထုတ်ပါ
    - ဥပမာ: စာလုံး 5000 ဆို 5 ခါခွဲထုတ်ပြီး MP3 တွေ ပြန်ပေါင်းပါ
    - CapCut/Audacity နဲ့ MP3 တွေ ပေါင်းလို့ရတယ်
    """)

st.divider()

# ========== Voice Selection ==========
st.subheader("🎤 1. အသံရွေးချယ်ပါ")
voice_options = {
    "Nilar - မိန်းကလေး (ချိုသာတယ်)": "my-MM-NilarNeural",
    "Thiha - ယောက်ျားလေး (ပြတ်သားတယ်)": "my-MM-ThihaNeural",
}

voice_name = st.selectbox("အသံ", list(voice_options.keys()), label_visibility="collapsed")
voice = voice_options[voice_name]

# ========== Style Selection ==========
st.subheader("🎭 2. Style ရွေးချယ်ပါ")
styles = {
    "1. သာမန်": {"rate": "+0%", "pitch": "+0Hz", "vol": "+0%"},
    "2. ပျော်ရွှင်စရာ": {"rate": "+12%", "pitch": "+5Hz", "vol": "+15%"},
    "3. ဝမ်းနည်းစရာ": {"rate": "-30%", "pitch": "-5Hz", "vol": "-15%"},
    "4. ဒေါသထွက်စရာ": {"rate": "+15%", "pitch": "+4Hz", "vol": "+40%"},
    "5. ကြောက်လန့်စရာ": {"rate": "+20%", "pitch": "+6Hz", "vol": "+10%"},
    "6. တိုးတိုးလေး": {"rate": "-15%", "pitch": "-2Hz", "vol": "-50%"},
    "7. သတင်းကြေညာသူ": {"rate": "-8%", "pitch": "-3Hz", "vol": "+10%"},
    "8. ရုပ်ရှင်နမူနာ": {"rate": "-12%", "pitch": "-4Hz", "vol": "+25%"},
    "9. ကလေးအသံ": {"rate": "+22%", "pitch": "+8Hz", "vol": "+5%"},
    "10. အဘိုးကြီးအသံ": {"rate": "-35%", "pitch": "-6Hz", "vol": "-10%"},
    "11. DJ/Host": {"rate": "+5%", "pitch": "+2Hz", "vol": "+20%"},
    "12. ASMR": {"rate": "-20%", "pitch": "-1Hz", "vol": "-60%"},
    "13. ရုံးအစည်းအဝေး": {"rate": "-3%", "pitch": "-1Hz", "vol": "+5%"},
    "14. ပုံပြင်ပြောသူ": {"rate": "-10%", "pitch": "+3Hz", "vol": "+10%"},
    "15. Robot": {"rate": "-5%", "pitch": "-8Hz", "vol": "+0%"},
}

style_name = st.selectbox("Style", list(styles.keys()), label_visibility="collapsed")
config = styles[style_name]

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Speed", config["rate"])
with col2:
    st.metric("Pitch", config["pitch"])
with col3:
    st.metric("Volume", config["vol"])

# ========== Text Input - UNLIMITED ==========
st.subheader("📝 3. စာသားရိုက်ထည့်ပါ - အကန့်အသတ်မရှိ")
text = st.text_area(
    "စာသား", 
    height=300, 
    placeholder="စာလုံးရေ ဘယ်လောက်ရှည်ရှည် ရိုက်လို့ရတယ်...\n\nဒါပေမယ့် စာလုံး 3000 ကျော်ရင် ကြာမယ်၊ Timeout ဖြစ်နိုင်တယ်။",
    label_visibility="collapsed"
)

# စာလုံးရေပြမယ် + Warning
char_count = len(text)
if char_count == 0:
    st.caption("စာလုံးရေ: 0")
elif char_count < 1000:
    st.success(f"✅ စာလုံးရေ: {char_count} - မြန်မြန်ရမယ်")
elif char_count < 3000:
    st.warning(f"⚠️ စာလုံးရေ: {char_count} - 20-40 စက္ကန့်ကြာမယ်")
else:
    st.error(f"🚨 စာလုံးရေ: {char_count} - Timeout ဖြစ်နိုင်တယ်! အပိုင်းခွဲထုတ်တာ ပိုကောင်းမယ်")

# ========== Generate Function ==========
def split_text(text, max_len=400):
    """စာရှည်ရင် အပိုင်းပိုင်းခွဲမယ် - Edge-TTS Limit ရှောင်ဖို့"""
    if len(text) <= max_len:
        return [text]
    
    chunks = []
    # ဝါကျအလိုက် ခွဲမယ်
    sentences = text.replace("။", "။|").replace(".", ".|").replace("!", "!|").replace("?", "?|").split("|")
    
    current = ""
    for sent in sentences:
        if len(current) + len(sent) <= max_len:
            current += sent
        else:
            if current:
                chunks.append(current.strip())
            current = sent
    if current.strip():
        chunks.append(current.strip())
    
    return chunks

async def make_audio(text, voice, rate, pitch, vol):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        filename = f.name
    
    # Pause ထည့်မယ်
    text = text.replace("။", "။... ")
    text = text.replace(".", ".... ")
    text = text.replace("!", "!... ")
    text = text.replace("?", "?... ")
    
    comm = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch, volume=vol)
    await comm.save(filename)
    
    with open(filename, "rb") as f:
        audio = f.read()
    os.unlink(filename)
    return audio

async def make_unlimited_audio(text, voice, rate, pitch, vol):
    """စာဘယ်လောက်ရှည်ရှည် ရအောင်လုပ်မယ်"""
    chunks = split_text(text, max_len=400)
    audio_parts = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    start_time = time.time()
    
    for i, chunk in enumerate(chunks):
        status_text.text(f"အပိုင်း {i+1}/{len(chunks)} လုပ်နေတယ်... ({len(chunk)} လုံး)")
        try:
            audio_part = await make_audio(chunk, voice, rate, pitch, vol)
            audio_parts.append(audio_part)
            progress_bar.progress((i + 1) / len(chunks))
        except Exception as e:
            st.error(f"အပိုင်း {i+1} မှာ Error: {e}")
            break
    
    progress_bar.empty()
    status_text.empty()
    
    elapsed = time.time() - start_time
    st.caption(f"⏱️ ကြာချိန်: {elapsed:.1f} စက္ကန့်")
    
    # အပိုင်းတွေအားလုံးပေါင်းမယ်
    return b"".join(audio_parts)

# ========== Generate Button ==========
st.subheader("🚀 4. အသံထုတ်မယ်")
if st.button("🎵 အသံထုတ်မယ် - Unlimited", use_container_width=True, type="primary"):
    if text.strip():
        with st.spinner("လုပ်နေတယ်... စာရှည်ရင် ခဏစောင့်ပါ"):
            try:
                audio = asyncio.run(make_unlimited_audio(
                    text, 
                    voice,
                    config["rate"],
                    config["pitch"], 
                    config["vol"]
                ))
                st.balloons()
                st.success("✅ 5. ရပြီ! အောက်မှာ နားထောင်ပြီး Download လုပ်ပါ")
                st.audio(audio, format="audio/mp3")
                st.download_button(
                    label="📥 MP3 Download လုပ်မယ်",
                    data=audio,
                    file_name=f"myanmar_tts_unlimited.mp3",
                    mime="audio/mp3",
                    use_container_width=True
                )
                st.info(f"📊 စာလုံးရေ: {len(text)} | ဖိုင်ဆိုဒ်: {len(audio)/1024:.1f} KB | အပိုင်းပေါင်း: {len(split_text(text))}")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.warning("""
                **💡 Timeout ဖြစ်သွားတာဖြစ်နိုင်တယ်**
                
                ဖြေရှင်းနည်း:
                1. စာကို အပိုင်း 1000 လုံးစီခွဲပြီး ထုတ်ပါ
                2. MP3 တွေ ရလာရင် CapCut/Audacity နဲ့ ပြန်ပေါင်းပါ
                3. Streamlit Cloud Free Plan က 30 စက္ကန့်ပဲ ခွင့်ပြုလို့
                """)
    else:
        st.warning("⚠️ စာသားအရင်ရိုက်ထည့်ပါ")

# ========== Footer ==========
st.divider()
st.caption("Made with ❤️ | Edge-TTS | Unlimited Version v4.0")
st.caption("⚠️ စာလုံး 5000+ ဆို ကိုယ့်ကွန်ပျူတာမှာ Local Run တာပိုကောင်းတယ်")
