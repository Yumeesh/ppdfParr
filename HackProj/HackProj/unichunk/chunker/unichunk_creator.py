# UniChunk Creator
# Merges blocks into semantically meaningful UniChunks
import uuid

class UniChunkCreator:
    def __init__(self):
        self.chunks = []

    def create_chunk(self, content, chunk_type, elements, page_no, source):
        chunk = {
            'id': str(uuid.uuid4()),
            'content': content,
            'type': chunk_type,
            'elements': elements,
            'page_no': page_no,
            'source': source
        }
        self.chunks.append(chunk)
        return chunk

    def get_chunks(self):
        return self.chunks
