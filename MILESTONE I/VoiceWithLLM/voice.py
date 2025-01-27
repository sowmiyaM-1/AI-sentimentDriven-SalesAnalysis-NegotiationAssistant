
import pyttsx3 
import speech_recognition as sr 
from transformers import pipeline 
import time
llm = pipeline("text-generation", model="gpt2", device=-1)

tts_engine = pyttsx3.init()
def recognize_speech():

    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source) 
        try:
            audio = recognizer.listen(source)
            print("Recognizing...")
            text = recognizer.recognize_google(audio)  
            print(f"User said: {text}")
            return text
        except sr.UnknownValueError:
            return "Sorry, I didn't understand that."
        except sr.RequestError as e:
            return f"Speech recognition error: {e}"
def generate_response(input_text):
    
    print(f"User Input: {input_text}")
    response = llm(input_text, max_length=50, truncation=True)[0]["generated_text"]
    print(f"LLM Response: {response}")
    return response
def speak_response(response_text):
    
    print(f"Speaking: {response_text}")
    tts_engine.say(response_text)  
    tts_engine.runAndWait() 
def main():
    while True:
        print("Say something...")
        user_input = recognize_speech()  
        
        if user_input.lower() == "exit":
            print("Exiting...")
            speak_response("Goodbye!")
            break
        response = generate_response(user_input)
        speak_response(response)
        
        time.sleep(1)  
        
main()