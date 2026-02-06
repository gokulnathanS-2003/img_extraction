"""
PDF Extraction & Chart Analysis Backend
FastAPI Application Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from routers.pdf_router import router as pdf_router
from routers.image_router import router as image_router
from config import CORS_ORIGINS, OUTPUT_DIR, IMAGES_DIR


# Create FastAPI app
app = FastAPI(
    title="PDF Chart Extraction API",
    description="Extract and analyze charts, graphs, and tables from PDF documents",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for images
app.mount("/static/images", StaticFiles(directory=str(IMAGES_DIR)), name="images")

# Include routers
app.include_router(pdf_router)
app.include_router(image_router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "PDF Chart Extraction API",
        "docs": "/docs",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
