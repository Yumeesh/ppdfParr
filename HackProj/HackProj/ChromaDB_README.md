# Accessing and Inspecting ChromaDB in UniChunk

This guide explains how to access your local ChromaDB vector database, inspect its contents, and understand how the data is stored for the UniChunk PDF Knowledge Extraction and Q&A system.

---

## 1. Where is ChromaDB Data Stored?

- The ChromaDB database is stored locally in the directory:
  
  ```
  output/chroma_db/
  ```
- Each PDF ingested creates a collection named after the PDF file (without extension).

---

## 2. How is Data Stored?

- **Collections:** Each PDF = one ChromaDB collection.
- **Documents:** Each chunk of PDF text is a document in the collection.
- **Metadata:** Each document has metadata, e.g.:
  - `page_no`: Page number in the PDF
  - `chunk_idx`: Index of the chunk on that page
  - `images`: Comma-separated image paths (if any)
  - `pdf_name`: Name of the PDF

---

## 3. How to Access ChromaDB Programmatically

You can use Python to access and inspect the ChromaDB database. Here is a step-by-step guide:

### a. Install ChromaDB (if not already installed)

```bash
pip install chromadb
```

### b. Open a Python shell or script in your project root

```bash
python
```

### c. Connect to the ChromaDB database

```python
import chromadb
from chromadb.config import Settings

client = chromadb.Client(Settings(persist_directory="output/chroma_db"))
```

### d. List all collections (PDFs ingested)

```python
collections = client.list_collections()
for col in collections:
    print(col.name)
```

### e. Access a specific collection

```python
collection = client.get_collection("YourPDFName")  # Replace with your PDF's name (no .pdf)
```

### f. Inspect documents and metadata

```python
# Get all document IDs
ids = collection.get()['ids']
print(ids)

# Fetch documents and metadata for the first 5 chunks
results = collection.get(ids=ids[:5])
for doc, meta in zip(results['documents'], results['metadatas']):
    print("Document chunk:", doc)
    print("Metadata:", meta)
    print("---")
```

### g. Query ChromaDB (semantic search)

```python
query = "What are the key obligations of the manufacturers?"
results = collection.query(query_texts=[query], n_results=3)
for doc, meta in zip(results['documents'][0], results['metadatas'][0]):
    print("Relevant chunk:", doc)
    print("Metadata:", meta)
    print("---")
```

---

## 4. Notes
- ChromaDB is a vector database; it stores embeddings for semantic search.
- All metadata is stored as simple types (str, int, float, bool).
- Images are referenced by path in metadata, not stored in the DB itself.

---

## 5. Cleaning Up Unnecessary Files
- The `output/` directory should only contain ChromaDB data and images you want to keep.
- To remove all unnecessary files (e.g., old JSONs, logs, etc.), you can run:

```bash
rm -rf output/*.json output/*.log output/*.db output/*.sqlite3
```

---

## 6. Further Help
- For more, see the [ChromaDB documentation](https://docs.trychroma.com/).
- If you have custom ingestion or chunking logic, check your `unichunk/` Python modules.
