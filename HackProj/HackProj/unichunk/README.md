# UniChunk PDF Knowledge System

A modular, fully open-source pipeline to convert complex PDFs into semantically chunked, searchable knowledge bases.

## Folder Structure

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
│   └── app.py
├── utils/
│   └── config.py
├── test_pipeline.py
├── requirements.txt
└── README.md
```

## Modules
- **ingestion/**: PDF loading, orientation correction, digital/scanned classification
- **parser/**: Layout parsing, element detection
- **chunker/**: UniChunk creation (semantic chunking)
- **embedding/**: Text & image embedding
- **vector_store/**: Vector DB storage/retrieval
- **metadata/**: Metadata engine (JSON, DB)
- **frontend/**: Streamlit UI
- **utils/**: Configs, helpers

## Setup
See `Build.md` for full build instructions.
