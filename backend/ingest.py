import os
from functools import partial
from dotenv import load_dotenv

from langchain_community.document_loaders import (
    DirectoryLoader,
    PythonLoader,
    TextLoader,
    JSONLoader,
    UnstructuredHTMLLoader
)
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Load environment variables
load_dotenv()

# Configuration
VECTOR_STORE_DIR = "vectorstore"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150

# Supported file types and their loaders
SUPPORTED_EXTENSIONS = {
    ".py": PythonLoader,
    ".js": partial(TextLoader, encoding="utf-8"),
    ".ts": partial(TextLoader, encoding="utf-8"),
    ".cs": partial(TextLoader, encoding="utf-8"),
    ".cshtml": partial(TextLoader, encoding="utf-8"),
    ".html": UnstructuredHTMLLoader,
    ".txt": partial(TextLoader, encoding="utf-8"),
    ".json": JSONLoader,
    ".md": partial(TextLoader, encoding="utf-8"),
    ".xml": partial(TextLoader, encoding="utf-8"),
    ".sql": partial(TextLoader, encoding="utf-8")
}

def load_documents(repo_path: str):
    all_docs = []
    total_files = 0

    for ext, loader_cls in SUPPORTED_EXTENSIONS.items():
        try:
            loader = DirectoryLoader(
                repo_path,
                glob=f"**/*{ext}",
                loader_cls=loader_cls,
                recursive=True,
                silent_errors=True,
                exclude=["**/node_modules/**", "**/lib/**", "**/dist/**", "**/.git/**"]
            )
            docs = loader.load()
            if docs:
                print(f"✅ {ext}: {len(docs)} files loaded")
                all_docs.extend(docs)
                total_files += len(docs)
            else:
                print(f"⚠️  {ext}: no files found")
        except Exception as e:
            print(f"❌ Error loading {ext} files: {e}")

    print(f"📄 Total documents loaded: {total_files}")
    return all_docs

def embed_and_save(documents):
    splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    chunks = splitter.split_documents(documents)
    print(f"🧩 Split into {len(chunks)} chunks")

    print("🧠 Generating embeddings using JinaAI model...")
    embeddings = HuggingFaceEmbeddings(model_name="jinaai/jina-embeddings-v2-base-code")

    db = FAISS.from_documents(chunks, embeddings)
    db.save_local(VECTOR_STORE_DIR)
    print(f"✅ Vector store saved to: `{VECTOR_STORE_DIR}`")

def ingest_repo(repo_path: str):
    if not os.path.exists(repo_path):
        raise FileNotFoundError(f"❌ Provided repo path does not exist: {repo_path}")

    print(f"📂 Scanning directory: {repo_path}")
    documents = load_documents(repo_path)

    if not documents:
        print("🚫 No supported files found in the repo. Nothing to ingest.")
        return

    embed_and_save(documents)

# Run if main
if __name__ == "__main__":
    repo_path = r"C:\Users\adara\source\repos\KOProject\PasswordManagerApplication"
    ingest_repo(repo_path)
