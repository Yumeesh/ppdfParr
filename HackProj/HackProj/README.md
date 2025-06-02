# UniChunk PDF Knowledge Extraction & Q&A System

This guide will help you set up, run, and use the UniChunk system for PDF knowledge extraction, vector database ingestion, and Gemini-powered Q&A.

---

## 1. Prerequisites
- Python 3.10+
- [Poppler](https://poppler.freedesktop.org/) (for PDF image rendering)
- pip (Python package manager)

---

## 2. Install System Dependencies

**Poppler (for Linux):**
```bash
sudo apt-get update && sudo apt-get install -y poppler-utils
```

---

## 3. Install Python Dependencies

From the project root:
```bash
pip install -r unichunk/requirements.txt
```

---

## 4. Set Up Environment Variables

Create a `.env` file in `unichunk/` with your Gemini API key:
```
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

---

## 5. Run the Streamlit App

From the project root:
```bash
streamlit run unichunk/frontend/app.py --server.headless true --server.port 8501
```

Open your browser and go to:
```
http://localhost:8501
```

---

## 6. Using the App

1. **Upload a PDF** using the sidebar.
2. Click **Extract Text & Ingest to Vector DB**.
3. Once complete, ask questions in the chat box.
4. For answers referencing the PDF, the relevant page will be visually displayed below the answer.

---

## 7. Troubleshooting
- If you see errors about Poppler, make sure it is installed and available in your PATH.
- If you see errors about missing environment variables, check your `.env` file.
- If you see blank images for PDF pages, ensure the PDF is not encrypted or corrupted.

---

## 8. Advanced
- See `ChromaDB_README.md` for details on accessing and inspecting the vector database.
- All extracted images are saved in `output/images/`.
- All vector DB data is in `output/chroma_db/`.

---

## 9. Support
- For more, see the code in `unichunk/` and the [ChromaDB documentation](https://docs.trychroma.com/).
