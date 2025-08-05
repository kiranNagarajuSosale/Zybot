from fastapi import FastAPI, Request
from pydantic import BaseModel
from chatbot import load_chain
from dom_context import get_runtime_dom_data
from runtime_tracer import get_runtime_trace
from fastapi.middleware.cors import CORSMiddleware
import markdown
import re
import html
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

chat_chain = load_chain()  # default is "developer"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5199"], allow_methods=["*"], allow_headers=["*"],# Don't use "*" with allow_credentials=True
    allow_credentials=True
)

def prettify_response(text: str) -> str:
    if not isinstance(text, str):
        raise ValueError("Response to prettify must be a string")
    
    # Handle code blocks manually first
    def replace_code_block(match):
        language = match.group(1) if match.group(1) else ''
        code_content = html.escape(match.group(2))  # Escape HTML entities
        return f'<pre><code class="language-{language}">{code_content}</code></pre>'
    
    # Replace fenced code blocks with HTML
    text = re.sub(r'```(\w+)?\n(.*?)\n?```', replace_code_block, text, flags=re.DOTALL)
    
    # Convert the rest with markdown
    html_result = markdown.markdown(text)
    
    return html_result

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
    pretty_result = prettify_response(result)

    return {"answer": pretty_result, "format": "html"}

@app.get("/")
def serve_index():
    return FileResponse(os.path.join("static", "index.html"))
