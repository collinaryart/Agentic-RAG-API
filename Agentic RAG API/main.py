from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os

from dotenv import load_dotenv

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools import tool
from langchain.tools.retriever import create_retriever_tool

load_dotenv()

# Config
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not set in .env")

embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, openai_api_key=OPENAI_API_KEY)

# Persistent Chroma DB
DB_PATH = "db"
vectorstore = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

retriever_tool = create_retriever_tool(
    retriever,
    "search_docs",
    "Search the ingested documents for relevant context.",
)

app = FastAPI(
    title="RAG Agent API",
    description="Production-ready FastAPI service for RAG queries and agentic workflows (Chroma + LangChain + OpenAI)",
    version="1.0.0",
)


# Request models
class IngestRequest(BaseModel):
    texts: List[str]
    metadata: Optional[List[dict]] = None


class QueryRequest(BaseModel):
    question: str


# Bonus tool: simple calculator for agentic automation demo
@tool
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression (e.g., '2 + 3 * 4')."""
    try:
        return str(eval(expression, {"__builtins__": {}}))
    except Exception:
        return "Invalid expression"


tools = [retriever_tool, calculator]

# Agent setup
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful AI agent. Use tools when needed. Answer based on retrieved context if relevant.",
        ),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)


@app.post("/ingest")
async def ingest_documents(request: IngestRequest):
    if not request.texts:
        raise HTTPException(status_code=400, detail="No texts provided")

    docs = [
        Document(page_content=text, metadata=meta or {})
        for text, meta in zip(
            request.texts, request.metadata or [{} for _ in request.texts]
        )
    ]

    vectorstore.add_documents(docs)
    vectorstore.persist()
    return {"status": "success", "ingested": len(docs)}


@app.post("/rag-query")
async def rag_query(request: QueryRequest):
    if vectorstore._collection.count() == 0:
        raise HTTPException(
            status_code=400, detail="Vector DB empty — ingest documents first"
        )

    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | ChatPromptTemplate.from_template(
            "Answer based on context:\n{context}\n\nQuestion: {question}"
        )
        | llm
        | StrOutputParser()
    )
    response = chain.invoke(request.question)
    return {"answer": response}


@app.post("/agent-run")
async def agent_run(request: QueryRequest):
    if vectorstore._collection.count() == 0:
        raise HTTPException(
            status_code=400, detail="Vector DB empty for retrieval tool"
        )

    response = agent_executor.invoke({"input": request.question, "chat_history": []})
    return {"answer": response["output"]}


@app.get("/")
async def root():
    return {"message": "RAG Agent API running. Use /docs for Swagger UI."}