

def create_prompt(query, context):
    prompt = f"""
    You are a knowledgeable assistant answering questions based strictly on the provided context.
    Do not make assumptions or include information not present in the context.
    If the context is insufficient to answer the question, respond with: "The context does not contain enough information to answer this question."
    
    Context:
    {context}
    
    Question:
    {query}
    
    Answer:
    """
    return prompt
