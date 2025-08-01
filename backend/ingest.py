import os
from dotenv import load_dotenv
from langchain_community.document_loaders import (
    DirectoryLoader,
    PythonLoader,
    TextLoader,
    JSONLoader,
    UnstructuredHTMLLoader
)
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings

# Load environment variables
load_dotenv()

VECTOR_STORE_DIR = "vectorstore"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150

# Supported file extensions and their loaders
EXTENSION_LOADERS = {
    ".py": PythonLoader,
    ".js": TextLoader,
    ".ts": TextLoader,
    ".cs": TextLoader,
    ".cshtml": TextLoader,
    ".html": UnstructuredHTMLLoader,
    ".txt": TextLoader,
    ".json": JSONLoader,
    ".md": TextLoader
}

def load_documents(repo_path: str):
    documents = []
    for ext, loader_cls in EXTENSION_LOADERS.items():
        loader = DirectoryLoader(
            repo_path,
            glob=f"**/*{ext}",
            loader_cls=loader_cls,
            recursive=True,
            silent_errors=True,
            exclude=["**/node_modules/**", "**/lib/**", "**/dist/**", "**/.git/**"]
        )
        docs = loader.load()
        documents.extend(docs)
        print(f"✅ Loaded {len(docs)} {ext} files")
    return documents

def embed_and_save(documents):
    splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    chunks = splitter.split_documents(documents)

    # Use HuggingFaceEmbeddings with INSTRUCTOR model
    embeddings = HuggingFaceEmbeddings(
        model_name="jinaai/jina-embeddings-v2-base-code"
    )

    db = FAISS.from_documents(chunks, embeddings)
    db.save_local(VECTOR_STORE_DIR)
    print(f"✅ Vector DB saved to `{VECTOR_STORE_DIR}` with {len(chunks)} chunks.")

def ingest_repo(repo_path: str):
    print(f"📂 Ingesting from: {repo_path}")
    documents = load_documents(repo_path)
    if not documents:
        print("❌ No documents found. Check file types or path.")
        return
    embed_and_save(documents)

# Entry point
if __name__ == "__main__":
    repo_path = r"C:\Users\adara\source\repos\KOProject\PasswordManagerApplication"
    ingest_repo(repo_path)
