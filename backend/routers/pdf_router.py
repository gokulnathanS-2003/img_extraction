"""
PDF Processing Router
API endpoints for PDF upload and processing
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pathlib import Path
from datetime import datetime
from typing import List
import uuid

from models.schemas import (
    PDFExtractionResult,
    ImageExtraction,
    OCRData,
    InferenceResult,
    ProcessingStatus
)
from services.pdf_extractor import extract_pdf
from services.chart_detector import detect_chart
from services.ocr_service import extract_chart_text
from services.chart_analyzer import analyze_chart
from services.inference_service import generate_chart_inference
from services.json_storage import save_result, get_result, get_all_results
from utils.file_utils import save_upload_file, is_allowed_file
from config import OUTPUT_DIR, IMAGES_DIR


router = APIRouter(prefix="/api/pdf", tags=["PDF Processing"])

# In-memory processing status
processing_status = {}


@router.post("/upload")
async def upload_pdf(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """
    Upload a PDF file for processing
    Returns a task ID to track processing status
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    if not is_allowed_file(file.filename):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Save file
    content = await file.read()
    file_path = await save_upload_file(content, file.filename)
    
    # Generate task ID
    task_id = uuid.uuid4().hex
    
    # Initialize status
    processing_status[task_id] = {
        "status": "processing",
        "message": "PDF uploaded, starting extraction...",
        "progress": 0,
        "result": None
    }
    
    # Start background processing
    background_tasks.add_task(
        process_pdf,
        task_id,
        file_path,
        file.filename
    )
    
    return {"task_id": task_id, "message": "PDF uploaded successfully, processing started"}


async def process_pdf(task_id: str, file_path: Path, filename: str):
    """Background task to process PDF"""
    try:
        # Step 1: Extract PDF content
        processing_status[task_id]["message"] = "Extracting text and images from PDF..."
        processing_status[task_id]["progress"] = 10
        
        extraction = extract_pdf(file_path)
        
        processing_status[task_id]["progress"] = 30
        processing_status[task_id]["message"] = f"Found {len(extraction['images'])} images, analyzing..."
        
        # Step 2: Process each image
        image_extractions = []
        total_images = len(extraction["images"])
        
        for idx, img_info in enumerate(extraction["images"]):
            image_path = img_info["image_path"]
            
            # Detect if it's a chart
            detection = detect_chart(image_path)
            
            if detection["is_chart"]:
                processing_status[task_id]["message"] = f"Analyzing chart {idx + 1}/{total_images}..."
                
                # Extract text using OCR
                ocr_result = extract_chart_text(image_path)
                
                # Get context from PDF text
                page_num = img_info["page_number"]
                context = extraction["text"][:2000]  # Use first 2000 chars as context
                
                # Generate inference
                inference = generate_chart_inference(
                    image_path,
                    detection["chart_type"],
                    ocr_result,
                    context
                )
                
                # Build structured data
                ocr_data = OCRData(
                    title=ocr_result["structured"].get("title"),
                    x_axis=ocr_result["structured"].get("x_axis"),
                    y_axis=ocr_result["structured"].get("y_axis"),
                    values=[{"value": v} for v in ocr_result["structured"].get("values", [])],
                    legends=ocr_result["structured"].get("legends", [])
                )
                
                inference_result = InferenceResult(
                    trend=inference.get("trend"),
                    max_point=inference.get("max_point"),
                    min_point=inference.get("min_point"),
                    correlations=inference.get("correlations", []),
                    anomalies=inference.get("anomalies", []),
                    summary=inference.get("summary", "")
                )
                
                image_extractions.append(ImageExtraction(
                    image_id=img_info["image_id"],
                    image_path=image_path,
                    type=detection["chart_type"],
                    page_number=page_num,
                    ocr_data=ocr_data,
                    inference=inference_result
                ))
            else:
                # Store as regular image
                image_extractions.append(ImageExtraction(
                    image_id=img_info["image_id"],
                    image_path=image_path,
                    type="image",
                    page_number=img_info["page_number"],
                    ocr_data=None,
                    inference=None
                ))
            
            # Update progress
            progress = 30 + int((idx + 1) / total_images * 60)
            processing_status[task_id]["progress"] = progress
        
        # Step 3: Build final result
        result = PDFExtractionResult(
            pdf_name=filename,
            processed_at=datetime.now(),
            total_pages=extraction["total_pages"],
            extracted_text=extraction["text"],
            extractions=image_extractions
        )
        
        # Step 4: Save to JSON
        processing_status[task_id]["message"] = "Saving results..."
        processing_status[task_id]["progress"] = 95
        
        saved_id = save_result(result.model_dump())
        
        # Complete
        processing_status[task_id] = {
            "status": "completed",
            "message": "Processing complete",
            "progress": 100,
            "result": result.model_dump(),
            "extraction_id": saved_id
        }
        
    except Exception as e:
        processing_status[task_id] = {
            "status": "failed",
            "message": f"Error: {str(e)}",
            "progress": 0,
            "result": None
        }


@router.get("/status/{task_id}")
async def get_processing_status(task_id: str):
    """Get the processing status of a PDF"""
    if task_id not in processing_status:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return processing_status[task_id]


@router.get("/results")
async def get_all_extraction_results():
    """Get all saved extraction results"""
    return get_all_results()


@router.get("/results/{extraction_id}")
async def get_extraction_result(extraction_id: str):
    """Get a specific extraction result"""
    result = get_result(extraction_id)
    if not result:
        raise HTTPException(status_code=404, detail="Extraction not found")
    return result


@router.get("/images/{image_id}")
async def get_image(image_id: str):
    """Get an extracted image by ID"""
    # Look for image with any extension
    for ext in ["png", "jpg", "jpeg", "gif", "bmp"]:
        image_path = IMAGES_DIR / f"{image_id}.{ext}"
        if image_path.exists():
            return FileResponse(image_path)
    
    raise HTTPException(status_code=404, detail="Image not found")
