# Chroma Vector Store
import chromadb
from chromadb.config import Settings

class ChromaStore:
    def __init__(self, persist_directory='chroma_db'):
        self.client = chromadb.Client(Settings(persist_directory=persist_directory))
        self.collection = self.client.get_or_create_collection('unichunks')

    def add(self, embedding, metadata):
        self.collection.add(embeddings=[embedding], metadatas=[metadata])

    def query(self, embedding, top_k=5):
        return self.collection.query(query_embeddings=[embedding], n_results=top_k)
