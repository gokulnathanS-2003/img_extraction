"""
Inference Service using Google Gemini
Generates detailed analysis and insights from chart data
"""
from typing import Dict, Any, Optional
import google.generativeai as genai
from pathlib import Path

from config import GEMINI_API_KEY


class InferenceService:
    """Generate insights using LLM"""
    
    def __init__(self):
        self.model = None
        self._initialize()
    
    def _initialize(self):
        """Initialize Gemini API"""
        if not GEMINI_API_KEY:
            print("Warning: GEMINI_API_KEY not set")
            return
            
        try:
            genai.configure(api_key=GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-pro')
        except Exception as e:
            print(f"Error initializing Gemini: {e}")
    
    def generate_inference(
        self,
        image_path: str,
        chart_type: str,
        ocr_data: Dict[str, Any],
        pdf_context: str = ""
    ) -> Dict[str, Any]:
        """
        Generate detailed inference about a chart
        
        Args:
            image_path: Path to chart image
            chart_type: Type of chart (bar_chart, line_graph, etc.)
            ocr_data: Extracted text data from OCR
            pdf_context: Surrounding text context from PDF
            
        Returns:
            Dict with inference results
        """
        if not self.model:
            return self._fallback_inference(ocr_data)
        
        try:
            # Build prompt
            prompt = self._build_prompt(chart_type, ocr_data, pdf_context)
            
            # Generate response
            response = self.model.generate_content(prompt)
            
            # Parse response into structured format
            return self._parse_response(response.text, ocr_data)
            
        except Exception as e:
            print(f"Inference error: {e}")
            return self._fallback_inference(ocr_data)
    
    def _build_prompt(
        self,
        chart_type: str,
        ocr_data: Dict[str, Any],
        pdf_context: str
    ) -> str:
        """Build the prompt for LLM"""
        structured = ocr_data.get("structured", {})
        
        prompt = f"""Analyze this {chart_type} and provide detailed insights.

Chart Information:
- Title: {structured.get('title', 'Unknown')}
- X-Axis: {structured.get('x_axis', 'Unknown')}
- Y-Axis: {structured.get('y_axis', 'Unknown')}
- Values Found: {', '.join(structured.get('values', [])[:20])}
- Legend Items: {', '.join(structured.get('legends', []))}

Context from Document:
{pdf_context[:1000] if pdf_context else 'No additional context available'}

Please provide a comprehensive analysis including:
1. **TREND**: Is the data showing an increasing, decreasing, stable, or fluctuating trend?
2. **MAX_POINT**: What appears to be the maximum value and what does it represent?
3. **MIN_POINT**: What appears to be the minimum value and what does it represent?
4. **CORRELATIONS**: Any notable correlations or relationships in the data?
5. **ANOMALIES**: Any outliers or unusual patterns?
6. **SUMMARY**: A detailed paragraph explaining what this chart shows, its significance, and key takeaways.

Format your response clearly with each section labeled."""

        return prompt
    
    def _parse_response(self, response_text: str, ocr_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse LLM response into structured format"""
        result = {
            "trend": None,
            "max_point": None,
            "min_point": None,
            "correlations": [],
            "anomalies": [],
            "summary": response_text
        }
        
        # Try to extract structured data from response
        lines = response_text.split('\n')
        current_section = None
        
        for line in lines:
            line_lower = line.lower().strip()
            
            if 'trend' in line_lower and ':' in line:
                result["trend"] = line.split(':', 1)[1].strip()
            elif 'max' in line_lower and ':' in line:
                result["max_point"] = {"description": line.split(':', 1)[1].strip()}
            elif 'min' in line_lower and ':' in line:
                result["min_point"] = {"description": line.split(':', 1)[1].strip()}
            elif 'correlation' in line_lower and ':' in line:
                result["correlations"].append(line.split(':', 1)[1].strip())
            elif 'anomal' in line_lower and ':' in line:
                result["anomalies"].append(line.split(':', 1)[1].strip())
            elif 'summary' in line_lower and ':' in line:
                result["summary"] = line.split(':', 1)[1].strip()
        
        return result
    
    def _fallback_inference(self, ocr_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate basic inference without LLM"""
        structured = ocr_data.get("structured", {})
        values = structured.get("values", [])
        
        # Try to extract numeric values
        numeric_values = []
        for v in values:
            try:
                cleaned = v.replace(',', '').replace('%', '').replace('$', '')
                numeric_values.append(float(cleaned))
            except:
                pass
        
        trend = "unknown"
        max_point = None
        min_point = None
        
        if len(numeric_values) >= 2:
            if numeric_values[-1] > numeric_values[0]:
                trend = "increasing"
            elif numeric_values[-1] < numeric_values[0]:
                trend = "decreasing"
            else:
                trend = "stable"
            
            max_val = max(numeric_values)
            min_val = min(numeric_values)
            max_point = {"value": max_val, "label": str(max_val)}
            min_point = {"value": min_val, "label": str(min_val)}
        
        return {
            "trend": trend,
            "max_point": max_point,
            "min_point": min_point,
            "correlations": [],
            "anomalies": [],
            "summary": f"Chart with title '{structured.get('title', 'Unknown')}' showing {len(values)} data points. Trend appears to be {trend}."
        }


# Singleton
_service: Optional[InferenceService] = None


def get_inference_service() -> InferenceService:
    """Get or create inference service"""
    global _service
    if _service is None:
        _service = InferenceService()
    return _service


def generate_chart_inference(
    image_path: str,
    chart_type: str,
    ocr_data: Dict[str, Any],
    pdf_context: str = ""
) -> Dict[str, Any]:
    """Generate inference for chart"""
    service = get_inference_service()
    return service.generate_inference(image_path, chart_type, ocr_data, pdf_context)
