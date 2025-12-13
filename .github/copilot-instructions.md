# Copilot Project Instructions

## Project Overview

The app leverages LLMs and Retrieval Augmented Generation (RAG) to let users summarize and chat (Q&A style) with YouTube videos. It's can be run locally using Docker.

## Tech Stack
- Languages: Python
- Frameworks / libraries: Streamlit, LangChain, YouTube Transcript API, peewee
- Databases: ChromaDB (vector store)

## Architecture & Structure
- High-level architecture: The app consists of three main components: Summary, Chat and Library. Summary generates summaries of YouTube videos, Chat leverages RAG to answer user questions based on video content, and Library manages saved summaries and answers from Q&A sessions.
- Key directories and responsibilities:
  - `modules/`: contains classes and functions used throughout the application
  - `pages/`: contains different Streamlit pages (summary, chat, library) for the app, which define the UI and application logic
  - `prompts/`: contains system & user prompts for LLMs
- Important design patterns or constraints: follow **SOLID principles**

## Coding Standards
- Style guide / formatter: Black
- Naming conventions: snake_case for variables and functions, PascalCase for classes

## Testing
- Test framework(s): pytest
- Where tests live: `tests/` directory

## Output Expectations
- Code should be: simple, readable and maintainable
- Commit message conventions: follow conventional commits
- Documentation expectations: provide google-style docstrings for all classes and functions
