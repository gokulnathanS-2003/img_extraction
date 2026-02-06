"""
Pydantic models for request/response schemas
"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class OCRData(BaseModel):
    """OCR extracted data from chart/graph"""
    title: Optional[str] = None
    x_axis: Optional[str] = None
    y_axis: Optional[str] = None
    values: List[Dict[str, Any]] = []
    legends: List[str] = []


class InferenceResult(BaseModel):
    """LLM generated inference"""
    trend: Optional[str] = None
    max_point: Optional[Dict[str, Any]] = None
    min_point: Optional[Dict[str, Any]] = None
    correlations: List[str] = []
    anomalies: List[str] = []
    summary: str = ""


class ImageExtraction(BaseModel):
    """Single extracted image with analysis"""
    image_id: str
    image_path: str
    type: str  # bar_chart, line_graph, pie_chart, table, image
    page_number: int
    ocr_data: Optional[OCRData] = None
    inference: Optional[InferenceResult] = None


class PDFExtractionResult(BaseModel):
    """Complete PDF extraction result"""
    pdf_name: str
    processed_at: datetime
    total_pages: int
    extracted_text: str
    extractions: List[ImageExtraction] = []


class ProcessingStatus(BaseModel):
    """Processing status response"""
    status: str  # processing, completed, failed
    message: str
    progress: int = 0
    result: Optional[PDFExtractionResult] = None
