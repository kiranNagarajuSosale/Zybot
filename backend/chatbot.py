import os
from dotenv import load_dotenv
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.retrievers import BM25Retriever, EnsembleRetriever
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables
load_dotenv()

def load_chain(role="developer", gemini_model="gemini-1.5-flash"):
    """
    Loads a ConversationalRetrievalChain with hybrid retrieval and role-based prompting.

    Args:
        role (str): The role of the assistant ("developer", "tester", or "user").
        gemini_model (str): Gemini model variant to use.

    Returns:
        ConversationalRetrievalChain: The configured LangChain conversational chain.
    """
    try:
        # 🔍 Load vector store with JinaAI embeddings
        embeddings = HuggingFaceEmbeddings(model_name="jinaai/jina-embeddings-v2-base-code")
        db = FAISS.load_local("vectorstore", embeddings, allow_dangerous_deserialization=True)

        # 🧠 Memory
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

        # 📜 Role-based instructions
        role_instructions = {
            "developer": "Explain code, architecture, and impact of changes.",
            "tester": "Explain features, suggest test cases and edge cases.",
            "user": "Explain functionality and navigation in simple language."
        }
        instruction = role_instructions.get(role, "You are a helpful assistant.")

        # ✨ Prompt template
        template = f"""You are an assistant helping a {role}. {instruction}

Chat History:
{{chat_history}}
Context: {{context}}

Question: {{question}}
Answer:"""
        prompt = PromptTemplate(
            template=template,
            input_variables=["chat_history", "context", "question"]
        )

        # 🔎 Hybrid retriever (FAISS + BM25)
        all_docs = db.similarity_search("", k=100)
        bm25 = BM25Retriever.from_documents(all_docs)
        bm25.k = 4

        retriever = EnsembleRetriever(
            retrievers=[db.as_retriever(search_kwargs={"k": 5}), bm25],
            weights=[0.5, 0.5]
        )

        # 🔥 LLM (Gemini)
        llm = ChatGoogleGenerativeAI(model=gemini_model, temperature=0)

        return ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=retriever,
            memory=memory,
            combine_docs_chain_kwargs={"prompt": prompt}
        )

    except Exception as e:
        print(f"❌ Error initializing assistant chain: {e}")
        return None


# CLI Entry Point
if __name__ == "__main__":
    print("🤖 Gemini Assistant Initializer")
    selected_role = input("Enter role (developer / tester / user): ").strip().lower()
    if selected_role not in ["developer", "tester", "user"]:
        selected_role = "developer"

    chain = load_chain(role=selected_role)

    if chain:
        print(f"\n✅ Assistant ready for: {selected_role.capitalize()}")
        print("💬 Type your question or 'exit' to quit.")
        while True:
            question = input("You: ")
            if question.lower() in ["exit", "quit"]:
                print("👋 Goodbye!")
                break
            try:
                response = chain.invoke({"question": question})
                print(f"Assistant: {response['answer']}\n")
            except Exception as e:
                print(f"❌ Error generating response: {e}")
    else:
        print("🚫 Failed to start the assistant.")
