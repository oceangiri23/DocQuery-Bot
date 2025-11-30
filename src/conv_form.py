import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
import chromadb
import chromadb.utils.embedding_functions as embedding_functions
from text_processing import load_pdfs, split_txt_to_chunk, find_relevant_context
from prompt import create_prompt
import dateparser
import re


load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

google_ef = embedding_functions.GoogleGenerativeAiEmbeddingFunction(api_key=api_key)
client = chromadb.PersistentClient(path="embeddings/gemini")
collection = client.get_or_create_collection(name="pdf_rag", embedding_function=google_ef)
generative_model = genai.GenerativeModel("gemini-1.5-pro-latest")

def validate_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

def validate_phone(phone):
    return re.match(r"^\+?\d{7,15}$", phone) is not None

def parse_date(user_input):
    date = dateparser.parse(user_input)
    return date.strftime("%Y-%m-%d") if date else None

def generate_answer(prompt):
    result = generative_model.generate_content(prompt)
    return result.text

def process_pdf(uploaded_file):
    """Processes an uploaded PDF file and stores its chunks if not processed already."""
    if "pdf_processed" not in st.session_state:  
        text = load_pdfs(uploaded_file)
        chunks = split_txt_to_chunk(text, max_len=1500, chunk_overlap=200)
        
        batch_size = 50
        for i in range(0, len(chunks), batch_size):
            batch_chunks = chunks[i:i + batch_size]
            batch_ids = [str(j) for j in range(i, i + len(batch_chunks))]
            collection.add(documents=batch_chunks, ids=batch_ids)
        
        st.session_state["pdf_processed"] = True
        st.session_state["pdf_text"] = text 
        return "PDF processed and data embedded successfully."
    
    else:
        return "PDF has already been processed."

def get_answer(question):
    """Generates an answer based on the uploaded PDF's context."""
    if "pdf_processed" not in st.session_state: 
        return "Please upload and process a PDF first."
    
    if "call me" in question.lower() or "book an appointment" in question.lower():
        return start_conversational_form()
    results = find_relevant_context(question, collection)
    prompt = create_prompt(query=question, context=results)

    answer = generate_answer(prompt)
    
    return answer

def start_conversational_form():
    """Handles the conversational form collection for name, phone, email, and date."""
    st.subheader("Provide Your Details for Call or Appointment")
    
    
    name = st.text_input("Name")
    phone = st.text_input("Phone Number (e.g., +1234567890)")
    email = st.text_input("Email")
    date_input = st.text_input("Preferred Date (e.g., Next Monday)")
    
   
    if st.button("Submit"):
        if not name:
            st.error("Name is required.")
        elif not validate_phone(phone):
            st.error("Invalid phone number format.")
        elif not validate_email(email):
            st.error("Invalid email format.")
        else:
            preferred_date = parse_date(date_input)
            if not preferred_date:
                st.error("Please enter a recognizable date format (e.g., 'next Monday').")
            else:
                st.success("Your appointment request has been submitted!")
                st.session_state.user_info = {"name": name, "phone": phone, "email": email, "date": preferred_date}
                return f"Thank you, {name}. We will contact you on {preferred_date} at {phone}."
    
    return "Please fill out the form to book an appointment."

# Streamlit UI
st.title("PDF-based Chatbot with Appointment Booking")
st.sidebar.header("Upload a PDF to begin")
uploaded_file = st.sidebar.file_uploader("Upload PDF", type=["pdf"])

if uploaded_file:
    with st.spinner("Processing PDF..."):
        process_status = process_pdf(uploaded_file)
    st.sidebar.success(process_status)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if user_input := st.chat_input("Ask me anything about the PDF..."):
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = get_answer(user_input)
                st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
else:
    st.write("Please upload a PDF to start interacting with the chatbot.")
