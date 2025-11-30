import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
from user_info_validate import extract_date, validate_email, validate_phone_number
from prompt import create_prompt_for_form

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)
generative_model = genai.GenerativeModel("gemini-1.5-flash")


def generate_answer(question, answers):
    prompt = create_prompt_for_form(question, answers)
    result = generative_model.generate_content(prompt)
    return result.text

st.title("Conversational Form")


if "messages" not in st.session_state:
    st.session_state.messages = []
if "question_index" not in st.session_state:
    st.session_state.question_index = 0
if "responses" not in st.session_state:
    st.session_state.responses = {}


questions = [
    "What is your name?",
    "What is your email?",
    "What is your phone number?",
    "When would you like to book the appointment?"
]


def add_message(role, content):
    st.session_state.messages.append({"role": role, "content": content})


def handle_response():
    user_response = st.session_state.user_input.strip()
    if user_response:
        current_question = questions[st.session_state.question_index]

        if current_question == questions[1]:  
            if not validate_email(user_response):
                add_message("bot", "It seems the email you entered is invalid. Could you kindly provide a valid email address")
                return
            
        elif current_question == questions[2]:  
            if not validate_phone_number(user_response):
                add_message("bot", "The phone number you provided doesn't seem to be valid. Could you please enter a valid 10-digit phone number?")
                return
            
        elif current_question == questions[3]: 
            appointment_date = extract_date(user_response)
            if not appointment_date:
                add_message("bot", "Sorry, I couldn't understand the date. Please provide a valid date (e.g., Next Monday).")
                return   
            st.session_state.responses[current_question] = appointment_date
        else:
            st.session_state.responses[current_question] = user_response
        
        add_message("user", user_response)

        
       
        st.session_state.question_index += 1
        st.session_state.user_input = "" 
        if st.session_state.question_index < len(questions):
            next_question = generate_answer(questions[st.session_state.question_index],st.session_state.messages)
            add_message("bot", next_question)
        else:
            add_message("bot", "Thank you! for the response")

if not st.session_state.messages:
    add_message("bot", "Hello! I need some information from you.")
    add_message("bot", questions[0])

for message in st.session_state.messages:
    if message["role"] == "bot":
        with st.chat_message("assistant"):
            st.markdown(message["content"])
    else:
        with st.chat_message("user"):
            st.markdown(message["content"])

st.text_input("Type your response here...", key="user_input", on_change=handle_response)
