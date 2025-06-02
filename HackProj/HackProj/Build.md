## ✅ OVERVIEW

**Objective**
Build a system to convert complex, multimodal PDFs (manuals, diagrams, logs) into semantically chunked knowledge representations, enabling accurate information retrieval using natural language queries. It must work fully offline with only **free and open-source tools**.

**Primary Goals**

* Extract text, images, tables, and annotations from PDFs (digital + scanned)
* Preserve layout, saliency, and relationships between content blocks
* Form semantic content units (“UniChunks”)
* Embed chunks using text and image embedding models
* Store them in a **local vector store** (FAISS / Chroma)
* Enable semantic retrieval via query and present results with context

---

## ⚙️ SYSTEM REQUIREMENTS

### Programming Language & Environment

* **Python ≥ 3.8** (recommended: Python 3.10+)
* Virtual environment: `venv` or `conda`
* RAM: 8–16 GB (minimum for moderate files)
* CPU is sufficient for Tesseract-based OCR; GPU not mandatory.

### Core Libraries and Tools

| Purpose           | Tool                                                | Type        |
| ----------------- | --------------------------------------------------- | ----------- |
| PDF parsing       | PyMuPDF (`fitz`), `pdfplumber`                      | Open source |
| OCR               | `Tesseract` + `pytesseract`                         | Open source |
| Image processing  | `OpenCV`, `pdf2image`                               | Open source |
| Text embeddings   | `sentence-transformers` (e.g., all-MiniLM-L6-v2)    | Open source |
| Image embeddings  | `CLIP ViT-B/32` via HuggingFace                     | Open source |
| Vector DB         | FAISS / Chroma (prefer Chroma for metadata support) | Open source |
| Metadata handling | JSON, optionally `tinydb` or `sqlite3`              | Built-in    |
| Frontend          | Streamlit or FastAPI                                | Open source |

---

## 🧱 SYSTEM ARCHITECTURE & MODULES

Split the system into **modular components** for scalability and maintainability. Each module is responsible for a clearly defined task.

---

### 🧩 Module 1: PDF Ingestion & Classification

**Objective**: Load PDF pages, correct orientation, and classify each as *scanned* (image-based) or *digital* (text extractable).

**Tools**:

* `PyMuPDF` for basic PDF operations
* `pdf2image` to convert PDF pages into images (for OCR)
* `Tesseract` for OCR (via `pytesseract`)

**Key Features**:

* Detect rotation/skew and fix page orientation
* Extract text if possible (digital); otherwise route to OCR
* Normalize images (DPI \~300) for better OCR accuracy

---

### 🧩 Module 2: Layout Parsing & Content Element Detection

**Objective**: Identify structural elements (text blocks, tables, images, annotations, diagrams).

**Tools**:

* `pdfplumber` (for digital pages) to extract bounding boxes of text, images, and tables
* `OpenCV` (for scanned images) to detect contours, handwritten notes, legends, stamps, etc.

**Key Tasks**:

* Detect page structure: single/multi-column, rotated sections
* Extract:

  * Text (with bounding box, font size/style if available)
  * Tables (bounding box and headers)
  * Captions and nearby blocks
  * Embedded images or scanned figures
* Handle rotated/marginal annotations and handwritten text with image processing

---

### 🧩 Module 3: Metadata Engine

**Objective**: Create a unified representation (JSON) that holds layout-aware metadata for each element.

**Metadata Includes**:

* Page number
* Type (`text`, `table`, `image`, `caption`, `handwriting`)
* Position and dimensions (bounding box)
* Font info (optional)
* Source (`digital` or `OCR`)
* Reference linking (e.g., caption → image, table → description)

**Storage Format**:

* JSON object per document with hierarchical structure
* Optional: Use a small local DB (e.g., TinyDB or SQLite) for faster querying

---

### 🧩 Module 4: UniChunk Creation (Semantic Chunking)

**Objective**: Merge logically connected blocks into semantically meaningful units (called **UniChunks**).

**Examples**:

* Heading + Paragraph
* Image + Caption
* Table + Note
* Diagram + Associated Explanation

**Chunking Strategy**:

* **Layout-Aware**: Use spatial proximity (above/below/side) to group blocks
* **Semantic-Aware**: Prefer thematic similarity and document flow (section-level context)
* **Multi-modal**: UniChunks can contain mixed content (text + image)

Each **UniChunk** will be represented as:

```json
{
  "id": "chunk_001",
  "content": "combined text content",
  "type": "text/table/image/multimodal",
  "elements": [...element_ids...],
  "page_no": 5,
  "source": "digital"
}
```

---

### 🧩 Module 5: Embedding Pipeline

**Objective**: Convert each UniChunk into a **vector embedding** that represents its semantic meaning.

**Tools**:

* **Text**: Use `sentence-transformers` (e.g., `all-MiniLM-L6-v2`, or any small SBERT variant)
* **Image**: Use `CLIP ViT-B/32` via `transformers` + `PIL`

**Embedding Dimensions**:

* Text: 384-dim
* Image: 512-dim

**Process**:

* If UniChunk contains only text → use text encoder
* If it includes an image → use image encoder (or both for multimodal)
* Normalize and store embeddings alongside UniChunk ID and metadata

---

### 🧩 Module 6: Vector Storage & Retrieval Engine

**Objective**: Store embeddings in a local vector DB with metadata, and enable fast **semantic search**.

**Tools**:

* **Chroma DB** (recommended for ease of use with metadata)
* **FAISS** (faster and lighter; use if metadata is managed separately)

**Responsibilities**:

* Insert vector + metadata into DB
* Perform similarity search using embedded queries
* Support filters (e.g., by page, type)

**Structure**:

```json
{
  "embedding": [...],
  "metadata": {
    "chunk_id": "chunk_001",
    "type": "text",
    "page": 5,
    "source": "OCR",
    "content": "..."
  }
}
```

---

### 🧩 Module 7: Query Interface & Search

**Objective**: Accept user queries (in natural language), embed them, and retrieve the most relevant UniChunks.

**Process**:

1. Input query → generate embedding
2. Search in vector DB → get top-k similar UniChunks
3. Return content + metadata (page, type, source, snippet)
4. (Optional) Post-rank based on saliency, recentness, or type preference

**Use Cases**:

* “What does Table 2 describe?”
* “How is the circuit diagram explained?”
* “Show all safety guidelines for section 5.”

---

### 🧩 Module 8: Frontend Interface

**Objective**: Provide a **simple and usable UI** for:

* Uploading PDF files
* Running the UniChunk pipeline
* Inputting queries and showing results

**Options**:

* **Streamlit (preferred)** for quick web UI
* **FastAPI** if you need an API-first backend

**Pages**:

1. Upload & Process PDF
2. Show Extracted UniChunks (with metadata)
3. Input Search Query → View Results

---

## 🔍 STAGE-WISE DEVELOPMENT GUIDE

### ✅ Stage 1: Setup & Architecture

* Define folders for each module (e.g., `ingestion/`, `parser/`, `chunker/`, `embedding/`, etc.)
* Setup `requirements.txt` with all packages
* Install Tesseract and test OCR on a scanned page
* Design JSON schema for metadata and UniChunks

### ✅ Stage 2: Core Ingestion and Chunking Pipeline

* Build working ingestion for PDFs (digital + scanned)
* Parse layout and store structured elements
* Implement basic UniChunk logic (image + caption, etc.)
* Store UniChunks as enriched JSON

### ✅ Stage 3: Embedding + Vector Storage

* Add support for SBERT/CLIP models (via Hugging Face)
* Embed UniChunks and insert into FAISS/Chroma
* Perform semantic search using example queries

### ✅ Stage 4: End-to-End UI + Retrieval

* Integrate with Streamlit for document upload and query
* Build search UI to display top matches with page + preview
* Add functionality to explore UniChunks manually

---

## 🧪 TESTING AND EVALUATION STRATEGY

**Testing**:

* Try with at least 3 PDFs:

  * 1 scanned (with images/tables)
  * 1 digital (multicolumn/manual)
  * 1 mixed (diagrams + notes)

**Metrics**:

* **Accuracy of Retrieval**: Are relevant chunks returned?
* **Chunking Quality**: Does each UniChunk preserve layout & meaning?
* **OCR Quality**: Are scanned sections readable?
* **Latency**: How long does processing/querying take?

---

## 🔚 FINAL OUTCOME

After implementation, you should have:

* A local system that takes a PDF and builds an indexed knowledge base
* Streamlit UI to query documents semantically
* Full modular codebase, easily extensible and deployable to cloud (future)

---

## 📁 FOLDER STRUCTURE (Recommended)

```
unichunk/
│
├── ingestion/
│   └── pdf_ingestor.py
├── parser/
│   └── layout_parser.py
├── chunker/
│   └── unichunk_creator.py
├── embedding/
│   ├── text_embedder.py
│   ├── image_embedder.py
├── vector_store/
│   ├── store_faiss.py
│   ├── store_chroma.py
├── metadata/
│   └── metadata_engine.py
├── frontend/
│   └── app.py (Streamlit UI)
├── utils/
│   └── config.py
├── test_pipeline.py
├── requirements.txt
└── README.md
```

