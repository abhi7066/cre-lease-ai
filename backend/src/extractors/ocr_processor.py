"""
OCR processor using fitz (PyMuPDF) + Tesseract
Works without needing Poppler or pdf2image
"""

import os
import pytesseract
from pathlib import Path
from typing import Optional, Tuple
from ..config.settings import Settings
from ..utils.logger import get_logger

# Set Tesseract path
if os.path.exists(Settings.TESSERACT_PATH):
    pytesseract.pytesseract.tesseract_cmd = Settings.TESSERACT_PATH

logger = get_logger(__name__)


class OCRProcessor:
    """Handles OCR extraction from PDF documents"""
    
    def __init__(self):
        """Initialize OCR processor"""
        self.logger = get_logger(__name__)
        if not os.path.exists(Settings.TESSERACT_PATH):
            raise RuntimeError(f"Tesseract not found at: {Settings.TESSERACT_PATH}")
    
    def extract_text(self, pdf_path: str) -> str:
        """
        Extract text from PDF using fitz (PyMuPDF) + Tesseract OCR.
        Works for both digital and scanned PDFs.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text content
        """
        import fitz
        
        self.logger.info(f"Opening PDF: {pdf_path}")
        pdf = fitz.open(pdf_path)
        page_count = len(pdf)
        self.logger.info(f"PDF has {page_count} page(s)")
        
        all_text = []
        
        for i in range(page_count):
            page = pdf[i]
            
            # Try direct text extraction first
            text = page.get_text()
            if text and len(text.strip()) > 50:
                self.logger.debug(f"Page {i+1}/{page_count}: Direct text extraction ({len(text)} chars)")
                all_text.append(text)
                continue
            
            # If no text, use OCR
            self.logger.info(f"Page {i+1}/{page_count}: Using OCR...")
            try:
                # Render page as image with configured DPI
                pix = page.get_pixmap(
                    matrix=fitz.Matrix(Settings.OCR_DPI_SCALE, Settings.OCR_DPI_SCALE)
                )
                
                # Convert to PIL Image for pytesseract
                from PIL import Image
                img_data = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                
                # OCR the image
                text = pytesseract.image_to_string(img_data, lang=Settings.OCR_LANGUAGE)
                if text and text.strip():
                    all_text.append(text)
                    self.logger.debug(f"Page {i+1}/{page_count}: OCR successful ({len(text)} chars)")
                else:
                    self.logger.warning(f"Page {i+1}/{page_count}: No text detected")
            except Exception as e:
                self.logger.error(f"Page {i+1}/{page_count}: OCR failed - {e}")
        
        pdf.close()
        
        if not all_text:
            raise ValueError("No text extracted from PDF")
        
        extracted = "\n\n".join(all_text)
        self.logger.info(f"Total extracted: {len(extracted)} characters")
        return extracted
    
    def process_file(self, pdf_path: Path, output_path: Optional[Path] = None) -> Tuple[str, Optional[Path]]:
        """
        Extract text from a single PDF and optionally save to file.
        
        Args:
            pdf_path: Path to PDF file
            output_path: Optional path to save extracted text
            
        Returns:
            Tuple of (extracted_text, output_file_path)
        """
        try:
            text = self.extract_text(str(pdf_path))
            
            if output_path:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_text(text, encoding="utf-8")
                self.logger.info(f"Saved raw text: {output_path}")
                return text, output_path
            
            return text, None
            
        except Exception as e:
            self.logger.error(f"Failed to process {pdf_path}: {e}")
            raise



if __name__ == "__main__":
    process_all_pdfs("leases", "process")
