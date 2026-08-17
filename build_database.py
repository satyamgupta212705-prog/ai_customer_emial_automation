from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

def create_vector_db():
    print("1. Loading FAQ document...")
    loader = TextLoader("company_faq.txt")
    docs = loader.load()

    print("2. Chunking text into smaller pieces...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=50)
    chunks = text_splitter.split_documents(docs)

    print("3. Downloading free embedding model (this takes a moment the first time)...")
    #----> Using a fast, free, local embedding model ----------
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    print("4. Saving to ChromaDB...")
    #------> This creates a local folder called "chroma_db" to store your data -------
    vectorstore = Chroma.from_documents(
        documents=chunks, 
        embedding=embeddings, 
        persist_directory="./chroma_db"
    )
    print("Database built successfully!")

if __name__ == "__main__":
    create_vector_db()