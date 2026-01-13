# AGENTS.md

## Purpose

This repository is a Streamlit app that uses LLMs and RAG to summarize and chat with
YouTube videos, plus a Library page to save outputs.

## How to Navigate

Main entrypoint is `main.py`. Streamlit pages live in `pages/`. Shared logic is in
`modules/`. Prompts are in `prompts/`. Tests are in `tests/`.

## Repository Structure

```bash
.
├── main.py                  # Streamlit entrypoint and app shell
├── pages/                   # Streamlit pages (summary, chat, library)
│   ├── chat.py              # RAG-based Q&A UI flow
│   ├── library.py           # Saved summaries/answers UI
│   └── summary.py           # Summary UI flow
├── modules/                 # Core logic (summarization, RAG, persistence, UI helpers)
│   ├── helpers.py           # Shared helpers (config, tokens, providers)
│   ├── persistance.py       # SQLite models and library CRUD
│   ├── rag.py               # Chunking, embeddings, and RAG response
│   ├── summary.py           # Summary prompt + model invocation
│   ├── transcription.py     # Whisper-based transcription
│   ├── ui.py                # Streamlit UI helpers/settings
│   └── youtube.py           # YouTube metadata and transcript retrieval
├── prompts/                 # LLM system/user prompt templates
├── tests/                   # pytest suites
├── data/                    # Local SQLite database and saved outputs
├── config.json              # Default models and UI/config settings
├── docker-compose.yml       # ChromaDB + app services for local Docker setup
├── requirements.txt         # Python dependencies
```

## Key Flows

- Summary: `pages/summary.py` -> `modules/summary.py` -> prompt files in `prompts/`.
- Chat (RAG): `pages/chat.py` -> `modules/rag.py` -> ChromaDB.
- Library: `pages/library.py` -> `modules/persistance.py` (SQLite).

## Coding Standards

- Follow SOLID principles.
- Format with Black.
- Use snake_case for variables/functions, PascalCase for classes.
- Provide Google-style docstrings for all classes and functions.

## Testing

- Use pytest; tests are in `tests/`.

## Run (local)

- `python -m venv .venv` and `pip install -r requirements.txt`
- `docker-compose up -d chromadb`
- `streamlit run main.py`
