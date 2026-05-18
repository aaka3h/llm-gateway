import os
import subprocess
import time
import sys
import requests
import json
import gradio as gr

def check_dependencies():
    """Ensure Ollama is installed before starting."""
    if subprocess.call(["which", "ollama"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) != 0:
        print("ERROR: Ollama is not installed on this system.")
        print("Please install it first using: curl -fsSL https://ollama.com/install.sh | sh")
        sys.exit(1)

def start_ollama():
    """Boot up the Ollama background service."""
    print("Starting Ollama background service...")
    # Inherit system environment variables (important for GPU pathways)
    env = os.environ.copy()
    subprocess.Popen(["ollama", "serve"], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(5) 

def pull_required_models():
    """Ensure the A-Team models are downloaded."""
    models = ["llama3.2:1b", "llama3.2", "qwen2.5-coder:7b"]
    for model in models:
        print(f"Checking/Downloading {model}...")
        subprocess.run(["ollama", "pull", model], stdout=subprocess.DEVNULL)
    print("All models verified and loaded!")

def determine_best_model(prompt):
    """Level 2 Supervisor AI Router logic."""
    system_instruction = """
    You are an intelligent routing AI. Read the user's prompt. 
    If the prompt asks for programming, coding, scripts, debugging, or web development, output exactly the word: CODE
    If it is a general question, output exactly the word: CHAT
    Do not output any other words or punctuation.
    """
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.2:1b",
                "prompt": prompt,
                "system": system_instruction,
                "stream": False
            },
            timeout=10
        )
        supervisor_decision = response.json().get("response", "").strip().upper()
    except Exception:
        # Fallback to generalist if supervisor API fails
        return "llama3.2"
    
    if "CODE" in supervisor_decision:
        return "qwen2.5-coder:7b"
    return "llama3.2"

def chat_with_ollama(message, history):
    target_model = determine_best_model(message)
    
    messages = []
    for user_msg, bot_msg in history:
        messages.append({"role": "user", "content": user_msg})
        messages.append({"role": "assistant", "content": bot_msg})
    messages.append({"role": "user", "content": message})
    
    yield f"*(Supervisor routed to **{target_model}**)*\n\n"
    
    try:
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={"model": target_model, "messages": messages, "stream": True},
            stream=True
        )
        
        partial_message = f"*(Supervisor routed to **{target_model}**)*\n\n"
        for line in response.iter_lines():
            if line:
                data = json.loads(line)
                partial_message += data["message"]["content"]
                yield partial_message
    except Exception as e:
        yield f"An error occurred while communicating with the engine: {str(e)}"

if __name__ == "__main__":
    check_dependencies()
    start_ollama()
    pull_required_models()
    
    print("Launching Gradio public interface...")
    # share=True creates a temporary public share link automatically
    gr.ChatInterface(chat_with_ollama, title="Level 2 AI: Intelligent Supervisor Router").launch(share=True)
