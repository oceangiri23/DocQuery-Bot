# Document Query Chatbot with Conversational Form  

This project demonstrates a chatbot capable of answering user queries from any PDF document and handling conversational forms for collecting user details such as **Name**, **Email**, **Phone Number**, and **Appointment Date**.  
The project utilizes the **Gemini** model, **LangChain**, and **ChromaDB**, and is deployed using **Streamlit** for a user-friendly interface.  

---


## Features  

### Chatbot Functionality  
- **Document-Based Query Resolution**:  
   - Processes PDF documents by splitting them into chunks.  
   - Stores and retrieves chunks as embeddings using ChromaDB.  
   - Responds to user queries with contextually accurate answers based on stored embeddings.  

### Conversational Form  
- Collects user information like:  
  - Name  
  - Email  
  - Phone Number  
  - Appointment Date  
- **Validation**:  
   - Ensures that email and phone number inputs are valid.  
   - Converts natural date expressions like "Next Monday" or "Coming Friday" into ISO format (**YYYY-MM-DD**).  
- **Data Management**:  
   - Stores collected data in a structured **JSON** file.  

### Tool-Agent Integration  
- The conversational form integrates seamlessly with tool agents for appointment booking and query handling.  

### Deployment  
- The project is deployed using **Streamlit**, providing a user-friendly interface for interacting with the chatbot and conversational form.  

---

## Installation  

### Prerequisites  
Ensure the following are installed:  
1. **Python 3.8+**  
2. **pip**  
3. **Git**  

### Clone the Repository  
```bash
git clone https://github.com/username/DocumentQueryChatbot.git
cd DocumentQueryChatbot
```
### Install Dependencies
``` pip install -r requirements.txt ```
### Running the Project Locally
``` streamlit run main.py ```

### Example json Output
```[
    {
        "What is your name?": "sagar giri",
        "When would you like to book the appointment?": "2024-11-29"
    },
    {
        "What is your name?": "aman kansakar",
        "When would you like to book the appointment?": "2024-11-29"
    }
] ```
