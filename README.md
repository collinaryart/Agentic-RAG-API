## Live Demo Notes
- Hosted on Render free tier: Vector DB resets after ~15 min inactivity or redeploy.
- To test:
  1. POST to `/ingest` with sample texts (example below).
  2. Then query via `/rag-query` or `/agent-run`.

Example /ingest payload:
```json
{
  "texts": [
    "Arcadian Digital builds AI automations for Australian companies.",
    "LangChain enables RAG and agentic workflows with tools.",
    "OpenAI embeddings power vector search in Chroma."
  ]
}
``json
Example /rag-query payload:
```json
{
  "question": "What does Arcadian Digital do?"
}
``json
Example /agent-run payload (tests agent's context retrieval, as well as calculator functionality):
'''json
{
  "question": "What is 15 * 8 plus the number of texts I ingested earlier?"
}
``json

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
