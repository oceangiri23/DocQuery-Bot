from user_info_validate import validate_email, validate_phone_number, extract_date
from pdf_chat import process_pdf, get_answer
from form import add_message, questions, generate_answer
import streamlit as st
from save_to_json import save_booking_to_json


def handle_response():
    user_response = st.session_state.user_input.strip()
    if user_response:
        # Save user response for the current question in the predefined flow
        current_question = questions[st.session_state.question_index]

        if current_question == questions[1]:  
            if not validate_email(user_response):
                add_message("bot", "It seems the email you entered is invalid. Could you kindly provide a valid email address?")
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
            next_question = generate_answer(questions[st.session_state.question_index], st.session_state.messages)
            add_message("bot", next_question)
        else:
            add_message("bot", "Thank you for providing the information. Your appointment is booked!")
            save_booking_to_json(st.session_state.responses)

def initialize_chat():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "question_index" not in st.session_state:
        st.session_state.question_index = 0
    if "responses" not in st.session_state:
        st.session_state.responses = {}
    if "in_pdf_qa_mode" not in st.session_state:
        st.session_state.in_pdf_qa_mode = True  # Default mode is PDF Q&A

# Initialize the chatbot conversation
initialize_chat()

st.title("PDF-based Chatbot")
st.sidebar.header("Options")

# Sidebar buttons to switch between PDF Q&A and appointment booking
pdf_qa_button = st.sidebar.button("PDF Q&A")
appointment_button = st.sidebar.button("Book Appointment")

# Update mode based on button clicks
if pdf_qa_button:
    st.session_state.in_pdf_qa_mode = True
    st.session_state.messages.clear()
    add_message("bot", "You are now in PDF Q&A mode. Please upload a PDF to begin.")
elif appointment_button:
    st.session_state.in_pdf_qa_mode = False
    st.session_state.messages.clear()
    st.session_state.question_index = 0  # Reset to start from the first question
    add_message("bot", "You are now in appointment booking mode. Let's start with your information.")
    add_message("bot", questions[0])

uploaded_file = st.sidebar.file_uploader("Upload PDF", type=["pdf"], key="pdf_uploader") if st.session_state.in_pdf_qa_mode else None

if st.session_state.in_pdf_qa_mode:
    if uploaded_file:
        # Process the uploaded PDF only if not already processed
        with st.spinner("Processing PDF..."):
            process_status = process_pdf(uploaded_file)
        st.sidebar.success(process_status)

        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Handle PDF-based Q&A
        if user_input := st.chat_input("Ask me anything about the PDF..."):
            add_message("user", user_input)
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = get_answer(user_input)
                    st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
    else:
        st.write("Please upload a PDF to start interacting with the chatbot.")
else:
    # Appointment booking mode: display the predefined question/answer-based chat
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Input box for user response in appointment booking mode
    st.text_input("Type your response here...", key="user_input", on_change=handle_response)
