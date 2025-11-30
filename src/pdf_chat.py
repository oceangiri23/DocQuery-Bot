import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
import chromadb
import chromadb.utils.embedding_functions as embedding_functions
from text_processing import load_pdfs, split_txt_to_chunk, find_relevant_context
from prompt import create_prompt

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

google_ef = embedding_functions.GoogleGenerativeAiEmbeddingFunction(api_key=api_key)
client = chromadb.PersistentClient(path="embeddings/gemini")
collection = client.get_or_create_collection(name="pdf_rag", embedding_function=google_ef)
generative_model = genai.GenerativeModel("gemini-1.5-flash")

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
    if "pdf_processed" not in st.session_state:
        return "Please upload and process a PDF first."
    
    results = find_relevant_context(question, collection)
    
    prompt = create_prompt(query=question, context=results)
    answer = generate_answer(prompt)
    
    return answer


st.title("PDF-based Chatbot")
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