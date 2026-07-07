import streamlit as st
import edge_tts
import asyncio
import tempfile
import os

# ========== Page Config ==========
st.set_page_config(
    page_title="Myanmar TTS Pro", 
    page_icon="🎭", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ========== Header ==========
st.title("🎭 Myanmar TTS Pro - Style 15 မျိုး")
st.caption("Edge-TTS Powered | Card မလို | API မလို | 100% အလကား")

# ========== Instructions ==========
with st.expander("📖 အသုံးပြုနည်းလမ်းညွှန် - ဒီကိုနှိပ်ပြီးဖတ်ပါ", expanded=False):
    st.markdown("""
    ### 🚀 5 ချက်နဲ့ အသံထုတ်မယ်
    
    **Step 1: 🎤 အသံရွေးပါ**
    - **Nilar** = မိန်းကလေးအသံ၊ ချိုသာ၊ YouTube/Story အတွက်မိုက်
    - **Thiha** = ယောက်ျားလေးအသံ၊ ပြတ်သား၊ သတင်း/Documentary အတွက်မိုက်
    
    **Step 2: 🎭 Style ရွေးပါ - 15 မျိုးရှိတယ်**
    
    | Style | သုံးသင့်တဲ့နေရာ | ဥပမာ |
    | --- | --- | --- |
    | **သာမန်** | နေ့စဉ်စကားပြော၊ Tutorial | "ဒီနေ့တော့..." |
    | **ပျော်ရွှင်စရာ** | TikTok, Reels, ပျော်စရာ | "ဝိုး အရမ်းမိုက်တယ်!" |
    | **ဝမ်းနည်းစရာ** | Drama, သီချင်း, ခံစားချက် | "ငါတကယ်ဝမ်းနည်းတယ်..." |
    | **ဒေါသထွက်စရာ** | ရန်ဖြစ် Scene, Gaming | "တော်တော့! မခံနိုင်တော့ဘူး!" |
    | **ကြောက်လန့်စရာ** | Horror Story, သရဲကား | "ဟိုမှာ... ဟိုမှာ တစ်ခုခုရှိတယ်!" |
    | **တိုးတိုးလေး** | လျှို့ဝှက်ချက်, ASMR Intro | "တိုးတိုးပြောမယ်..." |
    | **သတင်းကြေညာသူ** | သတင်း, Documentary | "ယနေ့သတင်းအစီအစဉ်..." |
    | **ရုပ်ရှင်နမူနာ** | Movie Trailer, Epic Intro | "သမိုင်းသစ်ရေးမယ့် ဇာတ်ကား..." |
    | **ကလေးအသံ** | ကလေးပုံပြင်, ကာတွန်း | "ဟေး သူငယ်ချင်းတို့!" |
    | **အဘိုးကြီးအသံ** | ပုံပြင်, သမိုင်း | "ဟိုးရှေးရှေးတုန်းက..." |
    | **DJ/Host** | ပွဲဦးဆောင်, Podcast | "Welcome from the party!" |
    | **ASMR** | အိပ်ရာဝင်ပုံပြင်, Meditation | "စိတ်ကိုလျှော့ပြီး..." |
    | **ရုံးအစည်းအဝေး** | Presentation, Business | "မင်္ဂလာပါ လူကြီးမင်းများ..." |
    | **ပုံပြင်ပြောသူ** | ကလေးပုံပြင်, Audiobook | "တခါက တောထဲမှာ..." |
    | **Robot** | Sci-Fi, စက်ရုပ်ကာရိုက်တာ | "System activated..." |
    
    **Step 3: 📝 စာသားရိုက်ပါ**
    - မြန်မာလိုရိုက်ပါ ✅
    - စာကြောင်းအဆုံးမှာ `။` ထည့်ရင် ခဏရပ်မယ်
    - `!` `?` သုံးရင် အသံ ပိုအသက်ဝင်မယ်
    - ဥပမာ: `မင်္ဂလာပါ! ဒီနေ့ ရာသီဥတု အရမ်းကောင်းတယ်။`
    
    **Step 4: 🚀 "အသံထုတ်မယ်" နှိပ်ပါ**
    - 3-5 စက္ကန့်စောင့်ပါ
    - အသံထွက်လာရင် Play လုပ်နားထောင်ပါ
    
    **Step 5: 📥 Download လုပ်ပါ**
    - MP3 ဖိုင်ရပါမယ်
    - CapCut, TikTok, YouTube, Facebook မှာ တိုက်ရိုက်သုံးလို့ရတယ်
    
    ### 💡 Pro Tips
    1. **စာရှည်ရင် အပိုင်းပိုင်းခွဲပါ** → တစ်ခါကို 3-4 ကြောင်းပဲ ထုတ်ပါ
    2. **"အရမ်း" "တကယ်" "လုံးဝ" သုံးပါ** → အသံ ပိုခံစားချက်ပါမယ်
    3. **ASMR Style** → နားကြပ်တပ်နားထောင်ရင် ရှယ်မိုက်
    4. **ရုပ်ရှင်နမူနာ Style** → "..." ထည့်သုံးရင် Drama ဆန်မယ်
    
    ### ❌ ရှောင်ရန်
    - အင်္ဂလိပ်စာ သီးသန့် → မြန်မာအသံနဲ့ဖတ်ရင် ဝူးဝါးဖြစ်မယ်
    - စာလုံး 500 ကျော် တစ်ခါတည်းထုတ် → Error တက်နိုင်တယ်
    - Emoji 😂🔥 → မဖတ်တတ်ဘူး၊ ဖြုတ်ပါ
    
    ### 🆘 Error တက်ရင်
    1. **"Error" ပေါ်ရင်** → စာလုံးရေလျှော့ပြီး ပြန်စမ်းပါ
    2. **အသံမထွက်ရင်** → Browser Refresh လုပ်ပါ
    3. **ဖြည်းနေရင်** → Streamlit Free Plan မို့ ခဏစောင့်ပါ
    """)

st.divider()

# ========== Voice Selection ==========
st.subheader("🎤 1. အသံရွေးချယ်ပါ")
voice_options = {
    "Nilar - မိန်းကလေး (ချိုသာတယ်)": "my-MM-NilarNeural",
    "Thiha - ယောက်ျားလေး (ပြတ်သားတယ်)": "my-MM-ThihaNeural",
}

voice_name = st.selectbox(
    "အသံ", 
    list(voice_options.keys()),
    label_visibility="collapsed"
)
voice = voice_options[voice_name]

# ========== Style Selection ==========
st.subheader("🎭 2. Style ရွေးချယ်ပါ")
styles = {
    "1. သာမန် - နေ့စဉ်သုံး�": {"rate": "+0%", "pitch": "+0Hz", "vol": "+0%", "desc": "ပုံမှန်အတိုင်း"},
    "2. ပျော်ရွှင်စရာ - TikTok/Reels": {"rate": "+12%", "pitch": "+5Hz", "vol": "+15%", "desc": "မြန်၊ အသံမြင့်၊ စိတ်လှုပ်ရှား"},
    "3. ဝမ်းနည်းစရာ - Drama": {"rate": "-30%", "pitch": "-5Hz", "vol": "-15%", "desc": "ဖြည်း၊ အသံနိမ့်၊ ခံစားချက်"},
    "4. ဒေါသထွက်စရာ - Gaming": {"rate": "+15%", "pitch": "+4Hz", "vol": "+40%", "desc": "မြန်၊ ကျယ်၊ ပြတ်သား"},
    "5. ကြောက်လန့်စရာ - Horror": {"rate": "+20%", "pitch": "+6Hz", "vol": "+10%", "desc": "မြန်၊ တုန်လှုပ်"},
    "6. တိုးတိုးလေး - လျှို့ဝှက်": {"rate": "-15%", "pitch": "-2Hz", "vol": "-50%", "desc": "ဖြည်း၊ တိုးတိုး"},
    "7. သတင်းကြေညာသူ - MRTV": {"rate": "-8%", "pitch": "-3Hz", "vol": "+10%", "desc": "တည်ငြိမ်၊ ရှင်းလင်း"},
    "8. ရုပ်ရှင်နမူနာ - Epic": {"rate": "-12%", "pitch": "-4Hz", "vol": "+25%", "desc": "လေးနက်၊ ခမ်းနား"},
    "9. ကလေးအသံ - ကာတွန်း": {"rate": "+22%", "pitch": "+8Hz", "vol": "+5%", "desc": "အမြန်ဆုံး၊ အမြင့်ဆုံး"},
    "10. အဘိုးကြီးအသံ - ပုံပြင်": {"rate": "-35%", "pitch": "-6Hz", "vol": "-10%", "desc": "အဖြည်းဆုံး၊ အနိမ့်ဆုံး"},
    "11. DJ/Host - ပွဲဦးဆောင်": {"rate": "+5%", "pitch": "+2Hz", "vol": "+20%", "desc": "တက်ကြွ၊ စည်းချက်"},
    "12. ASMR - အိပ်ရာဝင်": {"rate": "-20%", "pitch": "-1Hz", "vol": "-60%", "desc": "အတိုးဆုံး၊ ဖြည်း"},
    "13. ရုံးအစည်းအဝေး - Professional": {"rate": "-3%", "pitch": "-1Hz", "vol": "+5%", "desc": "ပီသ၊ ယုံကြည်"},
    "14. ပုံပြင်ပြောသူ - Audiobook": {"rate": "-10%", "pitch": "+3Hz", "vol": "+10%", "desc": "နွေးထွေး၊ ဇာတ်လမ်း"},
    "15. Robot - Sci-Fi": {"rate": "-5%", "pitch": "-8Hz", "vol": "+0%", "desc": "ပြတ်သား၊ စက်ရုပ်"},
}

style_name = st.selectbox(
    "Style", 
    list(styles.keys()),
    label_visibility="collapsed"
)
config = styles[style_name]

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Speed", config["rate"])
with col2:
    st.metric("Pitch", config["pitch"])
with col3:
    st.metric("Volume", config["vol"])

st.caption(f"💡 {config['desc']}")

# ========== Custom Settings ==========
with st.expander("⚙️ ကိုယ်တိုင်အသေးစိတ်ချိန်ညှိမယ်"):
    c1, c2, c3 = st.columns(3)
    with c1:
        custom_rate = st.slider(
            "Speed", -50, 50, 
            int(config["rate"].replace("%","").replace("+","")),
            help="- အနှုတ်=ဖြည်း, + အပေါင်း=မြန်"
        )
    with c2:
        custom_pitch = st.slider(
            "Pitch", -10, 10, 
            int(config["pitch"].replace("Hz","").replace("+","")),
            help="- အနှုတ်=အသံနိမ့်, + အပေါင်း=အသံမြင့်"
        )
    with c3:
        custom_volume = st.slider(
            "Volume", -50, 50, 
            int(config["vol"].replace("%","").replace("+","")),
            help="- အနှုတ်=တိုးတိုး, + အပေါင်း=ကျယ်ကျယ်"
        )
    
    config["rate"] = f"{custom_rate:+d}%"
    config["pitch"] = f"{custom_pitch:+d}Hz"
    config["vol"] = f"{custom_volume:+d}%"

# ========== Text Input ==========
st.subheader("📝 3. စာသားရိုက်ထည့်ပါ")
text = st.text_area(
    "စာသား", 
    height=180, 
    placeholder="ဥပမာ: မင်္ဂလာပါ! ဒီနေ့ ရာသီဥတု အရမ်းကောင်းတယ်။ စိတ်ချမ်းသာစရာပဲ။",
    label_visibility="collapsed"
)

st.caption(f"စာလုံးရေ: {len(text)} / 500 (အများဆုံး 500 လောက်ပဲထုတ်ပါ)")

# ========== Generate Function ==========
async def make_audio(text, voice, rate, pitch, vol):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        filename = f.name
    
    # စာကြောင်းကြား Pause ထည့်မယ်
    text = text.replace("။", "။ ... ")
    text = text.replace(".", ". ... ")
    text = text.replace("!", "! ... ")
    text = text.replace("?", "? ... ")
    
    comm = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch, volume=vol)
    await comm.save(filename)
    
    with open(filename, "rb") as f:
        audio = f.read()
    os.unlink(filename)
    return audio

# ========== Generate Button ==========
st.subheader("🚀 4. အသံထုတ်မယ်")
if st.button("🎵 အသံထုတ်မယ်", use_container_width=True, type="primary"):
    if text.strip():
        if len(text) > 500:
            st.warning("⚠️ စာလုံးရေ 500 ကျော်နေတယ်။ အပိုင်းပိုင်းခွဲထုတ်ပါ")
        else:
            with st.spinner(f"{style_name} နဲ့ လုပ်နေတယ်... ခဏစောင့်ပါ"):
                try:
                    audio = asyncio.run(make_audio(
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
                        file_name=f"myanmar_tts_{style_name[:2]}.mp3",
                        mime="audio/mp3",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.info("💡 Tip: စာလုံးရေလျှော့ပြီး ပြန်စမ်းကြည့်ပါ။ ဒါမှမဟုတ် Refresh လုပ်ပါ။")
    else:
        st.warning("⚠️ စာသားအရင်ရိုက်ထည့်ပါ")

# ========== Footer ==========
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("✅ 100% Free")
with col2:
    st.caption("✅ Card မလို")
with col3:
    st.caption("✅ Unlimited")

st.caption("Made with ❤️ using Edge-TTS | Myanmar TTS Pro v2.0")
