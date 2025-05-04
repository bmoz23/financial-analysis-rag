# analysis/rag_service.py

import os
from fastapi import FastAPI, Query, HTTPException
from shared.db import AsyncSession
from sqlalchemy import select
from shared.models import Price
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.agents import initialize_agent, Tool, AgentType
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from dotenv import load_dotenv

app = FastAPI(title="RAG Service with Gemini Agent via LangChain")
load_dotenv()

gemini_key = os.getenv("GEMINI_API_KEY")
if not gemini_key:
    raise RuntimeError("Missing GEMINI_API_KEY in environment")

@app.on_event("startup")
async def startup():
    async with AsyncSession() as session:
        result = await session.execute(
            select(Price).order_by(Price.timestamp.desc()).limit(1000)
        )
        rows = result.scalars().all()

    docs = [
        Document(page_content=(
            f"{r.symbol} at {r.timestamp.isoformat()}: "
            f"open={r.open}, high={r.high}, low={r.low}, "
            f"close={r.close}, volume={r.volume}"
        ))
        for r in rows
    ]

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001", google_api_key=gemini_key
    )
    vectordb = Chroma.from_documents(docs, embeddings, collection_name="price_history")
    retriever = vectordb.as_retriever(search_kwargs={"k": 5})

    gemini_llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash", google_api_key=gemini_key, temperature=0.2
    )

    def retrieve_tool(q: str) -> str:
        docs = retriever.get_relevant_documents(q)
        return "\n".join(d.page_content for d in docs)

    agent = initialize_agent(
        [Tool(name="RetrievePriceHistory", func=retrieve_tool,
              description="Fetch price history snippets")],
        gemini_llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=False
    )
    app.state.agent = agent

@app.get("/query")
async def query(q: str = Query(...)):
    async_client = app.state.agent
    try:
        answer = app.state.agent.invoke({"input": q})
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(502, f"Agent error: {e}")
