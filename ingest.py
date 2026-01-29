
import os
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_google_genai import GoogleGenerativeAIEmbeddings
# from langchain_google_genai.embeddings import GoogleGenerativeAIEmbeddings
from langchain.chains import retrieval
from langchain_google_genai import ChatGoogleGenerativeAI,GoogleGenerativeAIEmbeddings

from langchain.vectorstores import FAISS
from dotenv import load_dotenv

load_dotenv()

PDF_DIR = "data/pdfs"
VECTOR_DIR = "vectorstore"

def ingest_pdfs():
    documents = []

    for file in os.listdir(PDF_DIR):
        if file.endswith(".pdf"):
            loader = PyPDFLoader(os.path.join(PDF_DIR, file))
            documents.extend(loader.load())

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = splitter.split_documents(documents)

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001"
    )

    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(VECTOR_DIR)

    print("✅ PDF ingestion completed")

if __name__ == "__main__":
    ingest_pdfs()
