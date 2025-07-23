fastapi

# ✅ Advanced Chatbot Backend with Evaluation, Debug, Multi-repo, and Active Learning Support

from fastapi import FastAPI, Request, UploadFile, File
from pydantic import BaseModel
from chatbot import load_chain, ingest_repo_from_zip, learn_from_test_failures
from dom_context import get_runtime_dom_data
from runtime_tracer import get_runtime_trace
from fastapi.middleware.cors import CORSMiddleware
from typing import Literal, List, Dict
import json

app = FastAPI(title="LLM QA Chatbot", description="LangChain + Gemini Hybrid Retrieval Bot with Eval, Debug, Multi-repo, Active Learning", version="1.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

class Query(BaseModel):
    question: str
    role: Literal["developer", "tester", "user"]
    dom_context: str = ""
    trace_context: str = ""

@app.post("/chat")
async def chat(query: Query):
    chain = load_chain(role=query.role)
    runtime_context = f"{query.dom_context}\n\n{query.trace_context}"
    final_input = f"{query.question}\n\nRuntime Context:\n{runtime_context}"
    result = chain.run(final_input)
    return {"answer": result}

# ✅ Predefined test cases for evaluation
TEST_QUERIES = [
    {"role": "developer", "question": "What does the login function do?", "expected": "Handles user authentication or login"},
    {"role": "tester", "question": "Give test cases for user registration.", "expected": "Positive, negative, edge test cases for registration"},
    {"role": "user", "question": "How do I reset my password?", "expected": "Steps for password reset"}
]

@app.get("/test-eval")
async def test_eval():
    results = []
    for case in TEST_QUERIES:
        chain = load_chain(role=case["role"])
        response = chain.run(case["question"])
        score = "✔️" if case["expected"].lower() in response.lower() else "❌"
        results.append({
            "role": case["role"],
            "question": case["question"],
            "expected_contains": case["expected"],
            "answer": response,
            "score": score
        })
    return {"results": results}

# ✅ Upload .json file for large-scale eval
@app.post("/test-eval/upload")
async def test_eval_upload(file: UploadFile = File(...)):
    content = await file.read()
    test_cases = json.loads(content.decode("utf-8"))
    results = []
    for case in test_cases:
        chain = load_chain(role=case["role"])
        response = chain.run(case["question"])
        score = "✔️" if case["expected"].lower() in response.lower() else "❌"
        results.append({
            "role": case["role"],
            "question": case["question"],
            "expected_contains": case["expected"],
            "answer": response,
            "score": score
        })
    return {"results": results}

# ✅ Debug route - returns sources, scores, chunks
@app.post("/chat-debug")
async def chat_debug(query: Query):
    chain = load_chain(role=query.role)
    runtime_context = f"{query.dom_context}\n\n{query.trace_context}"
    final_input = f"{query.question}\n\nRuntime Context:\n{runtime_context}"

    result = chain.invoke({"question": query.question, "context": runtime_context})
    retriever = chain.retriever
    docs = retriever.get_relevant_documents(final_input)

    return {
        "answer": result,
        "sources": [d.metadata.get("source", "") for d in docs],
        "scores": [d.metadata.get("score", 0) for d in docs],
        "chunks": [d.page_content for d in docs]
    }

# ✅ Ingest zipped codebase and build new vector index
@app.post("/ingest-zip")
async def ingest_zip(file: UploadFile = File(...)):
    zip_data = await file.read()
    success, message = ingest_repo_from_zip(zip_data)
    return {"status": "success" if success else "error", "message": message}

# ✅ Learn from test evaluation failures
@app.post("/learn-from-failures")
async def learn_from_failures(file: UploadFile = File(...)):
    json_data = await file.read()
    feedback = json.loads(json_data.decode("utf-8"))
    learn_from_test_failures(feedback)
    return {"status": "success", "message": "Feedback ingested for learning."}


from ingest import ingest_github_repo

@app.get("/get-dom-context")
async def get_dom_context(url: str, element_descriptor: str = ""):
    return {"dom": get_runtime_dom_data(url, element_descriptor)}

@app.get("/trace-runtime")
async def trace_runtime(log_path: str = "runtime_logs/trace.json"):
    return {"trace": get_runtime_trace(log_path)}

@app.get("/ingest-github")
async def ingest_github(raw_url: str):
    try:
        ingest_github_repo(raw_url)
        return {"status": "success", "message": f"Ingested GitHub repo: {raw_url}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
