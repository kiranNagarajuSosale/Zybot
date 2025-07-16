import os
from functools import partial
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, PythonLoader, TextLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Load environment variables
load_dotenv()

# File extensions and their loaders
SUPPORTED_EXTENSIONS = {
    ".py": PythonLoader,
    ".txt": partial(TextLoader, encoding="utf-8"),
    ".md": partial(TextLoader, encoding="utf-8"),
    ".json": partial(TextLoader, encoding="utf-8"),
    ".html": partial(TextLoader, encoding="utf-8"),
    ".cshtml": partial(TextLoader, encoding="utf-8"),
    ".sql": partial(TextLoader, encoding="utf-8"),
    ".cs": partial(TextLoader, encoding="utf-8"),
    ".js": partial(TextLoader, encoding="utf-8"),
    ".xml": partial(TextLoader, encoding="utf-8")
}

def load_all_files(repo_path: str):
    all_docs = []
    total_files = 0

    for ext, loader_cls in SUPPORTED_EXTENSIONS.items():
        loader = DirectoryLoader(repo_path, glob=f"**/*{ext}", loader_cls=loader_cls, recursive=True)
        try:
            docs = loader.load()
            if docs:
                print(f"📄 {ext}: {len(docs)} files loaded")
                all_docs.extend(docs)
                total_files += len(docs)
            else:
                print(f"⚠️  {ext}: no files found")
        except Exception as e:
            print(f"❌ Error loading {ext} files: {e}")

    return all_docs, total_files

def ingest_docs(repo_path="your_repo_path", output_dir="vectorstore"):
    if not os.path.exists(repo_path):
        raise FileNotFoundError(f"❌ Provided repo path does not exist: {repo_path}")

    print(f"📂 Scanning directory: {repo_path}")
    docs, total_files = load_all_files(repo_path)

    if total_files == 0:
        print("🚫 No supported files found in the repo. Nothing to ingest.")
        return

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    split_docs = splitter.split_documents(docs)
    print(f"🧩 Split into {len(split_docs)} chunks")

    print("🧠 Generating embeddings using HuggingFace...")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    db = FAISS.from_documents(split_docs, embeddings)
    db.save_local(output_dir)
    print(f"✅ Vector store saved to: {output_dir}")

if __name__ == "__main__":
    ingest_docs(r"")