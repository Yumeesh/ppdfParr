# PDF Ingestion & Classification
# Loads PDF, corrects orientation, classifies as digital or scanned

try:
    import fitz  # PyMuPDF
except ModuleNotFoundError:
    import subprocess
    import sys
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pymupdf'])
    import fitz

try:
    import pytesseract
except ModuleNotFoundError:
    import subprocess
    import sys
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pytesseract'])
    import pytesseract

try:
    from pdf2image import convert_from_path
except ModuleNotFoundError:
    import subprocess
    import sys
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pdf2image'])
    from pdf2image import convert_from_path

try:
    import spacy
except ModuleNotFoundError:
    import subprocess
    import sys
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'spacy'])
    import spacy

from PIL import Image
import numpy as np
import cv2
import os

try:
    nlp = spacy.load("en_core_web_sm")
except:
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'spacy', 'download', 'en_core_web_sm'])
    nlp = spacy.load("en_core_web_sm")

class PDFIngestor:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)

    def is_scanned(self, page):
        # Try to extract text; if little or none, treat as scanned
        text = page.get_text().strip()
        return len(text) < 20

    def correct_orientation(self, image):
        # Use pytesseract to detect orientation
        try:
            osd = pytesseract.image_to_osd(image)
            rotate = int([line for line in osd.split('\n') if 'Rotate:' in line][0].split(':')[1])
            if rotate != 0:
                image = image.rotate(360 - rotate, expand=True)
        except Exception:
            pass
        return image

    def extract_text_spacy(self, text):
        doc = nlp(text)
        return doc.text

    def extract_pages(self):
        results = []
        for i, page in enumerate(self.doc):
            if self.is_scanned(page):
                # Convert to image for OCR
                images = convert_from_path(self.pdf_path, first_page=i+1, last_page=i+1, dpi=300)
                image = images[0]
                image = self.correct_orientation(image)
                # Use pytesseract for OCR, then spaCy for text processing
                raw_text = pytesseract.image_to_string(image)
                processed_text = self.extract_text_spacy(raw_text)
                results.append({'type': 'scanned', 'page_no': i+1, 'text': processed_text})
            else:
                text = page.get_text()
                processed_text = self.extract_text_spacy(text)
                results.append({'type': 'digital', 'page_no': i+1, 'text': processed_text})
        return results
