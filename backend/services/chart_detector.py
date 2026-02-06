"""
Chart Detection Service using YOLOv8
Detects charts, graphs, and tables in images
"""
from pathlib import Path
from typing import List, Dict, Any, Optional
from ultralytics import YOLO
from PIL import Image
import numpy as np

from config import YOLO_MODEL, CONFIDENCE_THRESHOLD


# Chart/graph class mappings for detection
# These are common classes that might indicate charts
CHART_KEYWORDS = {
    'chart', 'graph', 'plot', 'diagram', 'table', 'bar', 'pie', 'line'
}


class ChartDetector:
    """Detect charts and graphs in images using YOLOv8"""
    
    def __init__(self):
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load YOLOv8 model"""
        try:
            # Using YOLOv8 nano for faster inference
            # For chart detection, you may want to use a fine-tuned model
            self.model = YOLO(YOLO_MODEL)
        except Exception as e:
            print(f"Error loading YOLO model: {e}")
            self.model = None
    
    def detect(self, image_path: str) -> Dict[str, Any]:
        """
        Detect objects in image and classify if it's a chart
        
        Returns:
            Dict with detection results including:
            - is_chart: bool
            - chart_type: str (bar_chart, line_graph, pie_chart, table, image)
            - confidence: float
            - detections: list of detected objects
        """
        if not self.model:
            return self._fallback_detection(image_path)
        
        try:
            # Run inference
            results = self.model(image_path, verbose=False)
            
            detections = []
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    cls_id = int(box.cls[0])
                    conf = float(box.conf[0])
                    label = result.names[cls_id]
                    
                    detections.append({
                        "label": label,
                        "confidence": conf,
                        "bbox": box.xyxy[0].tolist()
                    })
            
            # Analyze if this is likely a chart based on image characteristics
            chart_analysis = self._analyze_chart_characteristics(image_path)
            
            return {
                "is_chart": chart_analysis["is_chart"],
                "chart_type": chart_analysis["chart_type"],
                "confidence": chart_analysis["confidence"],
                "detections": detections
            }
            
        except Exception as e:
            print(f"Error during detection: {e}")
            return self._fallback_detection(image_path)
    
    def _analyze_chart_characteristics(self, image_path: str) -> Dict[str, Any]:
        """
        Analyze image characteristics to determine if it's a chart
        Uses heuristics based on color distribution, lines, and patterns
        """
        try:
            img = Image.open(image_path)
            img_array = np.array(img.convert('RGB'))
            
            # Get image statistics
            height, width = img_array.shape[:2]
            aspect_ratio = width / height if height > 0 else 1
            
            # Count unique colors (charts typically have limited color palette)
            resized = img.resize((100, 100))
            colors = resized.getcolors(maxcolors=10000)
            unique_colors = len(colors) if colors else 0
            
            # Heuristics for chart detection
            # Charts typically have:
            # - Limited color palette (< 100 distinct colors in downsampled image)
            # - Regular aspect ratios
            # - Not too small (likely icons) or too large
            
            is_chart = False
            chart_type = "image"
            confidence = 0.3
            
            if unique_colors < 50 and 0.5 < aspect_ratio < 2.5:
                is_chart = True
                chart_type = "chart"  # Generic, will be refined by OCR
                confidence = 0.6
            elif unique_colors < 100 and 0.3 < aspect_ratio < 3.0:
                is_chart = True
                chart_type = "graph"
                confidence = 0.5
            
            # Check for table-like structure (many horizontal/vertical lines)
            gray = img.convert('L')
            gray_array = np.array(gray)
            
            # Simple edge detection for line detection
            edges_h = np.abs(np.diff(gray_array.astype(float), axis=0))
            edges_v = np.abs(np.diff(gray_array.astype(float), axis=1))
            
            h_lines = np.sum(edges_h > 50) / edges_h.size
            v_lines = np.sum(edges_v > 50) / edges_v.size
            
            if h_lines > 0.05 and v_lines > 0.05:
                is_chart = True
                chart_type = "table"
                confidence = 0.7
            
            return {
                "is_chart": is_chart,
                "chart_type": chart_type,
                "confidence": confidence
            }
            
        except Exception as e:
            print(f"Error analyzing image: {e}")
            return {"is_chart": False, "chart_type": "image", "confidence": 0.0}
    
    def _fallback_detection(self, image_path: str) -> Dict[str, Any]:
        """Fallback detection using image analysis only"""
        return self._analyze_chart_characteristics(image_path)


# Singleton instance
_detector: Optional[ChartDetector] = None


def get_chart_detector() -> ChartDetector:
    """Get or create chart detector instance"""
    global _detector
    if _detector is None:
        _detector = ChartDetector()
    return _detector


def detect_chart(image_path: str) -> Dict[str, Any]:
    """Detect if image is a chart and its type"""
    detector = get_chart_detector()
    return detector.detect(image_path)
