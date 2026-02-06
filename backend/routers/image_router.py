"""
Image Processing Router
API endpoints for standalone image upload and processing
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from pathlib import Path
from datetime import datetime
import uuid
import shutil

from models.schemas import (
    PDFExtractionResult,
    ImageExtraction,
    OCRData,
    InferenceResult,
    ProcessingStatus
)
from services.chart_detector import detect_chart
from services.ocr_service import extract_chart_text
from services.chart_analyzer import analyze_chart
from services.inference_service import generate_chart_inference
from services.json_storage import save_result, get_result
from utils.file_utils import save_upload_file, is_allowed_file, save_image
from config import OUTPUT_DIR, IMAGES_DIR


router = APIRouter(prefix="/api/image", tags=["Image Processing"])

# Reuse the same processing status tracker
# In a production app, use Redis or a database
from routers.pdf_router import processing_status


@router.post("/upload")
async def upload_image(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """
    Upload a standalone image for processing
    Returns a task ID to track processing status
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Check extension
    ext = Path(file.filename).suffix.lower()
    if ext not in {'.png', '.jpg', '.jpeg', '.gif', '.bmp'}:
        raise HTTPException(status_code=400, detail="Only image files are allowed")
    
    # Save file
    content = await file.read()
    file_path = await save_upload_file(content, file.filename)
    
    # Generate task ID
    task_id = uuid.uuid4().hex
    
    # Initialize status
    processing_status[task_id] = {
        "status": "processing",
        "message": "Image uploaded, starting analysis...",
        "progress": 0,
        "result": None
    }
    
    # Start background processing
    background_tasks.add_task(
        process_image,
        task_id,
        file_path,
        file.filename
    )
    
    return {"task_id": task_id, "message": "Image uploaded successfully, processing started"}


async def process_image(task_id: str, file_path: Path, filename: str):
    """Background task to process standalone image"""
    try:
        processing_status[task_id]["message"] = "Analyzing image content..."
        processing_status[task_id]["progress"] = 20
        
        # Determine image ID
        image_id = uuid.uuid4().hex
        ext = file_path.suffix.lstrip(".")
        
        # Copy to images directory for serving
        target_path = IMAGES_DIR / f"{image_id}.{ext}"
        shutil.copy2(file_path, target_path)
        
        # Detect if it's a chart
        detection = detect_chart(str(target_path))
        
        image_extractions = []
        
        if detection["is_chart"]:
            processing_status[task_id]["message"] = "Chart detected, running OCR and analysis..."
            processing_status[task_id]["progress"] = 50
            
            # Extract text using OCR
            ocr_result = extract_chart_text(str(target_path))
            
            # Generate inference (no PDF context available)
            inference = generate_chart_inference(
                str(target_path),
                detection["chart_type"],
                ocr_result,
                context=""
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
                image_id=image_id,
                image_path=str(target_path),
                type=detection["chart_type"],
                page_number=1,
                bbox=[],
                ocr_data=ocr_data,
                inference=inference_result
            ))
        else:
            processing_status[task_id]["message"] = "Processing as generic image..."
            # It's a regular image, but user might want OCR anyway
            pass 
        
        # Even if not a chart, we still return it as an "extraction" so frontend can display it
        if not image_extractions:
             image_extractions.append(ImageExtraction(
                image_id=image_id,
                image_path=str(target_path),
                type="image",
                page_number=1,
                bbox=[],
                ocr_data=None,
                inference=None
            ))
            
        # Build final result (wrapping in PDFExtractionResult for backward compatibility)
        result = PDFExtractionResult(
            pdf_name=filename,
            processed_at=datetime.now(),
            total_pages=1,
            extracted_text="",
            extractions=image_extractions
        )
        
        # Save to JSON
        processing_status[task_id]["message"] = "Saving results..."
        processing_status[task_id]["progress"] = 90
        
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
