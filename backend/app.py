from typing import Optional, Dict, Any
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
    allow_origins=["http://localhost:5199", "http://localhost:4200", "*"], 
    allow_methods=["*"], 
    allow_headers=["*"],
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

class Dimensions(BaseModel):
    width: Optional[float] = None
    height: Optional[float] = None
    top: Optional[float] = None
    left: Optional[float] = None

class DomContextData(BaseModel):
    innerText: Optional[str] = None
    innerHTML: Optional[str] = None
    tagName: Optional[str] = None
    id: Optional[str] = None
    className: Optional[str] = None
    attributes: Optional[Dict[str, str]] = None
    computedStyles: Optional[Dict[str, str]] = None
    xpath: Optional[str] = None
    dimensions: Optional[Dimensions] = None

class Query(BaseModel):
    question: str
    role: str
    dom_context: Optional[DomContextData] = None
    trace_context: str = ""
    model: str = "gemini-1.5-flash"
    domContextEnabled: bool = False

@app.post("/chat")
async def chat(query: Query):
    chain = load_chain(role=query.role, geminiModel=query.model)

    # Process DOM context data if available
    dom_context_str = ""
    if query.dom_context:
        dom_context_str = format_dom_context(query.dom_context)
    
    # Inject extra context
    runtime_context = f"{dom_context_str}\n\n{query.trace_context}"
    final_input = f"{query.question}\n\nRuntime Context:\n{runtime_context}"

    result = chain.run(final_input)
    pretty_result = prettify_response(result)

    return {"answer": pretty_result, "format": "html"}

def format_dom_context(dom_data: DomContextData) -> str:
    """Format DOM context data into a readable string format for the LLM."""
    if not dom_data:
        return ""
    
    context_parts = [
        f"Selected Element Information:",
        f"• Content: {dom_data.innerText[:500] if dom_data.innerText else 'N/A'}",
        f"• Tag: {dom_data.tagName or 'N/A'}",
    ]
    
    if dom_data.id:
        context_parts.append(f"• ID: {dom_data.id}")
    
    if dom_data.className:
        context_parts.append(f"• Class: {dom_data.className}")
    
    if dom_data.xpath:
        context_parts.append(f"• XPath: {dom_data.xpath}")
    
    if dom_data.attributes:
        attr_str = ", ".join([f"{k}='{v}'" for k, v in dom_data.attributes.items() if k not in ['id', 'class']][:5])
        if attr_str:
            context_parts.append(f"• Attributes: {attr_str}")
    
    if dom_data.dimensions:
        dim = dom_data.dimensions
        dim_str = []
        if dim.width is not None:
            dim_str.append(f"W={dim.width}px")
        if dim.height is not None:
            dim_str.append(f"H={dim.height}px")
        if dim_str:
            context_parts.append(f"• Dimensions: {', '.join(dim_str)}")
    
    return "\n".join(context_parts)

@app.get("/")
def serve_index():
    return FileResponse(os.path.join("static", "index.html"))
