import os
import glob
from dotenv import load_dotenv
import gradio as gr
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_classic.chains import ConversationalRetrievalChain
from langchain_classic.memory import ConversationBufferMemory
import tempfile
import os

conversation_chain = None

MODEL = "gpt-4o-mini"
db_name = "vector_db"

load_dotenv(override=True)
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY', 'your-key-if-not-using-env')

def build_knowledgebase(files):
    global conversation_chain
    all_docs = []
    for file in files:
        temp_path = file.name
        ext = os.path.splitext(temp_path)[1].lower()
        if ext == ".pdf":
            loader = PyPDFLoader(temp_path)
        else:
            loader = TextLoader(temp_path)
        docs = loader.load()
        all_docs.extend(docs)
    splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(all_docs)
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma.from_documents(chunks, embedding=embeddings)

    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=MODEL,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )
    return "Knowledge base built successfully! You may now chat."

def chat(message, history):
    global conversation_chain
    if conversation_chain is None:
        return "⚠ Please upload documents first."
    result = conversation_chain.invoke({"question": message})
    return result["answer"]


with gr.Blocks() as app:
    gr.Markdown("#  RAG Chatbot Inside Gradio")
    file_input = gr.File(label="Upload Documents", file_count="multiple")
    upload_btn = gr.Button("Build Knowledge Base")
    output = gr.Textbox(label="Status")
    chat_ui = gr.ChatInterface(chat)
    upload_btn.click(build_knowledgebase, inputs=file_input, outputs=output)



app.launch(share=True)


