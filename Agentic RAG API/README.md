# RAG Agent API

Production-ready FastAPI service demonstrating:
- Document ingestion into persistent Chroma vector DB (OpenAI embeddings)
- Simple RAG Q&A endpoint
- Agentic workflow (LangChain tool-calling agent with retriever + calculator tool)

Perfect for automation platforms, internal tools, or client-facing AI features.

## Setup
1. `python -m venv venv && source venv/bin/activate`
2. `pip install -r requirements.txt`
3. Create `.env` with your `OPENAI_API_KEY`
4. Run: `uvicorn main:app --reload`

## Usage
- POST `/ingest` → add texts (e.g., `{"texts": ["Your document chunk 1", "Chunk 2"]}`)
- POST `/rag-query` → `{"question": "Your question"}`
- POST `/agent-run` → same, but agent can use tools (retrieval + calc)

Swagger UI at `/docs`.

## Deployment
- Free on Render/Railway (bind persistent volume for `db/` folder).
- Add Dockerfile for containerization if needed.

Built to showcase FastAPI + LangChain RAG/agent skills.