import sounddevice as sd
import speech_recognition as sr
import numpy as np
import google.generativeai as genai

# Configure the Gemini API with your API key
genai.configure(api_key="Actual key")

class ToneSentimentAnalyzer:
    def __init__(self, sample_rate=16000, chunk_size=1024, vad_threshold=0.02):
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.vad_threshold = vad_threshold
        self.recognizer = sr.Recognizer()

    def is_speech(self, audio_chunk):
        """Voice Activity Detection based on RMS amplitude."""
        rms = np.sqrt(np.mean(audio_chunk**2))
        return rms > self.vad_threshold

    def record_audio(self, duration=5):
        """Record audio for a fixed duration."""
        print("Listening...")
        try:
            audio = sd.rec(int(self.sample_rate * duration), samplerate=self.sample_rate, channels=1, dtype='float32')
            sd.wait()  # Wait until recording is finished
            return audio.flatten()
        except Exception as e:
            print(f"Error while recording audio: {e}")
            return None

    def convert_audio_to_text(self, audio_data):
        """Convert recorded audio to text using SpeechRecognition."""
        try:
            audio_data = (audio_data * 32767).astype(np.int16)  # Scale to int16
            audio = sr.AudioData(audio_data.tobytes(), self.sample_rate, 2)
            text = self.recognizer.recognize_google(audio)
            print(f"Transcription: {text}")
            return text
        except sr.UnknownValueError:
            print("Speech recognition could not understand audio.")
            return None
        except sr.RequestError as e:
            print(f"Speech recognition API error: {e}")
            return None

    def analyze_tone_with_gemini(self, text):
        """Analyze the tone using Google Gemini's Tone Analysis API."""
        try:
            # Send the text to Gemini for tone analysis
            generation_config = {
                "temperature": 1,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 500,
                "response_mime_type": "text/plain",
            }

            model = genai.GenerativeModel(
                model_name="gemini-2.0-flash-exp",
                generation_config=generation_config,
                system_instruction="You are a tone analyzing agent. Analyze the tone of the provided text and provide detailed results.",
            )

            response = model.predict(text)
            tone_analysis = response.text
            print(f"Tone Analysis: {tone_analysis}")
            return tone_analysis
        except Exception as e:
            print(f"Error during Gemini tone analysis: {e}")
            return None

    def start_analysis(self):
        """Start capturing audio and analyzing tone/sentiment."""
        audio_data = self.record_audio()

        if audio_data is not None and self.is_speech(audio_data):
            text = self.convert_audio_to_text(audio_data)
            if text:
                tone_analysis = self.analyze_tone_with_gemini(text)
                print("\nTone Analysis Complete:")
                print(tone_analysis)
        else:
            print("No speech detected or error in recording.")

if __name__ == "__main__":
    analyzer = ToneSentimentAnalyzer()
    try:
        while True:
            print("\nPress Enter to start recording or type 'exit' to quit.")
            user_input = input()
            if user_input.lower() == 'exit':
                break
            analyzer.start_analysis()
    except KeyboardInterrupt:
        print("\nExiting.")
