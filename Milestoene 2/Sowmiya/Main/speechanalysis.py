import os
import google.generativeai as genai

# IMPORTANT: Replace "YOUR_ACTUAL_API_KEY" with your actual Gemini API key.
YOUR_API_KEY = "actual gemini API key"

genai.configure(api_key=YOUR_API_KEY)


def upload_to_gemini(path, mime_type=None):
    file = genai.upload_file(path, mime_type=mime_type)
    print(f"Uploaded file '{file.display_name}' as: {file.uri}")
    return file


# Create the model
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash-exp",
    generation_config=generation_config,
    system_instruction="You are a tone analyzing agent. Analyze the tone and report the output in table format",
)

# TODO Make these files available on the local file system
# You may need to update the file paths
files = [
    upload_to_gemini("Recorded Audio December 30, 2024 - 9:21PM.ogg", mime_type="audio/ogg"),
]

chat_session = model.start_chat(
    history=[
        {
            "role": "user",
            "parts": [
                files[0],
            ],
        },
        {
            "role": "model",
            "parts": [
                "Okay, here's the tone analysis in table format:\n\n| Feature        | Analysis                                   |\n|----------------|--------------------------------------------|\n| **Tone**       | Casual, Friendly                        |\n| **Formality**   | Informal                                 |\n| **Emotion**    | Neutral, with a hint of warmth           |\n| **Purpose**    | Initiating a conversation, greeting someone |\n| **Intention**  |  To start a friendly and comfortable  interaction |\n",
            ],
        },
    ]
)

response = chat_session.send_message("Analyze the tone of the given audio file.")

print(response.text)
