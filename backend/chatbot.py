# ✅ chatbot.py — Enhanced Chain Loader with DOM/Trace-aware Context

from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.retrievers import BM25Retriever, MultiVectorRetriever
from langchain_google_genai import ChatGoogleGenerativeAI
from dom_context import get_runtime_dom_data
from runtime_tracer import get_runtime_trace_log  # Optional

def load_chain(role="developer", page_url=None, element_descriptor=None, trace_path=None):
    # 🔍 Load Vector Store
    db = FAISS.load_local(
        "vectorstore",
        HuggingFaceEmbeddings(model_name="intfloat/e5-base-v2"),
        allow_dangerous_deserialization=True
    )

    # 🧠 Memory
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    # 📜 Role-specific instruction
    role_instructions = {
        "developer": "Explain code, architecture, and impact of changes.",
        "tester": "Explain features, suggest test cases and edge cases. Use DOM and XPath context if available.",
        "user": "Explain functionality and navigation in simple language."
    }
    instruction = role_instructions.get(role, "You are a helpful assistant.")

    # 🧩 Additional Context (DOM + Runtime)
    additional_context = ""

    if page_url:
        additional_context += "\n\n[DOM CONTEXT]\n" + get_runtime_dom_data(page_url, element_descriptor)

    if trace_path:
        additional_context += "\n\n[TRACE LOG]\n" + get_runtime_trace_log(trace_path)

    # 🧠 Prompt Template
    template = f"""You are an assistant helping a {role}. {instruction}
Chat History:
{{chat_history}}
Context: {{context}}{additional_context}
Question: {{question}}
Answer:"""

    prompt = PromptTemplate(template=template, input_variables=["chat_history", "context", "question"])

    # 🔥 LLM
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)

    # 🔎 Hybrid Retrieval (BM25 + FAISS)
    all_docs = db.similarity_search("", k=100)  # Load a large sample of docs for BM25
    bm25 = BM25Retriever.from_documents(all_docs)
    bm25.k = 4

    retriever = MultiVectorRetriever(retrievers=[db.as_retriever(), bm25])

    # 🤖 Conversational Chain
    return ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        combine_docs_chain_kwargs={"prompt": prompt}
    )
