import os
import json
from dotenv import load_dotenv
from openai import OpenAI
import gradio as gr

load_dotenv(override=True)
openai_api_key = os.getenv('OPENAI_API_KEY')   
MODEL = "gpt-4o-mini"
openai = OpenAI()

system_message = (
    "You are a helpful conversational form assistant. "
    "Collect user name, email, and phone number. "
    "If some information is missing, ask only about the missing field. "
    "Keep responses short and polite. "
    "When all fields are collected, call the function."
)

def save_form_to_json(form_data):
    os.makedirs("submissions", exist_ok=True)
    filename = f"submissions/submission_{form_data['name']}.json"
    with open(filename, "w") as f:
        json.dump(form_data, f, indent=4)
    return filename

form_function = {
    "name": "submit_user_form",
    "description": "Submit a user form with name, email, and phone. Ask for missing values if not provided.",
    "parameters": {
        "type": "object",
        "properties": {
            "name": { "type": "string", "description": "Full name of the user" },
            "email": { "type": "string", "description": "User email" },
            "phone": { "type": "string", "description": "User phone number" }
        },
        "required": ["name", "email", "phone"],
        "additionalProperties": False
    }
}

tools = [{"type": "function", "function": form_function}]

def handle_tool_call(message):
    tool_call = message.tool_calls[0]
    args = json.loads(tool_call.function.arguments)

    save_form_to_json(args)

    response = {
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": json.dumps({"status": "saved", "data": args})
    }
    return response

def chat(message, history):
    messages = [{"role": "system", "content": system_message}] + history + [
        {"role": "user", "content": message}
    ]
    # FIRST MODEL CALL
    response = openai.chat.completions.create(
        model=MODEL, messages=messages, tools=tools
    )
    # If assistant wants to call function
    if response.choices[0].finish_reason == "tool_calls":
        message = response.choices[0].message
        tool_response = handle_tool_call(message)
        messages.append(message)
        messages.append(tool_response)

        # SECOND MODEL CALL (after tool executes)
        final = openai.chat.completions.create(
            model=MODEL, messages=messages
        )
        return final.choices[0].message.content
    return response.choices[0].message.content

gr.ChatInterface(fn=chat).launch()