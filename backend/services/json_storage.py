"""
JSON Storage Service
Saves extraction results to JSON file
"""
import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

from config import OUTPUT_DIR


class JSONStorage:
    """Store and manage extraction results in JSON format"""
    
    def __init__(self):
        self.results_file = OUTPUT_DIR / "results.json"
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Create results file if it doesn't exist"""
        if not self.results_file.exists():
            self._write_data({"extractions": []})
    
    def _read_data(self) -> Dict[str, Any]:
        """Read existing data from file"""
        try:
            with open(self.results_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {"extractions": []}
    
    def _write_data(self, data: Dict[str, Any]):
        """Write data to file"""
        with open(self.results_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
    
    def save_extraction(self, result: Dict[str, Any]) -> str:
        """
        Save a new extraction result
        
        Args:
            result: Extraction result dict
            
        Returns:
            ID of the saved extraction
        """
        data = self._read_data()
        
        # Add timestamp and ID
        extraction_id = f"extraction_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        result["extraction_id"] = extraction_id
        result["saved_at"] = datetime.now().isoformat()
        
        data["extractions"].append(result)
        self._write_data(data)
        
        return extraction_id
    
    def get_extraction(self, extraction_id: str) -> Dict[str, Any]:
        """Get a specific extraction by ID"""
        data = self._read_data()
        
        for extraction in data["extractions"]:
            if extraction.get("extraction_id") == extraction_id:
                return extraction
        
        return None
    
    def get_all_extractions(self) -> List[Dict[str, Any]]:
        """Get all saved extractions"""
        data = self._read_data()
        return data.get("extractions", [])
    
    def get_latest_extraction(self) -> Dict[str, Any]:
        """Get the most recent extraction"""
        extractions = self.get_all_extractions()
        if extractions:
            return extractions[-1]
        return None
    
    def clear_all(self):
        """Clear all saved extractions"""
        self._write_data({"extractions": []})


# Singleton
_storage = None


def get_json_storage() -> JSONStorage:
    """Get or create JSON storage instance"""
    global _storage
    if _storage is None:
        _storage = JSONStorage()
    return _storage


def save_result(result: Dict[str, Any]) -> str:
    """Save extraction result to JSON"""
    storage = get_json_storage()
    return storage.save_extraction(result)


def get_result(extraction_id: str) -> Dict[str, Any]:
    """Get extraction result by ID"""
    storage = get_json_storage()
    return storage.get_extraction(extraction_id)


def get_all_results() -> List[Dict[str, Any]]:
    """Get all extraction results"""
    storage = get_json_storage()
    return storage.get_all_extractions()
