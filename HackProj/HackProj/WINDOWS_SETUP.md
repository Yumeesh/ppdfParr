# UniChunk Windows Local Setup Guide

This guide will help you set up and run the UniChunk PDF Knowledge System on Windows, including solutions for common Windows-specific errors.

---

## 1. Prerequisites
- Python 3.10+ (from https://www.python.org/downloads/)
- [Poppler for Windows](https://github.com/oschwartz10612/poppler-windows/releases/) (for PDF image rendering)
- pip (Python package manager)

---

## 2. Create and Activate a Virtual Environment (Recommended)
```powershell
python -m venv .venv
.venv\Scripts\Activate
```

---

## 3. Install Python Dependencies
```powershell
python -m pip install -r unichunk\requirements.txt
```

---

## 4. Install Poppler for Windows
- Download the latest Poppler zip from [here](https://github.com/oschwartz10612/poppler-windows/releases/).
- Extract it to a folder, e.g., `C:\poppler`.
- Add `C:\poppler\bin` to your Windows PATH:
  - In PowerShell:
    ```powershell
    $env:PATH += ";C:\poppler\bin"
    ```
  - Or permanently via System Properties > Environment Variables.

---

## 5. Set Up the .env File
- Create a file named `.env` in the `unichunk\` folder with:
  ```
  GEMINI_API_KEY=your_actual_gemini_api_key_here
  ```

---

## 6. Fix SSL Certificate Errors (If You See CERTIFICATE_VERIFY_FAILED)
- Go to your Python install directory (e.g., `C:\Users\<YourUser>\AppData\Local\Programs\Python\Python3xx`)
- Run:
  ```powershell
  python ./Scripts/Install\ Certificates.command
  ```
- Or double-click `Install Certificates.command` in the `Scripts` folder.

---

## 7. Run the Streamlit App
```powershell
python -m streamlit run unichunk\frontend\app.py
```
- Open your browser to: http://localhost:8501

---

## 8. Torch/Streamlit Watcher Error Fix
- The code already sets:
  ```python
  os.environ["STREAMLIT_WATCHER_IGNORE_PACKAGES"] = "torch"
  os.environ["KMP_DUPLICATE_LIB_OK"] = "True"
  ```
- These must be at the very top of `app.py` (before any import) for Windows compatibility.

---

## 9. Optional: Use Local Embedding Model (No SSL Needed)
If you still have SSL issues, use a local embedding model for ChromaDB:
```python
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
embedding_function = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
collection = client.get_or_create_collection(collection_name, embedding_function=embedding_function)
```
Add this when creating your ChromaDB collection.

---

## 10. Troubleshooting
- **Poppler not found:** Ensure `C:\poppler\bin` is in your PATH.
- **SSL errors:** Run the Install Certificates script as above.
- **Torch watcher errors:** Ensure the environment variables are set at the very top of `app.py`.
- **Other issues:** Check the error message and refer to this guide or the main README.

---

You should now be able to run UniChunk locally on Windows!