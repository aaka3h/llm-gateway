# llm-router

A simple, lightweight implementation of an intelligent Mixture-of-Experts (MoE) gateway. Instead of relying on hardcoded keyword matching, this project uses an ultra-fast local LLM to analyze user intent and route prompts to the most qualified specialist model.

## Architecture



1. **User Input:** A prompt is received via a public-facing web interface.
2. **Intent Classification:** The prompt is secretly analyzed by a fast 1B parameter "Supervisor" model.
3. **Dynamic Routing:** The supervisor outputs a classification tag, forwarding the actual prompt to the appropriate specialist model (e.g., general chat vs. dedicated code generation).

## Technology Stack

* **Inference Engine:** [Ollama](https://ollama.com/) (Managing local model execution and GPU acceleration)
* **Supervisor Model:** `llama3.2:1b` (Used for low-latency classification)
* **Specialist Models:** `llama3.2` (General text/chat) & `qwen2.5-coder:7b` (Code generation/debugging)
* **User Interface:** [Gradio](https://www.gradio.app/) (Providing a clean, accessible chat window)
