#!/bin/bash

# Overwrite README.md with clean, professional documentation
cat << 'EOF' > README.md
# Local Multi-Model MoE Gateway

A production-grade, high-performance implementation of a local **Mixture-of-Experts (MoE)** routing gateway. This project leverages an ultra-fast local supervisor model to analyze user intent dynamically and route queries across a specialized roster of localized LLM experts running on personal hardware via Ollama.

---

## 🏗️ Architecture Overview

The system operates via a split cloud-local hybrid microservices architecture:
1. **Frontend Layer:** Static UI built with Tailwind CSS, globally deployed via Netlify.
2. **Secure Ingress:** Public traffic is safely tunneled to the local host machine using a secure Ngrok network bridge, passing custom security bypass headers.
3. **Routing Gateway:** A lightweight FastAPI backend serves as the Orchestration Layer.
4. **Execution Layer (The Brains):** Local LLMs process queries natively using host hardware (NVIDIA RTX 4060 GPU / 24GB RAM).

---

## 🔀 Router Roster Matrix

The Orchestration Layer utilizes `llama3.2:latest` as an intelligent dispatcher to sort user intent into specific domains and allocate the most qualified expert:

| Category | Targeted Domain | Active Expert Model | Model Footprint |
| :--- | :--- | :--- | :--- |
| **`linux`** | Bash scripts, terminal ops, OS internals | `linuxpal:latest` | ~4.9 GB |
| **`code`** | Complex programming, logic, debugging | `deepseek-coder-v2:16b` | ~8.9 GB |
| **`complex`**| Deep logic, multi-step reasoning, essays | `llama3.1:8b` | ~4.9 GB |
| **`casual`** | Contextual greetings, fast chat matrix | `shadow-ai:latest` | ~2.0 GB |

---

## 🛠️ Stack Components

* **Backend:** Python 3.12, FastAPI, Uvicorn (Asynchronous Server Gateway Interface)
* **LLM Engine:** Ollama (Local Orchestration)
* **Frontend:** Vanilla JavaScript, Tailwind CSS Engine, Netlify Hosting
* **Networking:** Ngrok (Reverse proxy secure endpoint tunnel)

---

## 🚀 Local Deployment Lifecycle

### 1. Initialize the Environment
Activate the isolated Python virtual sandbox:
```bash
source venv/bin/activate
```

### 2. Boot up Orchestration Layer
Fire up the local ASGI web server to start listening for requests:
```bash
uvicorn server:app --reload
```

### 3. Expose the Ingress Endpoint
Establish the secure tunnel connection on an alternative terminal instance:
```bash
ngrok http 8000
```
*(Ensure the forwarding address is mirrored in your client-side fetch script before staging).*
EOF

echo "✓ README.md has been successfully written!"

# Run git operations locally
git add README.md
git commit -m "docs: complete overhaul of README via automated shell script"

echo "✓ Changes committed locally!"
echo "Now run your git push command to upload it to GitHub."
