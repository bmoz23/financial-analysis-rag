# chat_service/main.py
import base64
from fastapi import FastAPI, Query, HTTPException
import httpx

app = FastAPI(title="Unified Chat Service")

RAG_URL    = "http://analysis:8003/query"
REPORT_URL = "http://report_generator:8004/generate_report"

def wants_report(message: str) -> bool:
    kws = ["report", "generate report", "pdf", "full report"]
    msg = message.lower()
    return any(kw in msg for kw in kws)

@app.get("/chat")
async def chat(q: str = Query(..., description="User message")):
    async with httpx.AsyncClient() as client:
        if wants_report(q):
            # call report generator
            resp = await client.post(REPORT_URL, timeout=60)
            if resp.status_code != 200:
                raise HTTPException(502, f"Report service error: {resp.status_code}")
            pdf_bytes = resp.content
            b64 = base64.b64encode(pdf_bytes).decode("utf-8")
            return {"type": "report", "data": b64}
        else:
            # call RAG Q&A
            resp = await client.get(RAG_URL, params={"q": q}, timeout=10)
            if resp.status_code != 200:
                raise HTTPException(502, f"RAG service error: {resp.status_code}")
            body = resp.json()
            answer = body.get("answer", "No answer.")
            return {"type": "text", "data": answer}
