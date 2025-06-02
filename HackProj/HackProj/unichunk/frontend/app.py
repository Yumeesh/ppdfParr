import os
import sys
import re
import traceback
import tempfile
import json
import uuid
import streamlit as st
from dotenv import load_dotenv

# --- ENVIRONMENT SETUP ---
os.environ["STREAMLIT_WATCHER_IGNORE_PACKAGES"] = "torch"
os.environ["KMP_DUPLICATE_LIB_OK"] = "True"
os.environ["CUDA_VISIBLE_DEVICES"] = ""

# Ensure .env is loaded from the correct location
DOTENV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../.env'))
if not os.path.exists(DOTENV_PATH):
    st.error(f".env file not found at {DOTENV_PATH}. Please create it and add GEMINI_API_KEY=your_key_here.")
    st.stop()
load_dotenv(DOTENV_PATH, override=True)

# --- STREAMLIT PAGE CONFIG ---
st.set_page_config(page_title="UniChunk PDF Knowledge System", layout="wide")
st.title("UniChunk PDF Knowledge System")

st.sidebar.header("Upload & Process PDF")
uploaded_files = st.sidebar.file_uploader("Choose PDF file(s)", type=["pdf"], accept_multiple_files=True)

# --- UTILS ---
def sanitize_collection_name(name):
    name = re.sub(r'[^a-zA-Z0-9._-]', '_', name)
    name = name.strip('_-.')
    if len(name) < 3:
        name = (name + '_db')[:3]
    if len(name) > 512:
        name = name[:512]
    return name

def chunk_text(text, chunk_size=1000, overlap=100):
    paragraphs = [p for p in text.split('\n') if p.strip()]
    chunks = []
    current = ""
    for p in paragraphs:
        if len(current) + len(p) < chunk_size:
            current += p + "\n"
        else:
            chunks.append(current.strip())
            current = p + "\n"
    if current.strip():
        chunks.append(current.strip())
    final_chunks = []
    for i, chunk in enumerate(chunks):
        prev = chunks[i-1][-overlap:] if i > 0 else ""
        final_chunks.append(prev + chunk)
    return final_chunks

# --- MAIN LOGIC ---
if uploaded_files:
    try:
        output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../output'))
        chroma_db_path = os.path.join(output_dir, "chroma_db")
        images_dir = os.path.join(output_dir, 'images')
        os.makedirs(images_dir, exist_ok=True)
        pdf_paths = []
        collection_names = []
        pdf_name_map = {}
        for uploaded_file in uploaded_files:
            temp_dir = tempfile.gettempdir()
            pdf_path = os.path.join(temp_dir, uploaded_file.name)
            with open(pdf_path, "wb") as f:
                f.write(uploaded_file.read())
            pdf_paths.append(pdf_path)
            pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
            collection_name = sanitize_collection_name(pdf_name)
            collection_names.append(collection_name)
            pdf_name_map[collection_name] = os.path.basename(pdf_path)

        if st.button("Extract Text & Ingest to Vector DB"):
            try:
                sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
                from ingestion.pdf_ingestor import PDFIngestor
                import chromadb
                from chromadb.config import Settings
                from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
                embedding_function = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
                client = chromadb.Client(Settings(persist_directory=chroma_db_path))
                for pdf_path, collection_name in zip(pdf_paths, collection_names):
                    ingestor = PDFIngestor(pdf_path)
                    pages = ingestor.doc
                    extracted = []
                    for i, page in enumerate(pages):
                        page_no = i + 1
                        text = page.get_text()
                        images = []
                        for img_index, img in enumerate(page.get_images(full=True)):
                            xref = img[0]
                            base_image = ingestor.doc.extract_image(xref)
                            img_bytes = base_image['image']
                            img_ext = base_image['ext']
                            img_path = os.path.join(images_dir, f"{collection_name}_page{page_no}_img{img_index+1}.{img_ext}")
                            with open(img_path, "wb") as img_file:
                                img_file.write(img_bytes)
                            images.append({
                                "image_path": os.path.relpath(img_path, output_dir),
                                "bbox": img[5:9] if len(img) > 8 else None
                            })
                        extracted.append({
                            "page_no": page_no,
                            "text": text,
                            "images": images
                        })
                    json_path = os.path.join(output_dir, f"{collection_name}.json")
                    with open(json_path, "w") as f:
                        json.dump(extracted, f, indent=2)
                    collection = client.get_or_create_collection(collection_name, embedding_function=embedding_function)
                    for page in extracted:
                        page_no = page["page_no"]
                        text = page["text"]
                        images = page.get("images", [])
                        image_paths = ','.join([img['image_path'] for img in images]) if images else ""
                        for idx, chunk in enumerate(chunk_text(text)):
                            doc_id = str(uuid.uuid4())
                            metadata = {
                                "page_no": int(page_no),
                                "chunk_idx": int(idx),
                                "images": image_paths,
                                "pdf_name": str(collection_name)
                            }
                            collection.add(
                                documents=[chunk],
                                metadatas=[metadata],
                                ids=[doc_id]
                            )
                st.success("Extraction and vector DB ingestion complete for all PDFs! Download your JSONs below.")
                for collection_name in collection_names:
                    json_path = os.path.join(output_dir, f"{collection_name}.json")
                    with open(json_path, "rb") as f:
                        st.download_button(f"Download JSON for {pdf_name_map[collection_name]}", f, file_name=f"{collection_name}.json", mime="application/json")
            except Exception as e:
                st.error(f"Extraction/Ingestion failed: {e}")
                st.text(traceback.format_exc())

        # --- CHAT BLOCK ---
        try:
            import chromadb
            from chromadb.config import Settings
            from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
            embedding_function = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
            client = chromadb.Client(Settings(persist_directory=chroma_db_path))
            collections = [client.get_or_create_collection(name, embedding_function=embedding_function) for name in collection_names]
            gemini_api_key = os.environ.get("GEMINI_API_KEY", "")
            if not gemini_api_key:
                st.error("GEMINI_API_KEY is not set in your .env file. Please add it and restart the app.")
                st.stop()
            from httpx import AsyncClient
            from pydantic_ai import Agent
            from pydantic_ai.models.gemini import GeminiModel
            from pydantic_ai.providers.google_gla import GoogleGLAProvider
            custom_http_client = AsyncClient(timeout=30)
            gemini_model = GeminiModel(
                'gemini-1.5-flash',
                provider=GoogleGLAProvider(api_key=gemini_api_key, http_client=custom_http_client),
            )
            agent = Agent(gemini_model)
            user_query = st.text_input("Ask your PDFs:")
            if user_query:
                if 'chat_history' not in st.session_state:
                    st.session_state['chat_history'] = []
                st.session_state['chat_history'].append({"role": "user", "content": user_query})
                chat_context = st.session_state['chat_history'][-5:]
                chat_prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in chat_context])
                import asyncio
                async def get_agent_answer():
                    try:
                        all_docs = []
                        all_metas = []
                        for collection in collections:
                            results = collection.query(query_texts=[chat_prompt], n_results=3)
                            all_docs.extend(results['documents'][0])
                            all_metas.extend(results['metadatas'][0])
                        context = "\n".join(all_docs)
                        full_prompt = f"Context from PDFs:\n{context}\n\nUser: {user_query}"
                        return all_docs, all_metas, await agent.run(full_prompt)
                    except Exception as e:
                        return [], [], f"Error during retrieval or chat: {e}\n{traceback.format_exc()}"
                try:
                    loop = asyncio.get_running_loop()
                except RuntimeError:
                    loop = None
                if loop and loop.is_running():
                    import nest_asyncio
                    nest_asyncio.apply()
                    docs, metadatas, answer = loop.run_until_complete(get_agent_answer())
                else:
                    docs, metadatas, answer = asyncio.run(get_agent_answer())
                st.session_state['chat_history'].append({"role": "agent", "content": answer})
                st.session_state['last_refs'] = list(zip(docs, metadatas))
                if 'open_ref' not in st.session_state:
                    st.session_state['open_ref'] = None
                for idx, msg in enumerate(st.session_state['chat_history'][-10:]):
                    if msg['role'] == 'user':
                        st.markdown(f"**You:** {msg['content']}")
                    else:
                        agent_content = str(msg['content']).strip()
                        st.markdown(f"**Agent:**\n\n{agent_content}")
                        if idx == len(st.session_state['chat_history'][-10:]) - 1 and 'last_refs' in st.session_state:
                            for ref_idx, (doc, meta) in enumerate(st.session_state['last_refs']):
                                pdf_file = pdf_name_map.get(meta.get('pdf_name', ''), None)
                                ref_btn = st.button(
                                    f"Show Reference {ref_idx+1} (PDF: {pdf_file}, Page {meta.get('page_no', '?')})",
                                    key=f"refbtn_{len(st.session_state['chat_history'])}_{ref_idx}"
                                )
                                if ref_btn:
                                    st.session_state['open_ref'] = (len(st.session_state['chat_history']), ref_idx)
                                # Only show the image if this reference is open and the button was clicked
                                if st.session_state.get('open_ref') == (len(st.session_state['chat_history']), ref_idx):
                                    page_no = meta.get('page_no', None)
                                    if page_no is not None and pdf_file:
                                        ref_label = f"Reference: {pdf_file} - Page {page_no}"
                                        pdf_path = None
                                        for p in pdf_paths:
                                            if os.path.basename(p) == pdf_file:
                                                pdf_path = p
                                                break
                                        if pdf_path:
                                            try:
                                                from pdf2image import convert_from_path
                                                # Ensure page_no is int and valid
                                                page_no_int = int(page_no)
                                                images = convert_from_path(pdf_path, first_page=page_no_int, last_page=page_no_int, fmt='jpeg', single_file=True)
                                                if images and len(images) > 0:
                                                    st.image(images[0], caption=ref_label, use_container_width=True)
                                                else:
                                                    st.warning(f"Could not render page {page_no} from PDF. PDF path: {pdf_path}")
                                            except Exception as e:
                                                st.warning(f"Error rendering PDF page: {e}\nPDF path: {pdf_path}")
                                        else:
                                            st.warning(f"PDF file not found for reference: {pdf_file}")
                                    else:
                                        st.warning("Reference metadata missing page number or PDF file.")
        except Exception as e:
            st.error(f"Critical error: {e}")
            st.text(traceback.format_exc())
    except Exception as e:
        st.error(f"App error: {e}")
        st.text(traceback.format_exc())

# --- SQLITE PATCH FOR CHROMADB ---
try:
    import pysqlite3
    sys.modules["sqlite3"] = sys.modules["pysqlite3"]
except ImportError:
    pass
