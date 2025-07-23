# ✅ ingest.py — Optimized Ingestion with Metadata & MultiRepo Support

import os
import shutil
import tempfile
import zipfile
import requests
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, PythonLoader, TextLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

load_dotenv()

SUPPORTED_EXTENSIONS = {
    ".py": PythonLoader,
    ".txt": TextLoader,
    ".md": TextLoader,
    ".json": TextLoader,
    ".html": TextLoader,
    ".cshtml": TextLoader,
    ".sql": TextLoader,
    ".cs": TextLoader,
    ".js": TextLoader,
    ".xml": TextLoader
}

def load_documents(path: str) -> List[Document]:
    all_docs = []
    for ext, loader_cls in SUPPORTED_EXTENSIONS.items():
        loader = DirectoryLoader(path, glob=f"**/*{ext}", loader_cls=loader_cls, recursive=True)
        try:
            docs = loader.load()
            for doc in docs:
                doc.metadata["source_path"] = doc.metadata.get("source", "")
            all_docs.extend(docs)
        except Exception as e:
            print(f"❌ Failed to load {ext} files: {e}")
    return all_docs

def split_documents(documents: List[Document]) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    return splitter.split_documents(documents)

def embed_and_save(docs: List[Document], output_dir="vectorstore"):
    if not docs:
        print("🚫 No documents to index.")
        return
    embeddings = HuggingFaceEmbeddings(model_name="intfloat/e5-base-v2")
    split_docs = split_documents(docs)
    db = FAISS.from_documents(split_docs, embeddings)
    db.save_local(output_dir)
    print(f"✅ Ingestion complete. Vector store saved to: {output_dir}")

def ingest_repo(repo_path: str):
    if not os.path.exists(repo_path):
        raise FileNotFoundError(f"❌ Path does not exist: {repo_path}")
    print(f"📂 Ingesting from: {repo_path}")
    documents = load_documents(repo_path)
    embed_and_save(documents)

def ingest_zip(zip_path: str):
    with tempfile.TemporaryDirectory() as tmpdir:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(tmpdir)
        ingest_repo(tmpdir)

def ingest_github_repo(raw_url: str):
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = os.path.join(tmpdir, "repo.zip")
        print(f"⬇️ Downloading from GitHub: {raw_url}")
        response = requests.get(raw_url)
        with open(zip_path, "wb") as f:
            f.write(response.content)
        ingest_zip(zip_path)

if __name__ == "__main__":
    # 🔁 Example usage
    ingest_repo(r"path/to/local/repo")
    # ingest_zip("path/to/file.zip")
    # ingest_github_repo("https://github.com/user/repo/archive/refs/heads/main.zip")
