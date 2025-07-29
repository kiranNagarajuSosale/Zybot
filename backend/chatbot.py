import os
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables from .env file
load_dotenv()



def load_chain(role="developer", geminiModel="gemini-1.5-flash"):
    """
    Loads and configures a conversational retrieval chain based on the specified role.

    Args:
        role (str): The role of the assistant ("developer", "tester", or "user").

    Returns:
        ConversationalRetrievalChain: The configured LangChain conversational chain.
    """
    try:
        # Load FAISS vector store with HuggingFace embeddings
        # NOTE: allow_dangerous_deserialization=True is used for loading potentially
        # untrusted data. Ensure your 'vectorstore' is from a trusted source.
        db = FAISS.load_local(
            "vectorstore",
            HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2"),
            allow_dangerous_deserialization=True
        )
        retriever = db.as_retriever(search_kwargs={"k": 5})
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

        # Role-based prompt instructions
        role_prompt_instruction = {
            "developer": "Explain code, architecture, and impact of changes.",
            "tester": "Explain features, suggest test cases and edge cases. Use DOM and XPath context if available.",
            "user": "Explain functionality and navigation in simple language."
        }
        # Get the specific instruction for the current role, with a default if role is not found
        instruction = role_prompt_instruction.get(role, "You are a helpful assistant.")

        # Updated template to include role-based instructions and chat history
        template = f"""You are an assistant helping a {role}. {instruction}
Chat History:
{{chat_history}}
Context: {{context}}
Question: {{question}}
Answer:"""
        prompt = PromptTemplate(template=template, input_variables=["chat_history", "context", "question"])

        # Initialize Gemini LLM
        # Ensure GOOGLE_API_KEY is set in your .env file
        llm = ChatGoogleGenerativeAI(model=geminiModel, temperature=0)

        return ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=retriever,
            memory=memory,
            combine_docs_chain_kwargs={"prompt": prompt}
        )
    except Exception as e:
        print(f"An error occurred during chain loading: {e}")
        print("Please ensure your 'vectorstore' exists and your GOOGLE_API_KEY is correctly set in the .env file.")
        return None

if __name__ == "__main__":
    print("Welcome to the AI Assistant! You can specify your role (developer, tester, user).")
    selected_role = input("Enter your role (developer, tester, user, or press Enter for developer): ").lower()
    if selected_role not in ["developer", "tester", "user"]:
        selected_role = "developer" # Default to developer if invalid input

    chain = load_chain(role=selected_role)

    if chain:
        print(f"\nAssistant initialized for role: {selected_role.capitalize()}")
        print("Type 'exit' or 'quit' to end the conversation.")
        while True:
            query = input("You: ")
            if query.lower() in ["exit", "quit"]:
                print("Ending conversation. Goodbye! 👋")
                break
            try:
                response = chain.invoke({"question": query}) # Use a dictionary for invoke
                print(f"Assistant: {response['answer']}")
            except Exception as e:
                print(f"An error occurred during response generation: {e}")
                print("Please check your API key, network connection, or try a different query.")
    else:
        print("Failed to load the conversational chain. Exiting. 😔")