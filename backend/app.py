from fastapi import FastAPI, Request
from pydantic import BaseModel
from chatbot import load_chain
from dom_context import get_runtime_dom_data
from runtime_tracer import get_runtime_trace
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
chat_chain = load_chain()  # default is "developer"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

class Query(BaseModel):
    question: str
    role: str
    dom_context: str = ""
    trace_context: str = ""
    model: str = "gemini-1.5-flash"

@app.post("/chat")
async def chat(query: Query):
    chain = load_chain(role=query.role, geminiModel=query.model)

    # Inject extra context
    runtime_context = f"{query.dom_context}\n\n{query.trace_context}"
    final_input = f"{query.question}\n\nRuntime Context:\n{runtime_context}"

    result = chain.run(final_input)
    return {"answer": result}
