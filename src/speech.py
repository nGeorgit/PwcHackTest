import azure.cognitiveservices.speech as speechsdk
import streamlit as st
from src.config import SPEECH_KEY, SPEECH_REGION

def recognize_speech():
    """
    Uses Azure Speech SDK to listen to the default microphone and transcribe text.
    Returns:
        str: The transcribed text or None if failed.
    """
    try:
        print(f"DEBUG: Key='{SPEECH_KEY}', Region='{SPEECH_REGION}'")
# speech_config = speechsdk.SpeechConfig(...)
        speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION,speech_recognition_language="el-GR")
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)
        
        # Display a status indicator
        with st.sidebar.status("Listening...", expanded=True) as status:
            st.write("Speak into your microphone now.")
            result = speech_recognizer.recognize_once_async().get()
            
            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                status.update(label="Audio captured!", state="complete")
                return result.text
            elif result.reason == speechsdk.ResultReason.NoMatch:
                status.update(label="No speech recognized", state="error")
                return None
            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = result.cancellation_details
                status.update(label=f"Error: {cancellation_details.reason}", state="error")
                return None
                
    except Exception as e:
        print(f"Azure Speech Error: {e}")
        st.error(f"Azure Speech Error: {e}")
        return None