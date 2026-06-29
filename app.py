import streamlit as st
import edge_tts
import tempfile
import os
import asyncio

# Page config
st.set_page_config(
    page_title="Myanmar TTS App",
    page_icon="🔊",
    layout="centered"
)

# Mobile friendly CSS
st.markdown("""
<style>
    .stTextArea textarea {
        font-size: 18px !important;
        min-height: 150px !important;
    }
    .stButton button {
        width: 100% !important;
        padding: 15px !important;
        font-size: 18px !important;
        border-radius: 10px !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        font-weight: bold !important;
    }
    @media (max-width: 768px) {
        .stApp {
            padding: 10px !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# Title
st.title("🔊 Myanmar TTS App")
st.caption("အခမဲ့ Edge TTS ကို အသုံးပြုထားသည်")

# Voice options
voice_options = {
    "US English - Jenny (Female)": "en-US-JennyNeural",
    "US English - Guy (Male)": "en-US-GuyNeural",
    "UK English - Sonia (Female)": "en-GB-SoniaNeural",
    "UK English - Ryan (Male)": "en-GB-RyanNeural",
    "Australian English - Natasha (Female)": "en-AU-NatashaNeural",
    "Australian English - William (Male)": "en-AU-WilliamNeural",
    "Indian English - Neerja (Female)": "en-IN-NeerjaNeural",
    "Indian English - Prabhat (Male)": "en-IN-PrabhatNeural",
}

# Sidebar settings
with st.sidebar:
    st.header("⚙️ Settings")
    selected_voice_name = st.selectbox("Select Voice", list(voice_options.keys()))
    selected_voice = voice_options[selected_voice_name]
    
    rate = st.slider("Speed", -50, 100, 0, 5, help="-50% to +100%")
    rate_str = f"{rate:+d}%"
    
    pitch = st.slider("Pitch", -12, 12, 0, 1, help="-12Hz to +12Hz")
    pitch_str = f"{pitch:+d}Hz"

# Text input
text_input = st.text_area(
    "📝 Enter text to convert to speech",
    height=150,
    placeholder="Type or paste your text here..."
)

# Function to generate audio
def generate_audio(text, voice, rate, pitch):
    """Generate audio using edge-tts"""
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            output_file = tmp_file.name
        
        # Run async function
        async def run_tts():
            communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
            await communicate.save(output_file)
        
        # Run the async function
        asyncio.run(run_tts())
        
        # Read the audio file
        with open(output_file, "rb") as f:
            audio_bytes = f.read()
        
        # Clean up
        os.unlink(output_file)
        
        return audio_bytes, None
        
    except Exception as e:
        return None, str(e)

# Generate button
if st.button("🚀 Generate Speech", use_container_width=True):
    if not text_input.strip():
        st.error("⚠️ Please enter some text!")
    else:
        with st.spinner("🎤 Generating audio... Please wait."):
            audio_bytes, error = generate_audio(
                text_input, 
                selected_voice, 
                rate_str, 
                pitch_str
            )
            
            if error:
                st.error(f"❌ Error: {error}")
            else:
                # Play audio
                st.audio(audio_bytes, format="audio/mp3")
                
                # Download button
                st.download_button(
                    label="📥 Download MP3",
                    data=audio_bytes,
                    file_name="tts_output.mp3",
                    mime="audio/mp3",
                    use_container_width=True
                )
                
                st.success("✅ Audio generated successfully!")

# Footer
st.divider()
st.caption("💡 Powered by Microsoft Edge TTS | Free to use")
