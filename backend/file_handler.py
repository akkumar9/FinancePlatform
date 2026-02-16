import os
import shutil
from pathlib import Path
from typing import Optional
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import uuid

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

class FileHandler:
    @staticmethod
    async def save_file(file, case_id: str) -> dict:
        """Save uploaded file and extract text"""
        file_id = str(uuid.uuid4())
        file_extension = Path(file.filename).suffix
        filename = f"{file_id}{file_extension}"
        file_path = UPLOAD_DIR / case_id
        file_path.mkdir(exist_ok=True)
        
        full_path = file_path / filename
        
        # Save file
        with open(full_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Extract text based on file type
        extracted_text = None
        file_type = file.content_type
        
        try:
            if "image" in file_type:
                extracted_text = FileHandler.extract_text_from_image(full_path)
            elif "pdf" in file_type:
                extracted_text = FileHandler.extract_text_from_pdf(full_path)
            elif "text" in file_type:
                with open(full_path, 'r') as f:
                    extracted_text = f.read()
        except Exception as e:
            print(f"Error extracting text: {e}")
            extracted_text = f"Could not extract text: {str(e)}"
        
        return {
            "id": file_id,
            "filename": file.filename,
            "file_path": str(full_path),
            "file_type": file_type,
            "extracted_text": extracted_text
        }
    
    @staticmethod
    def extract_text_from_image(image_path: Path) -> str:
        """Extract text from image using OCR"""
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            return f"OCR failed: {str(e)}"
    
    @staticmethod
    def extract_text_from_pdf(pdf_path: Path) -> str:
        """Extract text from PDF"""
        try:
            # Convert PDF to images
            images = convert_from_path(pdf_path, first_page=1, last_page=3)  # limit to first 3 pages
            text = ""
            for image in images:
                text += pytesseract.image_to_string(image) + "\n\n"
            return text
        except Exception as e:
            return f"PDF extraction failed: {str(e)}"

file_handler = FileHandler()
