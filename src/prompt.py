

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

def create_prompt_for_form(questions, answers):
    prompt = f"""Imagine you are engaging in a friendly, natural conversation with a user. 
    Your task is to ask the user questions based on a set of predefined questions and the responses they have already provided.

    Current Question: {questions}
    Previous Questions and Answers: {answers}

    Provide an interesting and conversational format for the next question based on this information."""
    
    return prompt
