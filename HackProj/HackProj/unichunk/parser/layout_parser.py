# Layout Parsing & Content Element Detection
# For digital: use pdfplumber; for scanned: use OpenCV

import pdfplumber
import cv2
import numpy as np

class LayoutParser:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path

    def parse_digital(self, page):
        # Use pdfplumber to extract text, tables, images
        elements = []
        with pdfplumber.open(self.pdf_path) as pdf:
            p = pdf.pages[page]
            # Text blocks
            for block in p.extract_words():
                bbox = block.get('bbox') if 'bbox' in block else [block.get('x0'), block.get('top'), block.get('x1'), block.get('bottom')]
                elements.append({'type': 'text', 'bbox': bbox, 'text': block.get('text', '')})
            # Tables
            for table in p.extract_tables():
                elements.append({'type': 'table', 'data': table})
            # Images
            for img in p.images:
                elements.append({'type': 'image', 'bbox': img.get('bbox')})
        return elements

    def parse_scanned(self, image):
        # Use OpenCV to detect contours, etc.
        elements = []
        img = np.array(image)
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        _, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            if w*h > 1000:
                elements.append({'type': 'block', 'bbox': [x, y, x+w, y+h]})
        return elements
