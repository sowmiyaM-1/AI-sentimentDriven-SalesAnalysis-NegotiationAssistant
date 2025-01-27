import speech_recognition as sr
import pyttsx3
import pandas as pd
import wave
import numpy as np
import librosa
from transformers import pipeline

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Load advanced sentiment and intent models
sentiment_analyzer = pipeline('sentiment-analysis')
intent_classifier = pipeline("text-classification", model="mrm8488/distilbert-base-multilingual-cased-finetuned-intent")

# Text-to-speech function
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Speech recognition function
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        try:
            audio = recognizer.listen(source)
            text = recognizer.recognize_google(audio)
            print(f"User said: {text}")
            return text, audio
        except sr.UnknownValueError:
            print("Sorry, I didn't catch that.")
            return None, None
        except sr.RequestError:
            print("Sorry, I'm having trouble connecting.")
            return None, None

# Advanced sentiment analysis function
def analyze_sentiment_advanced(text):
    sentiment_result = sentiment_analyzer(text)
    sentiment = sentiment_result[0]['label']
    score = sentiment_result[0]['score'] * 100
    if sentiment == 'POSITIVE':
        return 'Positive', score, 0, 100 - score
    elif sentiment == 'NEGATIVE':
        return 'Negative', 0, score, 100 - score
    else:
        return 'Neutral', 0, 0, 100

# Advanced tone analysis function
def analyze_tone_advanced(audio):
    with open("temp_audio.wav", "wb") as f:
        f.write(audio.get_wav_data())
    y, sr = librosa.load("temp_audio.wav", sr=None)
    avg_amplitude = np.mean(np.abs(y))
    energy = np.sum(y ** 2) / len(y)
    if avg_amplitude > 0.05 and energy > 0.01:
        return "Excited"
    elif avg_amplitude < 0.02 and energy < 0.005:
        return "Calm"
    else:
        return "Neutral"

# Advanced intent recognition function
def analyze_intent_advanced(text):
    intent_result = intent_classifier(text)
    return intent_result[0]['label']

# Provide advanced solution
def provide_solution_advanced(sentiment, intent):
    responses = {
        "greeting": "Hi there! How can I help you today?",
        "complaint": "I'm sorry to hear about the issue. Let me help resolve it.",
        "praise": "Thank you for your feedback! It motivates us to improve.",
        "question": "Sure, let me try to assist with your query.",
        "exit": "Goodbye! Feel free to come back anytime.",
    }
    if intent in responses:
        return responses[intent]
    if sentiment == "Negative":
        return "I sense some frustration. Could you elaborate on your concern?"
    elif sentiment == "Positive":
        return "That's great to hear! Tell me more about it."
    return "I'm not sure how to respond to that. Could you clarify?"

# Display results in a table format
def display_table(sentiment, positive, negative, neutral, intent, solution, tone):
    data = {
        "Sentiment": [sentiment],
        "Positive %": [f"{positive:.2f}"],
        "Negative %": [f"{negative:.2f}"],
        "Neutral %": [f"{neutral:.2f}"],
        "Intent": [intent],
        "Tone": [tone],
        "Solution": [solution]
    }
    df = pd.DataFrame(data)
    print(df)

# Main function to run the assistant
def run_assistant():
    while True:
        user_input, audio = listen()
        if user_input:
            if "exit" in user_input.lower():
                speak("Thank you!")
                break

            sentiment, positive, negative, neutral = analyze_sentiment_advanced(user_input)
            tone = analyze_tone_advanced(audio) if audio else "Neutral"
            intent = analyze_intent_advanced(user_input)
            solution = provide_solution_advanced(sentiment, intent)
            display_table(sentiment, positive, negative, neutral, intent, solution, tone)
            speak(f"Sentiment: {sentiment}. Positive: {positive:.2f}%. Negative: {negative:.2f}%. Neutral: {neutral:.2f}%. Tone: {tone}. Intent: {intent}.")
            speak(solution)
        else:
            speak("Please try again.")

if __name__ == "__main__":
    run_assistant()
