import azure.cognitiveservices.speech as speechsdk
import streamlit as st
from src.config import SPEECH_KEY, SPEECH_REGION
import re

def recognize_speech_from_file(audio_file_path):
    """
    Reads audio from a FILE (not the mic) and sends it to Azure.
    """
    try:
        speech_config = speechsdk.SpeechConfig(
            subscription=SPEECH_KEY, 
            region=SPEECH_REGION, 
            speech_recognition_language="el-GR"
        )
        
        # CRITICAL FIX: This tells Azure to listen to the FILE, not the hardware mic
        audio_config = speechsdk.audio.AudioConfig(filename=audio_file_path)
        
        speech_recognizer = speechsdk.SpeechRecognizer(
            speech_config=speech_config, 
            audio_config=audio_config  # <--- MUST BE INCLUDED
        )
        
        result = speech_recognizer.recognize_once_async().get()
        
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            return result.text
        elif result.reason == speechsdk.ResultReason.NoMatch:
            st.sidebar.error("No speech recognized.")
            return None
        elif result.reason == speechsdk.ResultReason.Canceled:
            st.sidebar.error(f"Azure Error: {result.cancellation_details.reason}")
            return None
            
    except Exception as e:
        st.error(f"Error: {e}")
        return None
    
def detect_language_voice(text):
    """
    Checks if the text contains Greek characters.
    Returns a Greek voice if yes, otherwise an English voice.
    """
    # Regex range for Greek characters
    if re.search(r'[\u0370-\u03FF]', text):
        return "el-GR-AthinaNeural"  # Greek Voice
    else:
        return "en-US-BrianNeural"   # English Voice (Clear, authoritative)

def text_to_speech(text):
    """
    Converts text to speech, dynamically selecting the language.
    """
    try:
        # 1. Determine the correct voice
        voice_name = detect_language_voice(text)
        
        # 2. Configure Speech
        speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
        speech_config.speech_synthesis_voice_name = voice_name
        
        # 3. Create Synthesizer
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)

        # 4. Speak
        result = speech_synthesizer.speak_text_async(text).get()

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            return result.audio_data
        elif result.reason == speechsdk.ResultReason.Canceled:
            print(f"Canceled: {result.cancellation_details.reason}")
            return None

    except Exception as e:
        print(f"TTS Error: {e}")
        return None