import google.generativeai as genai
from speech_recognition import Recognizer, Microphone
import pyttsx3
import pandas as pd
from datetime import datetime
import os
from textblob import TextBlob

# Configure Gemini API
api_key = ""
genai.configure(api_key=api_key)

# Initialize speech engine and recognizer
engine = pyttsx3.init()
recognizer = Recognizer()

# CRM file path
crm_file_path = "Crm_data.xlsx"

# Load CRM data
def load_crm_data(file_path):
    if os.path.exists(file_path):
        return pd.read_excel(file_path)
    else:
        return pd.DataFrame(columns=["Name", "Email", "Phone", "Company Name","Deal ID", "Date of Interaction", "Sentiment Score","User Complaint", "User Suggestions", "Refined Feedback", "Recommendations", "Deal Recommendations", "Post-Call Summary"])

#Name	Email	Phone	Company Name	Deal ID	Date of Interaction	Sentiment Score	User Suggestions	User Complaint	Refined Feedback	Recommendations	Deal Recommendations	Post-Call Summary	


# Save CRM data
def save_crm_data(file_path, crm_data):
    crm_data.to_excel(file_path, index=False)

# Text-to-speech
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Capture audio input
def capture_audio(prompt=None):
    if prompt:
        speak(prompt)
    
    with Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    
    try:
        print("Recognizing...")
        return recognizer.recognize_google(audio)
    except Exception as e:
        print(f"Error: {e}")
        return ""
    
def analyze_sentiment(text):
    blob = TextBlob(text)
    sentiment = blob.sentiment.polarity
    if sentiment > 0:
        return "Positive"
    elif sentiment < 0:
        return "Negative"
    else:
        return "Neutral"


# Refine text using Gemini API
def refine_text_with_gemini(input_text):
    model = genai.GenerativeModel("gemini-1.5-pro-latest")
    query = f"Refine the following user feedback for clarity: '{input_text}'"
    response = model.generate_content([query])
    return response.text

# Generate recommendations using Gemini API
def generate_recommendations(input_text, user_details):
    model = genai.GenerativeModel("gemini-1.5-pro-latest")
    query = (f"Based on the following user details: {user_details}, and the input feedback: "
             f"'{input_text}', provide tailored recommendations to improve user experience.")
    response = model.generate_content([query])
    return response.text

# Generate deal recommendations
def generate_deal_recommendations(crm_data, user_details):
    model = genai.GenerativeModel("gemini-1.5-pro-latest")
    historical_data = crm_data.to_dict(orient="records")
    query = (f"Using buyer needs, the following historical CRM data: {historical_data}, and competitor benchmarks, "
             f"suggest optimal deal terms for the user: {user_details}.")
    response = model.generate_content([query])
    return response.text

# Post-call analysis
def generate_post_call_summary(input_text, recommendations, deal_recommendations):
    model = genai.GenerativeModel("gemini-1.5-pro-latest")
    query = (f"Create a post-call analysis based on the conversation: '{input_text}', "
             f"recommendations: {recommendations}, and deal terms: {deal_recommendations}. Include a summary, "
             f"performance insights, and future engagement strategies.")
    response = model.generate_content([query])
    return response.text

# Main assistant function
def run_assistant():
    crm_data = load_crm_data(crm_file_path)
    
    while True:
        print("\nInteraction with customer begins.")
        speak("Please provide your name.")
        name = capture_audio()
        while not name:
            name = capture_audio("I couldn't hear your name. Please say it again.")
        
        speak("Please provide your email address.")
        email = capture_audio()
        while not email:
            email = capture_audio("I couldn't hear your email. Please say it again.")
        
        speak("Please provide your phone number.")
        phone = capture_audio()
        while not phone:
            phone = capture_audio("I couldn't hear your phone number. Please say it again.")
        
        speak("Please provide your company name.")
        company = capture_audio()
        while not company:
            company = capture_audio("I couldn't hear your company name. Please say it again.")
        
        speak("Please share your complaints.")
        complaint = capture_audio()
        while not complaint:
            complaint = capture_audio("I couldn't hear your complaints. Please provide them again.")
        
        speak("Do you have any suggestions for improvement?")
        suggestions = capture_audio()
        while not suggestions:
            suggestions = capture_audio("I couldn't hear your suggestions. Please provide them again.")
        
        # Refine feedback with Gemini API
        refined_feedback = refine_text_with_gemini(f"Complaints: {complaint} Suggestions: {suggestions}")
        print(f"Refined Feedback: {refined_feedback}")

        # Generate recommendations
        user_details = f"Name: {name}, Email: {email}, Phone: {phone}, Company: {company}"
        recommendations = generate_recommendations(refined_feedback, user_details)
        print(f"Generated Recommendations: {recommendations}")

        # Generate deal recommendations
        deal_recommendations = generate_deal_recommendations(crm_data, user_details)
        print(f"Deal Recommendations: {deal_recommendations}")

        # Post-call analysis
        post_call_summary = generate_post_call_summary(refined_feedback, recommendations, deal_recommendations)
        print(f"Post-Call Summary: {post_call_summary}")

        # Create a new record
        date_of_interaction = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_record = {
            "Name": name,
            "Email": email,
            "Phone": phone,
            "Company Name": company,
            "Deal ID": f"DEAL-{int(datetime.now().timestamp())}",
            "Date of Interaction": date_of_interaction,
            "Sentiment Score": analyze_sentiment(suggestions),
            "User Complaint": complaint,
            "User Suggestions": suggestions,
            "Refined Feedback": refined_feedback,
            "Recommendations": recommendations,
            "Deal Recommendations": deal_recommendations,
            "Post-Call Summary": post_call_summary
        }
        
        # Add to CRM
        crm_data = pd.concat([crm_data, pd.DataFrame([new_record])], ignore_index=True)
        save_crm_data(crm_file_path, crm_data)
        
        speak("Details successfully saved. Do you want to record another interaction? Say 'yes' to continue or 'no' to exit.")
        continue_input = capture_audio()
        if continue_input.lower() == "no":
            speak("Exiting the assistant. Goodbye!")
            break

# Run the assistant
run_assistant()


