from dotenv import load_dotenv
import os
import google.generativeai as genai
import chromadb
import chromadb.utils.embedding_functions as embedding_functions
from text_processing import load_pdf, split_txt_to_chunk, find_relevant_context
from prompt import create_prompt


load_dotenv()
api_key = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=api_key)

google_ef = embedding_functions.GoogleGenerativeAiEmbeddingFunction(api_key=api_key)
client = chromadb.PersistentClient(path = "embeddings/gemini")
collection = client.get_or_create_collection(name="pdf_rag", embedding_function=google_ef)
generative_model = genai.GenerativeModel("gemini-1.5-pro-latest")

def generate_answer(prompt):
  result = generative_model.generate_content(prompt)
  return result


def  get_answer(path_to_pdf, question):
  text = load_pdf(path_to_pdf)
  chunks = split_txt_to_chunk(text, max_len=1500, chunk_overlap=200)
  batch_size = 50
  for i in range(0, len(chunks), batch_size):
    batch_chunks = chunks[i:i+batch_size]
    batch_ids = [str(j) for j in range(i, i + len(batch_chunks))]
    collection.add(documents=batch_chunks, ids=batch_ids)

  results = find_relevant_context(question, collection)
  prompt = create_prompt(query=question, context = results)
  answer = generate_answer(prompt)
  return answer.text

answer = get_answer("./datas/word2vec.pdf", "What is the test set mentioned in the paper.")
print("The answer is :", answer, "!!Done")
