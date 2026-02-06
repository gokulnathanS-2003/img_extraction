"""
PDF Extraction Service using PyMuPDF
Extracts text and images from PDF files
"""
import fitz  # PyMuPDF
from pathlib import Path
from typing import List, Tuple, Dict, Any
import uuid

from utils.file_utils import save_image
from config import IMAGES_DIR


class PDFExtractor:
    """Extract text and images from PDF files"""
    
    def __init__(self, pdf_path: Path):
        self.pdf_path = pdf_path
        self.doc = None
        
    def __enter__(self):
        self.doc = fitz.open(self.pdf_path)
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.doc:
            self.doc.close()
    
    def get_total_pages(self) -> int:
        """Get total number of pages in PDF"""
        return len(self.doc) if self.doc else 0
    
    def extract_text(self) -> str:
        """Extract all text from PDF"""
        if not self.doc:
            return ""
        
        full_text = []
        for page_num in range(len(self.doc)):
            page = self.doc[page_num]
            text = page.get_text()
            if text.strip():
                full_text.append(f"--- Page {page_num + 1} ---\n{text}")
        
        return "\n\n".join(full_text)
    
    def extract_images(self) -> List[Dict[str, Any]]:
        """
        Extract all images from PDF
        Returns list of dicts with image info
        """
        if not self.doc:
            return []
        
        images = []
        
        for page_num in range(len(self.doc)):
            page = self.doc[page_num]
            image_list = page.get_images(full=True)
            
            for img_index, img in enumerate(image_list):
                xref = img[0]
                
                try:
                    # Extract image bytes
                    base_image = self.doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    
                    # Generate unique ID and save
                    image_id = f"img_{page_num + 1}_{img_index + 1}_{uuid.uuid4().hex[:8]}"
                    image_path = save_image(image_bytes, image_id, image_ext)
                    
                    images.append({
                        "image_id": image_id,
                        "image_path": str(image_path),
                        "page_number": page_num + 1,
                        "width": base_image.get("width", 0),
                        "height": base_image.get("height", 0),
                        "extension": image_ext
                    })
                    
                except Exception as e:
                    print(f"Error extracting image {xref} from page {page_num + 1}: {e}")
                    continue
        
        return images
    
    def extract_page_as_image(self, page_num: int, zoom: float = 2.0) -> Tuple[bytes, str]:
        """
        Render a PDF page as an image
        Useful for capturing charts that aren't embedded as images
        """
        if not self.doc or page_num >= len(self.doc):
            return b"", ""
        
        page = self.doc[page_num]
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        
        image_id = f"page_{page_num + 1}_{uuid.uuid4().hex[:8]}"
        image_bytes = pix.tobytes("png")
        
        return image_bytes, image_id


def extract_pdf(pdf_path: Path) -> Dict[str, Any]:
    """
    Main function to extract all content from PDF
    """
    with PDFExtractor(pdf_path) as extractor:
        return {
            "total_pages": extractor.get_total_pages(),
            "text": extractor.extract_text(),
            "images": extractor.extract_images()
        }
