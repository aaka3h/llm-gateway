# Local LLM Gateway

A small FastAPI application that uses an Ollama supervisor model to classify a prompt, sends it to one selected model, and returns the answer. A static HTML chat interface displays the response and the model that handled it.

This is a development prototype for routing between separate models. It does not train or combine a neural mixture-of-experts model.

## How it works

1. The browser sends a prompt to `POST /chat`.
2. `llama3.2:latest` classifies the prompt.
3. The backend selects a model from the roster below and sends it the original prompt.
4. The API returns `model_used` and `response`.

The supervisor and selected model are called sequentially. If classification fails or no category matches, the router falls back to `casual`.

| Category | Intended use | Model configured in server.py |
| --- | --- | --- |
| `linux` | Linux, shell commands, operating systems | `linuxpal:latest` |
| `code` | Programming and debugging | `deepseek-coder-v2:16b` |
| `complex` | Essays and complex reasoning | `llama3.1:8b` |
| `casual` | Greetings, quick facts, casual conversation | `shadow-ai:latest` |

## Set up the backend

You need Python 3 with `venv` and `pip`, plus a running Ollama service and models that fit your hardware.

```bash
git clone https://github.com/aaka3h/llm-gateway.git
cd llm-gateway
python -m venv .venv
```

Activate the environment on macOS/Linux:

```bash
source .venv/bin/activate
```

Or in Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the backend's dependencies:

```bash
python -m pip install fastapi uvicorn pydantic ollama
```

The current [requirements.txt](requirements.txt) lists Gradio and Requests; it does not include the full runtime dependencies imported by [server.py](server.py). Installing that file alone is insufficient for this backend.

Ensure Ollama is running, then check the models available locally:

```bash
ollama list
```

Every configured model name must resolve in your Ollama installation. The repository does not include model weights or definitions for `linuxpal:latest` and `shadow-ai:latest`. Provide those models yourself, or edit `model_roster` in [server.py](server.py) to use names from `ollama list`. Also make sure the supervisor name in `classify_intent` matches an available model.

Start the API from the repository directory:

```bash
python -m uvicorn server:app --reload --host 127.0.0.1 --port 8000
```

Open [the API documentation](http://127.0.0.1:8000/docs) to try `POST /chat`. Model downloads and inference speed depend on the models and hardware you choose.

## Connect the browser interface

The backend does not serve `index.html`. In [index.html](index.html), replace the existing hard-coded Ngrok URL in `fetch(...)` with your local API endpoint:

```javascript
const response = await fetch('http://127.0.0.1:8000/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt: text })
});
```

In another terminal, serve the frontend from the repository directory:

```bash
python -m http.server 5500 --bind 127.0.0.1
```

Open [the chat interface](http://127.0.0.1:5500). Its Tailwind styling is loaded from a CDN, so that part of the page requires internet access.

## API

Request:

```http
POST /chat
Content-Type: application/json
```

```json
{
  "prompt": "How do I list files in Linux?"
}
```

Response shape, with the actual values determined at runtime:

```json
{
  "model_used": "selected-model-name",
  "response": "Generated answer"
}
```

An empty prompt returns HTTP 400. Failure to generate an answer from the selected model returns HTTP 500. Requests contain only one prompt; conversation history and response streaming are not implemented.

## Optional remote access

A separately hosted frontend can call the backend through a tunnel, but no Netlify deployment configuration is included. The existing Ngrok URL in the HTML must be replaced with your own endpoint.

The current application has no authentication or rate limiting and allows all CORS origins. A tunnel and the `ngrok-skip-browser-warning` header do not add access control. Treat the current setup as a local development demo; public deployment needs additional controls.

## Repository files

| File | Purpose |
| --- | --- |
| [server.py](server.py) | FastAPI endpoint, supervisor classification, and model roster |
| [index.html](index.html) | Static chat interface |
| [requirements.txt](requirements.txt) | Existing dependency list; see the backend setup above |
| [.github/workflows/python-package.yml](.github/workflows/python-package.yml) | Python lint/test workflow |

The repository currently has no automated test files. The workflow invokes `pytest`, but it does not establish end-to-end model routing coverage. The legacy `update_readme.sh` overwrites this README with an older description; it is not needed to run the application.
