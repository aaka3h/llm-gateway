import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import ollama

# 1. Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 2. Initialize the API
app = FastAPI(title="Advanced Local MoE Gateway")

# 3. Configure CORS (Crucial for your Netlify frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Define the Data Structure
class UserInput(BaseModel):
    prompt: str

# 5. The Advanced Supervisor Logic
def classify_intent(prompt: str) -> str:
    """Uses a fast model to classify the prompt into multiple specific domains."""
    
    supervisor_prompt = f"""
    You are an intelligent router. Analyze the user's prompt and classify it into EXACTLY ONE of these categories:
    
    1. 'linux' - For questions about Linux, bash commands, terminal, or operating systems.
    2. 'code' - For programming, scripts, debugging, or web development.
    3. 'complex' - For deep logic, long essays, or complex reasoning.
    4. 'casual' - For simple greetings, quick facts, or casual conversation.
    
    Respond ONLY with the single category word. Do not explain yourself.
    
    User Prompt: "{prompt}"
    """
    
    try:
        # Using llama3.2 as the ultra-fast dispatcher
        response = ollama.chat(model='llama3.2:latest', messages=[
            {'role': 'user', 'content': supervisor_prompt}
        ])
        
        category = response['message']['content'].strip().lower()
        
        # Clean up the response to ensure it matches our exact routing keys
        valid_categories = ["linux", "code", "complex", "casual"]
        for valid in valid_categories:
            if valid in category:
                return valid
                
        return "casual" # Safe fallback if the model gets confused
        
    except Exception as e:
        logging.error(f"Supervisor classification failed: {e}")
        return "casual"

# 6. The Main Chat Endpoint
@app.post("/chat")
async def chat_endpoint(user_input: UserInput):
    """Receives prompt, routes to the best expert, and returns the answer."""
    prompt = user_input.prompt
    
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")

    # Step A: Classify the intent secretly in the background
    category = classify_intent(prompt)
    logging.info(f"Supervisor classified prompt as: '{category}'")

    # Step B: Map the category to your specific installed models
    model_roster = {
        "linux": "linuxpal:latest",
        "code": "deepseek-coder-v2:16b", 
        "complex": "llama3.1:8b",        
        "casual": "shadow-ai:latest"     
    }

    # Grab the right model, defaulting to shadow-ai if something goes wrong
    specialist_model = model_roster.get(category, "shadow-ai:latest")

    logging.info(f"Routing to specialist model: {specialist_model}...")

    # Step C: Generate the final answer using the chosen expert
    try:
        response = ollama.chat(model=specialist_model, messages=[
            {'role': 'user', 'content': prompt}
        ])
        
        answer = response['message']['content']
        
        # Send both the answer and the exact model name back to the frontend
        return {
            "model_used": specialist_model,
            "response": answer
        }
        
    except Exception as e:
        logging.error(f"Specialist model failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate response from the LLM.")
