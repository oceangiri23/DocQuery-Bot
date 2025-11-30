# AI Assistant Hub: RAG Chatbot + Conversational Form

A dual-mode AI assistant combining Retrieval-Augmented Generation (RAG) for document Q&A and function-calling capabilities for conversational form processing.

## 🏗️ Architecture

**Tech Stack:**
- **LLM:** OpenAI GPT-4o-mini
- **Framework:** LangChain + Gradio
- **Vector Store:** ChromaDB
- **Embeddings:** OpenAI Ada-002

## ✨ Features

### 1. RAG-Based Document Q&A
- **Document Processing:** Multi-format support (PDF, TXT)
- **Chunking Strategy:** CharacterTextSplitter (1000 chars, 200 overlap)
- **Vector Storage:** In-memory ChromaDB with OpenAI embeddings
- **Retrieval:** ConversationalRetrievalChain with conversation memory
- **Memory:** ConversationBufferMemory for context retention

### 2. Conversational Form with Function Calling
- **Function Calling:** OpenAI tools API for structured data extraction
- **Data Collection:** Name, email, phone via natural conversation
- **Validation:** LLM-driven input validation and missing field detection
- **Storage:** JSON file system (`submissions/submission_{name}.json`)
- **Smart Prompting:** Context-aware follow-ups for incomplete data

## 🚀 Quick Start

### Prerequisites
```bash
Python 3.8+
OpenAI API Key
```

### Installation
```bash
git clone https://github.com/oceangiri23/DocQuery-Bot.git
cd DocQuery-Bot
pip install -r requirements.txt
```

### Environment Setup
```bash
# Create .env file
echo "OPENAI_API_KEY=your_api_key_here" > .env
```

### Run Application
```bash
python app.py
```

## 📋 Implementation Details

### Function Calling Schema
```json
{
  "name": "submit_user_form",
  "parameters": {
    "type": "object",
    "properties": {
      "name": {"type": "string"},
      "email": {"type": "string"},
      "phone": {"type": "string"}
    },
    "required": ["name", "email", "phone"]
  }
}
```

### RAG Pipeline
1. **Document Loading** → PyPDFLoader / TextLoader
2. **Text Splitting** → CharacterTextSplitter
3. **Embedding Generation** → OpenAIEmbeddings
4. **Vector Indexing** → ChromaDB
5. **Retrieval** → Similarity search with conversational context
6. **Response Generation** → GPT-4o-mini with retrieved context

### UI Navigation
- **Side-by-side mode selector** with dynamic interface switching
- **State management** via Gradio visibility controls
- **Independent chat histories** for each mode


```

## 🔧 Configuration

**Model Settings:**
- Model: `gpt-4o-mini`
- Chunk Size: 1000 characters
- Chunk Overlap: 200 characters
- Vector DB: ChromaDB (ephemeral)


## ⚙️ Technical Notes

- **Stateless RAG:** Vector store rebuilt per session
- **Two-step Function Calling:** Tool execution → final response generation
- **Async-ready:** Built on Gradio's event system
