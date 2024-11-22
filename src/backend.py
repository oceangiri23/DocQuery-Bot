import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
import chromadb
import chromadb.utils.embedding_functions as embedding_functions
from text_processing import load_pdfs, split_txt_to_chunk, find_relevant_context
from prompt import create_prompt

# Load environment variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

# Initialize ChromaDB client and embedding function
google_ef = embedding_functions.GoogleGenerativeAiEmbeddingFunction(api_key=api_key)
client = chromadb.PersistentClient(path="embeddings/gemini")
collection = client.get_or_create_collection(name="pdf_rag", embedding_function=google_ef)
generative_model = genai.GenerativeModel("gemini-1.5-pro-latest")

# Define helper functions
def generate_answer(prompt):
    result = generative_model.generate_content(prompt)
    return result.text

def process_pdf(uploaded_file):
    """Processes an uploaded PDF file and stores its chunks if not processed already."""
    if "pdf_processed" not in st.session_state:  # Check if PDF is already processed
        # If not processed, process the PDF and store the embeddings
        text = load_pdfs(uploaded_file)
        chunks = split_txt_to_chunk(text, max_len=1500, chunk_overlap=200)
        
        # Store chunks in ChromaDB (Embedding storage)
        batch_size = 50
        for i in range(0, len(chunks), batch_size):
            batch_chunks = chunks[i:i + batch_size]
            batch_ids = [str(j) for j in range(i, i + len(batch_chunks))]
            collection.add(documents=batch_chunks, ids=batch_ids)
        
        # Mark PDF as processed
        st.session_state["pdf_processed"] = True
        st.session_state["pdf_text"] = text  # Store the PDF text for future reference
        return "PDF processed and data embedded successfully."
    
    else:
        return "PDF has already been processed."

def get_answer(question):
    """Generates an answer based on the uploaded PDF's context."""
    if "pdf_processed" not in st.session_state:  # Ensure the PDF is processed first
        return "Please upload and process a PDF first."
    
    # Retrieve the relevant context from ChromaDB (no need to reprocess the PDF)
    results = find_relevant_context(question, collection)
    
    # Create a prompt with the context and query
    prompt = create_prompt(query=question, context=results)
    
    # Generate the answer using the generative model
    answer = generate_answer(prompt)
    
    return answer


# Streamlit UI
st.title("PDF-based Chatbot")
st.sidebar.header("Upload a PDF to begin")
uploaded_file = st.sidebar.file_uploader("Upload PDF", type=["pdf"])

if uploaded_file:
    # Process the uploaded PDF only if not already processed
    with st.spinner("Processing PDF..."):
        process_status = process_pdf(uploaded_file)
    st.sidebar.success(process_status)

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if user_input := st.chat_input("Ask me anything about the PDF..."):
        # Display user message
        with st.chat_message("user"):
            st.markdown(user_input)
        # Add user input to history
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = get_answer(user_input)
                st.markdown(response)
        # Add assistant response to history
        st.session_state.messages.append({"role": "assistant", "content": response})
else:
    st.write("Please upload a PDF to start interacting with the chatbot.")