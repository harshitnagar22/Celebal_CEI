import os
import json
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document
from src.core.config import config

class VectorDBManager:
    def __init__(self):
        # We use Google's embedding model since we are using Gemini
        # It requires GOOGLE_API_KEY to be set
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
        self.persist_directory = config.VECTOR_DB_DIR
        os.makedirs(self.persist_directory, exist_ok=True)
        self.collection_name = "knowledge_base"
        
        self.vectorstore = Chroma(
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
            persist_directory=self.persist_directory
        )

    def populate_db(self, chunks_file_path):
        # loads json chunks and pushes them to chroma
        if not os.path.exists(chunks_file_path):
            print(f"File {chunks_file_path} not found.")
            return

        with open(chunks_file_path, 'r', encoding='utf-8') as f:
            chunks = json.load(f)

        documents = []
        for chunk in chunks:
            doc = Document(
                page_content=chunk["text"],
                metadata=chunk["metadata"]
            )
            documents.append(doc)
            
        import time
        print(f"Adding {len(documents)} documents to vector store in batches (to respect API rate limits)...")
        batch_size = 90
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i+batch_size]
            print(f"Adding batch {i//batch_size + 1} ({len(batch)} documents)...")
            self.vectorstore.add_documents(batch)
            if i + batch_size < len(documents):
                print("Sleeping for 60 seconds to respect free-tier rate limits...")
                time.sleep(60)
        print("Documents added successfully.")

    def as_retriever(self, search_kwargs={"k": 3}):
        # setup the retriever so langgraph can query it
        return self.vectorstore.as_retriever(search_kwargs=search_kwargs)

if __name__ == "__main__":
    vdb = VectorDBManager()
    chunks_path = os.path.join(config.DATA_DIR, "processed", "chunks.json")
    vdb.populate_db(chunks_path)
