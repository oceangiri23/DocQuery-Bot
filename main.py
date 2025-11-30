import os
import json
import glob
from dotenv import load_dotenv
from openai import OpenAI
import gradio as gr
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_classic.chains import ConversationalRetrievalChain
from langchain_classic.memory import ConversationBufferMemory

from src.conversational_form import save_form_to_json, handle_tool_call, chat as chat_form
from src.RAG import build_knowledgebase, chat as chat_rag

load_dotenv(override=True)
openai_api_key = os.getenv('OPENAI_API_KEY')
MODEL = "gpt-4o-mini"
openai = OpenAI()

conversation_chain = None

system_message = (
    "You are a helpful conversational form assistant. "
    "Collect user name, email, and phone number. "
    "If some information is missing, ask only about the missing field. "
    "Keep responses short and polite. "
    "When all fields are collected, call the function."
)

form_function = {
    "name": "submit_user_form",
    "description": "Submit a user form with name, email, and phone. Ask for missing values if not provided.",
    "parameters": {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Full name of the user"},
            "email": {"type": "string", "description": "User email"},
            "phone": {"type": "string", "description": "User phone number"}
        },
        "required": ["name", "email", "phone"],
        "additionalProperties": False
    }
}

tools = [{"type": "function", "function": form_function}]

with gr.Blocks() as app:
    gr.Markdown("# 🤖 AI Assistant Hub")
    with gr.Row():
        with gr.Column(scale=1, min_width=200):
            gr.Markdown("### 🎯 Navigation")
            form_btn = gr.Button("📝 Conversational Form", variant="primary", size="lg")
            rag_btn = gr.Button("📚 RAG Chatbot", variant="secondary", size="lg")
        
        with gr.Column(scale=4):
            with gr.Column(visible=True) as form_interface:
                gr.Markdown("## 📝 Conversational Form Assistant")
                gr.Markdown("I'll help you fill out a form by collecting your name, email, and phone number.")
                
                form_chatbot = gr.Chatbot(height=500)
                form_msg = gr.Textbox(
                    label="Your message",
                    placeholder="Type your message here...",
                    show_label=False
                )
                form_clear = gr.Button("Clear")
                
                def respond_form(message, chat_history):
                    bot_message = chat_form(message, chat_history)
                    chat_history.append((message, bot_message))
                    return "", chat_history
                
                form_msg.submit(respond_form, [form_msg, form_chatbot], [form_msg, form_chatbot])
                form_clear.click(lambda: None, None, form_chatbot, queue=False)
            
            with gr.Column(visible=False) as rag_interface:
                gr.Markdown("## 📚 RAG Chatbot")
                gr.Markdown("Upload documents to build a knowledge base, then ask questions about them.")
                
                file_input = gr.File(
                    label="Upload Documents (PDF or TXT)", 
                    file_count="multiple",
                    file_types=[".pdf", ".txt"]
                )
                upload_btn = gr.Button("🔨 Build Knowledge Base", variant="primary")
                status_output = gr.Textbox(label="Status", interactive=False)
                
                rag_chatbot = gr.Chatbot(height=400)
                rag_msg = gr.Textbox(
                    label="Your question",
                    placeholder="Ask a question about your documents...",
                    show_label=False
                )
                rag_clear = gr.Button("Clear")
                
                def respond_rag(message, chat_history):
                    bot_message = chat_rag(message, chat_history)
                    chat_history.append((message, bot_message))
                    return "", chat_history
                
                upload_btn.click(
                    build_knowledgebase, 
                    inputs=file_input, 
                    outputs=status_output
                )
                rag_msg.submit(respond_rag, [rag_msg, rag_chatbot], [rag_msg, rag_chatbot])
                rag_clear.click(lambda: None, None, rag_chatbot, queue=False)
    def show_form():
        return {
            form_interface: gr.update(visible=True),
            rag_interface: gr.update(visible=False),
            form_btn: gr.update(variant="primary"),
            rag_btn: gr.update(variant="secondary")
        }
    def show_rag():
        return {
            form_interface: gr.update(visible=False),
            rag_interface: gr.update(visible=True),
            form_btn: gr.update(variant="secondary"),
            rag_btn: gr.update(variant="primary")
        }
    form_btn.click(
        show_form,
        outputs=[form_interface, rag_interface, form_btn, rag_btn]
    )
    rag_btn.click(
        show_rag,
        outputs=[form_interface, rag_interface, form_btn, rag_btn]
    )

if __name__ == "__main__":
    app.launch(share=True)