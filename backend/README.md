# JARVIS Backend

The backend is the core execution engine of the JARVIS AI Operating System.

It provides the APIs, orchestration layer, memory management, and AI model integration that power the rest of the system.

## Responsibilities

* FastAPI server
* Hermes orchestration kernel
* GLM 5.1 integration
* Prompt management
* Conversation memory
* Obsidian vault integration (planned)
* Tool execution framework (planned)
* Voice service integration (planned)

## Directory Structure

```text
backend/
├── app/
│   ├── agents/
│   ├── api/
│   ├── config/
│   ├── core/
│   ├── llm/
│   ├── memory/
│   ├── tools/
│   ├── voice/
│   └── utils/
├── tests/
├── main.py
└── ARCHITECTURE.md
```

## Running the Backend

Create and activate the virtual environment:

```bash
uv venv
source .venv/bin/activate
```

Install dependencies:

```bash
uv pip install -r requirements.txt
```

Start the development server:

```bash
uvicorn main:app --reload
```

## API

The backend exposes REST endpoints for interacting with JARVIS.

Current endpoint:

* `POST /chat`

## Architecture

See `ARCHITECTURE.md` for the complete system design and roadmap.

