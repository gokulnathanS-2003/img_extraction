"""
OCR Service using PaddleOCR
Extracts text from charts and graphs
"""
from pathlib import Path
from typing import Dict, Any, List, Optional
from PIL import Image
import numpy as np

# PaddleOCR import with fallback
try:
    from paddleocr import PaddleOCR
    PADDLE_AVAILABLE = True
except ImportError:
    PADDLE_AVAILABLE = False
    print("PaddleOCR not available, using fallback")


class OCRService:
    """Extract text from images using PaddleOCR"""
    
    def __init__(self):
        self.ocr = None
        if PADDLE_AVAILABLE:
            try:
                # Initialize PaddleOCR with English
                self.ocr = PaddleOCR(
                    use_angle_cls=True,
                    lang='en',
                    show_log=False
                )
            except Exception as e:
                print(f"Error initializing PaddleOCR: {e}")
    
    def extract_text(self, image_path: str) -> Dict[str, Any]:
        """
        Extract all text from image
        
        Returns:
            Dict with:
            - raw_text: list of all extracted text
            - boxes: list of bounding boxes and text
            - structured: attempt to structure into axis/legend/values
        """
        if not self.ocr:
            return self._empty_result()
        
        try:
            result = self.ocr.ocr(image_path, cls=True)
            
            if not result or not result[0]:
                return self._empty_result()
            
            texts = []
            boxes = []
            
            for line in result[0]:
                box = line[0]
                text = line[1][0]
                confidence = line[1][1]
                
                texts.append(text)
                boxes.append({
                    "text": text,
                    "confidence": confidence,
                    "bbox": box,
                    "y_center": (box[0][1] + box[2][1]) / 2,
                    "x_center": (box[0][0] + box[2][0]) / 2
                })
            
            # Attempt to structure the extracted text
            structured = self._structure_chart_text(boxes)
            
            return {
                "raw_text": texts,
                "boxes": boxes,
                "structured": structured
            }
            
        except Exception as e:
            print(f"OCR error: {e}")
            return self._empty_result()
    
    def _structure_chart_text(self, boxes: List[Dict]) -> Dict[str, Any]:
        """
        Attempt to structure extracted text into chart components
        Uses position heuristics to identify:
        - Title (usually top center)
        - X-axis label (bottom center)
        - Y-axis label (left side, possibly rotated)
        - Values (numbers in data area)
        - Legend (right side or bottom)
        """
        if not boxes:
            return {
                "title": None,
                "x_axis": None,
                "y_axis": None,
                "values": [],
                "legends": []
            }
        
        # Sort by position
        sorted_by_y = sorted(boxes, key=lambda x: x["y_center"])
        sorted_by_x = sorted(boxes, key=lambda x: x["x_center"])
        
        # Get image bounds
        all_y = [b["y_center"] for b in boxes]
        all_x = [b["x_center"] for b in boxes]
        
        min_y, max_y = min(all_y), max(all_y)
        min_x, max_x = min(all_x), max(all_x)
        
        y_range = max_y - min_y if max_y > min_y else 1
        x_range = max_x - min_x if max_x > min_x else 1
        
        title = None
        x_axis = None
        y_axis = None
        values = []
        legends = []
        
        for box in boxes:
            text = box["text"].strip()
            y_pos = (box["y_center"] - min_y) / y_range if y_range > 0 else 0.5
            x_pos = (box["x_center"] - min_x) / x_range if x_range > 0 else 0.5
            
            # Title: top 20% of image, centered
            if y_pos < 0.2 and 0.3 < x_pos < 0.7:
                if title is None or len(text) > len(title):
                    title = text
            
            # X-axis: bottom 20%, centered
            elif y_pos > 0.8 and 0.3 < x_pos < 0.7:
                if x_axis is None or len(text) > len(x_axis):
                    x_axis = text
            
            # Y-axis: left 15%, middle area
            elif x_pos < 0.15 and 0.2 < y_pos < 0.8:
                if y_axis is None or len(text) > len(y_axis):
                    y_axis = text
            
            # Check if it's a number (likely a value)
            elif self._is_numeric(text):
                values.append(text)
            
            # Legend: right side or bottom right
            elif x_pos > 0.7 or (y_pos > 0.7 and x_pos > 0.5):
                legends.append(text)
        
        return {
            "title": title,
            "x_axis": x_axis,
            "y_axis": y_axis,
            "values": values,
            "legends": legends
        }
    
    def _is_numeric(self, text: str) -> bool:
        """Check if text is numeric (including formatted numbers)"""
        cleaned = text.replace(',', '').replace('%', '').replace('$', '').replace('-', '').strip()
        try:
            float(cleaned)
            return True
        except ValueError:
            return False
    
    def _empty_result(self) -> Dict[str, Any]:
        """Return empty result structure"""
        return {
            "raw_text": [],
            "boxes": [],
            "structured": {
                "title": None,
                "x_axis": None,
                "y_axis": None,
                "values": [],
                "legends": []
            }
        }


# Singleton instance
_ocr_service: Optional[OCRService] = None


def get_ocr_service() -> OCRService:
    """Get or create OCR service instance"""
    global _ocr_service
    if _ocr_service is None:
        _ocr_service = OCRService()
    return _ocr_service


def extract_chart_text(image_path: str) -> Dict[str, Any]:
    """Extract and structure text from chart image"""
    service = get_ocr_service()
    return service.extract_text(image_path)
