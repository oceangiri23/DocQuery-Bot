import fitz

#for link to directry
def load_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text("text")  
        text += "\n\n" 
    return text

# for object based file
def load_pdfs(uploaded_file):
    """Loads and extracts text from a PDF uploaded via Streamlit."""
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    
    text = ""
    for page in doc:
        text += page.get_text("text")
        text += "\n\n" 
    
    return text

def split_txt_to_chunk(text, max_len = 1500, chunk_overlap=200):
  chunks = []
  start = 0
  text_length = len(text)
  while start<text_length:
    end = start + max_len
    if end<text_length:
      end = text.rfind(" ", start, end) + 1

      if end <=start:
        end=start+max_len
    chunk = text[start:end].strip()

    if chunk:
      chunks.append(chunk)
    start = end - chunk_overlap
    if start >= text_length:
      break
  return chunks

def build_escaped_context(context):
    escaped_context = ""
    for item in context:
        if item.strip():  
            escaped_context += item.strip() + "\n\n"
    return escaped_context.strip() 

def find_relevant_context(query, db, n_results=3):
    results = db.query(query_texts=[query], n_results=n_results)
    
    if not results["documents"]:
        return "No relevant context found."
    
    relevant_documents = results["documents"]
    if len(relevant_documents) == 1:
        return build_escaped_context(relevant_documents[0])
    else:
        
        combined_context = "\n".join([doc.strip() for doc in relevant_documents[:n_results]])
        return build_escaped_context(combined_context.split("\n"))