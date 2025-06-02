# FAISS Vector Store
import faiss
import numpy as np

class FaissStore:
    def __init__(self, dim):
        self.index = faiss.IndexFlatL2(dim)
        self.vectors = []
        self.metadata = []

    def add(self, embedding, metadata):
        self.index.add(np.array([embedding]).astype('float32'))
        self.vectors.append(embedding)
        self.metadata.append(metadata)

    def query(self, embedding, top_k=5):
        D, I = self.index.search(np.array([embedding]).astype('float32'), top_k)
        return [self.metadata[i] for i in I[0]]
