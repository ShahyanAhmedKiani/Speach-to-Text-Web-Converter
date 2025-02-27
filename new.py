import streamlit as st
import speech_recognition as sr
from pydub import AudioSegment

# Add error handling for streamlit-webrtc
try:
    from streamlit_webrtc import webrtc_streamer
    webrtc_available = True
except ModuleNotFoundError:
    webrtc_available = False
    st.warning("Real-time functionality disabled (streamlit-webrtc not installed)")

# Rest of the code remains the same until the input method selection
st.set_page_config(page_title="Speech Recognition App", layout="wide")

st.title("🎤 Speech Recognition App")
st.markdown("""
This app demonstrates real-time speech recognition and audio file transcription.
- Use the microphone for live speech-to-text conversion
- Upload audio files (WAV format) for transcription
""")

with st.sidebar:
    st.header("Settings")
    recognizer_type = st.selectbox("Select Recognition Type", ("Google Web Speech API",))
    language = st.selectbox("Select Language", ("en-US", "es-ES", "fr-FR", "de-DE", "it-IT"))

recognizer = sr.Recognizer()

def process_audio_file(audio_file):
    try:
        # Check if ffmpeg is available
        try:
            audio_segment = AudioSegment.from_wav(audio_file)
        except Exception as e:
            return f"Error processing audio: {str(e)}. Ensure ffmpeg is installed and available in your PATH."

        audio_data = sr.AudioData(
            audio_segment.raw_data,
            sample_rate=audio_segment.frame_rate,
            sample_width=audio_segment.sample_width
        )
        text = recognizer.recognize_google(audio_data, language=language)
        return text
    except sr.UnknownValueError:
        return "Could not understand audio. Please check the audio quality or clarity."
    except sr.RequestError as e:
        return f"API unavailable: {str(e)}"

# Modified input method selection
input_method = st.radio(
    "Select Input Method:",
    ("Upload Audio File", "Real-time Microphone") if webrtc_available else ["Upload Audio File"],
    horizontal=True
)

if input_method == "Real-time Microphone" and webrtc_available:
    st.header("Real-time Speech Recognition")
    st.write("Click START to begin recording and speak into your microphone")
    
    def audio_callback(audio_frame):
        try:
            raw_audio = audio_frame.to_ndarray().tobytes()
            audio_data = sr.AudioData(raw_audio, sample_rate=16000, sample_width=2)
            text = recognizer.recognize_google(audio_data, language=language)
            return text
        except sr.UnknownValueError:
            return ""
        except sr.RequestError:
            return "API Error"

    from streamlit_webrtc import WebRtcMode

    webrtc_ctx = webrtc_streamer(
        key="speech-to-text",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
    )
    
    if webrtc_ctx.audio_receiver:
        st.subheader("Transcription:")
        st.write("Transcription will appear here once audio is processed.")

else:
    st.header("Audio File Transcription")
    uploaded_file = st.file_uploader("Upload WAV audio file", type=["wav"])
    
    if uploaded_file is not None:
        st.audio(uploaded_file, format="audio/wav")
        if st.button("Transcribe Audio"):
            with st.spinner("Processing audio..."):
                transcription = process_audio_file(uploaded_file)
            st.subheader("Transcription:")
            st.write(transcription)

st.markdown("---")
st.markdown("Made with ❤ using Streamlit and SpeechRecognition")
