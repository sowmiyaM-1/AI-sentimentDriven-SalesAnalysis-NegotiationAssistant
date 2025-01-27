
import streamlit as st
import google.generativeai as genai


api_key = "key"

genai.configure(api_key=api_key)

def get_gemini_response(input_text, code_generation=False):
    model = genai.GenerativeModel('gemini-1.5-pro-latest')
    
    if code_generation:
        response = model.generate_content([f"Generate code : {input_text}"])
    else:
        response = model.generate_content([input_text])
    
    return response.text

st.header("Text Generation")

input_prompt = st.text_input("Input:", key="input")


submit = st.button("Generate Content")


if submit:
    if input_prompt:
        st.subheader("Generate:")
        response = get_gemini_response(input_prompt, code_generation=False) 
        st.write(response)
    


