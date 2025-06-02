# Metadata Engine
# Creates unified JSON metadata for each element
import json

class MetadataEngine:
    def __init__(self):
        self.metadata = []

    def add_element(self, page_no, element_type, bbox, source, extra=None):
        entry = {
            'page_no': page_no,
            'type': element_type,
            'bbox': bbox,
            'source': source
        }
        if extra:
            entry.update(extra)
        self.metadata.append(entry)

    def to_json(self, out_path):
        with open(out_path, 'w') as f:
            json.dump(self.metadata, f, indent=2)
