# Tesseract OCR for lab report images
import pytesseract
from PIL import Image

def perform_ocr(image_path: str):
    return pytesseract.image_to_string(Image.open(image_path))
