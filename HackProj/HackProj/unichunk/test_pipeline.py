import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Test pipeline for UniChunk system
# This is a stub for running the full pipeline step by step

def main():
    from unichunk.ingestion.pdf_ingestor import PDFIngestor
    from unichunk.parser.layout_parser import LayoutParser
    from unichunk.metadata.metadata_engine import MetadataEngine
    from unichunk.chunker.unichunk_creator import UniChunkCreator
    import os
    import json

    # Use a sample PDF from Dataset
    pdf_path = os.path.abspath("../Dataset/Medical_Device_Coordination_Group_Document.pdf")
    if not os.path.exists(pdf_path):
        pdf_path = os.path.abspath("./Dataset/Medical_Device_Coordination_Group_Document.pdf")
    print(f"Processing: {pdf_path}")

    ingestor = PDFIngestor(pdf_path)
    pages = ingestor.extract_pages()
    parser = LayoutParser(pdf_path)
    metadata_engine = MetadataEngine()
    chunker = UniChunkCreator()

    for page in pages:
        page_no = page['page_no']
        if page['type'] == 'digital':
            elements = parser.parse_digital(page_no-1)
            for el in elements:
                metadata_engine.add_element(page_no, el['type'], el.get('bbox'), 'digital', {'text': el.get('text')})
                if el['type'] == 'text':
                    chunker.create_chunk(el['text'], 'text', [el], page_no, 'digital')
        else:
            elements = parser.parse_scanned(page['image'])
            for el in elements:
                metadata_engine.add_element(page_no, el['type'], el.get('bbox'), 'scanned')
                # For demo, treat each block as a chunk
                chunker.create_chunk('image block', 'image', [el], page_no, 'scanned')

    # Save metadata and chunks
    os.makedirs('output', exist_ok=True)
    metadata_engine.to_json('output/metadata.json')
    with open('output/unichunks.json', 'w') as f:
        json.dump(chunker.get_chunks(), f, indent=2)
    print("Metadata and UniChunks saved to output/")

if __name__ == "__main__":
    main()
