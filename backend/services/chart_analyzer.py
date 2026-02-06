"""
Chart Analyzer Service using Pix2Struct
Deep understanding of chart content and structure
"""
from pathlib import Path
from typing import Dict, Any, Optional
from PIL import Image

# Transformers import with fallback
try:
    from transformers import Pix2StructProcessor, Pix2StructForConditionalGeneration
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("Transformers not available for Pix2Struct")


class ChartAnalyzer:
    """Analyze charts using Pix2Struct model"""
    
    MODEL_NAME = "google/pix2struct-chartqa-base"
    
    def __init__(self):
        self.processor = None
        self.model = None
        self.device = "cuda" if self._check_cuda() else "cpu"
        
    def _check_cuda(self) -> bool:
        """Check if CUDA is available"""
        try:
            import torch
            return torch.cuda.is_available()
        except:
            return False
    
    def _load_model(self):
        """Lazy load the model"""
        if not TRANSFORMERS_AVAILABLE:
            return False
            
        if self.processor is None:
            try:
                self.processor = Pix2StructProcessor.from_pretrained(self.MODEL_NAME)
                self.model = Pix2StructForConditionalGeneration.from_pretrained(self.MODEL_NAME)
                self.model.to(self.device)
                return True
            except Exception as e:
                print(f"Error loading Pix2Struct model: {e}")
                return False
        return True
    
    def analyze(self, image_path: str, questions: list = None) -> Dict[str, Any]:
        """
        Analyze chart using Pix2Struct
        
        Args:
            image_path: Path to chart image
            questions: Optional list of questions to ask about the chart
            
        Returns:
            Dict with answers to questions or descriptions
        """
        if questions is None:
            questions = [
                "What is the title of this chart?",
                "What does the x-axis represent?",
                "What does the y-axis represent?",
                "What is the maximum value shown?",
                "What is the minimum value shown?",
                "What trend does this chart show?"
            ]
        
        if not self._load_model():
            return self._fallback_analysis()
        
        try:
            image = Image.open(image_path).convert("RGB")
            results = {}
            
            for question in questions:
                inputs = self.processor(
                    images=image,
                    text=question,
                    return_tensors="pt"
                ).to(self.device)
                
                with torch.no_grad():
                    predictions = self.model.generate(**inputs, max_new_tokens=50)
                
                answer = self.processor.decode(predictions[0], skip_special_tokens=True)
                results[question] = answer
            
            return {
                "success": True,
                "answers": results
            }
            
        except Exception as e:
            print(f"Chart analysis error: {e}")
            return self._fallback_analysis()
    
    def _fallback_analysis(self) -> Dict[str, Any]:
        """Fallback when model is not available"""
        return {
            "success": False,
            "answers": {},
            "message": "Pix2Struct model not available"
        }


# Singleton
_analyzer: Optional[ChartAnalyzer] = None


def get_chart_analyzer() -> ChartAnalyzer:
    """Get or create chart analyzer instance"""
    global _analyzer
    if _analyzer is None:
        _analyzer = ChartAnalyzer()
    return _analyzer


def analyze_chart(image_path: str, questions: list = None) -> Dict[str, Any]:
    """Analyze chart image"""
    analyzer = get_chart_analyzer()
    return analyzer.analyze(image_path, questions)
