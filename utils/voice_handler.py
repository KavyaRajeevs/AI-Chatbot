import streamlit as st
import tempfile
import os
import threading
import queue
from typing import Optional
import time

class VoiceHandler:
    """Enhanced voice input/output handler"""
    
    def __init__(self):
        self.is_recording = False
        self.is_speaking = False
        self.speech_queue = queue.Queue()
        self.setup_voice_libraries()
    
    def setup_voice_libraries(self):
        """Setup voice recognition and synthesis libraries"""
        self.sr_available = False
        self.tts_available = False
        self.recognizer = None
        self.microphone = None
        self.tts_engine = None

        # Speech recognition setup
        try:
            import speech_recognition as sr
            self.recognizer = sr.Recognizer()
            try:
                self.microphone = sr.Microphone()
            except OSError:
                self.microphone = None
                print("Warning: No default input device available. Voice features disabled.")
            self.sr_available = self.microphone is not None
            # Adjust for ambient noise only if microphone is available
            if self.microphone is not None:
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
        except ImportError:
            self.sr_available = False
            st.warning("Speech recognition not available. Install: pip install SpeechRecognition pyaudio")
        except Exception as e:
            self.sr_available = False
            st.warning(f"Speech recognition initialization failed: {str(e)}")

        # Text-to-speech setup
        try:
            import pyttsx3
            self.tts_engine = pyttsx3.init()
            self.tts_available = True
            # Configure TTS settings
            self.tts_engine.setProperty('rate', 180)  # Speed of speech
            self.tts_engine.setProperty('volume', 0.8)  # Volume level
            # Get available voices
            voices = self.tts_engine.getProperty('voices')
            if voices:
                # Try to set a pleasant voice (usually female voice is at index 1)
                if len(voices) > 1:
                    self.tts_engine.setProperty('voice', voices[1].id)
                else:
                    self.tts_engine.setProperty('voice', voices[0].id)
        except ImportError:
            self.tts_available = False
            st.warning("Text-to-speech not available. Install: pip install pyttsx3")
        except Exception as e:
            self.tts_available = False
            st.warning(f"TTS initialization failed: {str(e)}")
    
    def start_recording(self) -> bool:
        """Start voice recording in a separate thread"""
        if not self.sr_available:
            st.error("Speech recognition not available or no input device found")
            return False
        if self.is_recording:
            return False
        self.is_recording = True
        thread = threading.Thread(target=self._record_audio)
        thread.daemon = True
        thread.start()
        return True
    
    def stop_recording(self) -> Optional[str]:
        """Stop recording and return transcribed text"""
        if not self.is_recording:
            return None
        self.is_recording = False
        # Wait for recording to finish and get result
        try:
            result = self.speech_queue.get(timeout=5)
            return result if result != "ERROR" else None
        except queue.Empty:
            return None
    
    def _record_audio(self):
        """Internal method to handle audio recording"""
        try:
            import speech_recognition as sr
            if self.microphone is None or self.recognizer is None:
                self.speech_queue.put("ERROR")
                st.warning("No microphone available for recording.")
                return
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=30)
            # Convert audio to text using Google Speech Recognition
            try:
                text = self.recognizer.recognize_google(audio)
                self.speech_queue.put(text)
            except sr.UnknownValueError:
                self.speech_queue.put("ERROR")
                st.warning("Could not understand audio")
            except sr.RequestError as e:
                self.speech_queue.put("ERROR")
                st.error(f"Speech recognition error: {e}")
        except Exception as e:
            self.speech_queue.put("ERROR")
            st.error(f"Recording error: {e}")
        finally:
            self.is_recording = False
    
    def speak_text(self, text: str, async_mode: bool = True):
        """Convert text to speech"""
        if not self.tts_available:
            st.warning("Text-to-speech not available")
            return
        if self.is_speaking:
            self.stop_speaking()
        if async_mode:
            thread = threading.Thread(target=self._speak_async, args=(text,))
            thread.daemon = True
            thread.start()
        else:
            self._speak_sync(text)
    
    def _speak_async(self, text: str):
        """Async text-to-speech"""
        self.is_speaking = True
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            st.error(f"TTS error: {e}")
        finally:
            self.is_speaking = False
    
    def _speak_sync(self, text: str):
        """Synchronous text-to-speech"""
        self.is_speaking = True
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            st.error(f"TTS error: {e}")
        finally:
            self.is_speaking = False
    
    def stop_speaking(self):
        """Stop current speech output"""
        if self.tts_available and self.is_speaking:
            try:
                self.tts_engine.stop()
                self.is_speaking = False
            except Exception as e:
                st.error(f"Error stopping TTS: {e}")
    
    def is_recording_active(self) -> bool:
        """Check if recording is currently active"""
        return self.is_recording
    
    def is_speaking_active(self) -> bool:
        """Check if TTS is currently active"""
        return self.is_speaking
    
    def get_available_voices(self) -> list:
        """Get list of available TTS voices"""
        if not self.tts_available:
            return []
        try:
            voices = self.tts_engine.getProperty('voices')
            return [{"id": voice.id, "name": voice.name} for voice in voices] if voices else []
        except Exception:
            return []
    
    def set_voice(self, voice_id: str):
        """Set TTS voice by ID"""
        if not self.tts_available:
            return False
        try:
            self.tts_engine.setProperty('voice', voice_id)
            return True
        except Exception as e:
            st.error(f"Error setting voice: {e}")
            return False
    
    def set_speech_rate(self, rate: int):
        """Set TTS speech rate (words per minute)"""
        if not self.tts_available:
            return False
        try:
            # Clamp rate between 50 and 300
            rate = max(50, min(300, rate))
            self.tts_engine.setProperty('rate', rate)
            return True
        except Exception as e:
            st.error(f"Error setting speech rate: {e}")
            return False
    
    def set_volume(self, volume: float):
        """Set TTS volume (0.0 to 1.0)"""
        if not self.tts_available:
            return False
        try:
            # Clamp volume between 0.0 and 1.0
            volume = max(0.0, min(1.0, volume))
            self.tts_engine.setProperty('volume', volume)
            return True
        except Exception as e:
            st.error(f"Error setting volume: {e}")
            return False
    
    def save_audio_to_file(self, text: str, filename: str):
        """Save TTS audio to file"""
        if not self.tts_available:
            return False
        try:
            self.tts_engine.save_to_file(text, filename)
            self.tts_engine.runAndWait()
            return True
        except Exception as e:
            st.error(f"Error saving audio to file: {e}")
            return False
    
    def cleanup(self):
        """Clean up resources"""
        self.stop_speaking()
        self.is_recording = False
        # Clear the speech queue
        while not self.speech_queue.empty():
            try:
                self.speech_queue.get_nowait()
            except queue.Empty:
                break

# Example usage functions for Streamlit integration
def create_voice_ui(voice_handler: VoiceHandler):
    """Create voice input/output UI components"""
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🎤 Start Recording", disabled=voice_handler.is_recording_active()):
            if voice_handler.start_recording():
                st.success("Recording started... Speak now!")
    with col2:
        if st.button("⏹️ Stop Recording", disabled=not voice_handler.is_recording_active()):
            text = voice_handler.stop_recording()
            if text:
                st.session_state.voice_input = text
                st.success(f"Recorded: {text}")
            else:
                st.error("No speech detected or recording failed")
    with col3:
        if st.button("🔇 Stop Speaking", disabled=not voice_handler.is_speaking_active()):
            voice_handler.stop_speaking()
            st.success("Speech stopped")
    # Status indicators
    if voice_handler.is_recording_active():
        st.info("🎤 Recording in progress...")
    if voice_handler.is_speaking_active():
        st.info("🔊 Speaking...")
    # Voice settings
    with st.expander("Voice Settings"):
        # Speech rate
        rate = st.slider("Speech Rate (WPM)", 50, 300, 180)
        if st.button("Set Rate"):
            voice_handler.set_speech_rate(rate)
            st.success(f"Speech rate set to {rate} WPM")
        # Volume
        volume = st.slider("Volume", 0.0, 1.0, 0.8, 0.1)
        if st.button("Set Volume"):
            voice_handler.set_volume(volume)
            st.success(f"Volume set to {volume}")
        # Voice selection
        voices = voice_handler.get_available_voices()
        if voices:
            voice_names = [f"{v['name']} ({v['id']})" for v in voices]
            selected_voice = st.selectbox("Select Voice", voice_names)
            if st.button("Set Voice"):
                voice_id = voices[voice_names.index(selected_voice)]['id']
                if voice_handler.set_voice(voice_id):
                    st.success("Voice changed successfully")

def demo_voice_chat():
    """Demo function showing how to use VoiceHandler in a chat application"""
    st.title("Voice Chat Demo")
    # Initialize voice handler
    if 'voice_handler' not in st.session_state:
        st.session_state.voice_handler = VoiceHandler()
    voice_handler = st.session_state.voice_handler
    # Create voice UI
    create_voice_ui(voice_handler)
    # Text input area
    if 'voice_input' in st.session_state:
        user_input = st.text_area("Your message:", value=st.session_state.voice_input, key="user_message")
        del st.session_state.voice_input
    else:
        user_input = st.text_area("Your message:", key="user_message")
    # Send button
    if st.button("Send") and user_input:
        # Echo the message (replace with your chat logic)
        response = f"You said: {user_input}"
        st.write(response)
        # Speak the response
        if st.checkbox("Speak response"):
            voice_handler.speak_text(response)
    # Cleanup on app exit
    if st.button("Cleanup"):
        voice_handler.cleanup()
        st.success("Voice handler cleaned up")

# Run demo if this file is executed directly
if __name__ == "__main__":
    demo_voice_chat()