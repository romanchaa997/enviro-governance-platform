"""Utility functions for the application."""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import json

logger = logging.getLogger(__name__)

class RemediationAgent:
    """PoC agent for recommending bio-remediation strategies."""
    
    @staticmethod
    def analyze_contamination(description: str) -> Dict[str, Any]:
        """Analyze contamination description and recommend strategies."""
        return {
            "contamination_type": "heavy_metals",
            "severity": "high",
            "strategies": [
                {"name": "Phytoremediation", "effectiveness": 0.75, "timeline": "12-24 months"},
                {"name": "Mycoremediation", "effectiveness": 0.85, "timeline": "6-12 months"},
                {"name": "Bioremediation", "effectiveness": 0.90, "timeline": "3-6 months"}
            ],
            "risks": ["Slow processing", "Weather dependency", "Regulatory compliance"]
        }

class VotingEngine:
    """Multi-vector voting system for governance decisions."""
    
    VECTORS = ["environment", "health", "economy", "speed"]
    
    @staticmethod
    def calculate_consensus(votes: list) -> Dict[str, float]:
        """Calculate multi-vector consensus from stakeholder votes."""
        return {
            "environment": 0.85,
            "health": 0.78,
            "economy": 0.65,
            "speed": 0.72,
            "overall_consensus": 0.75
        }

def format_timestamp(dt: Optional[datetime] = None) -> str:
    """Format datetime for API responses."""
    if dt is None:
        dt = datetime.utcnow()
    return dt.isoformat() + "Z"

def create_success_response(data: Any, message: str = "Success") -> Dict[str, Any]:
    """Create standardized success response."""
    return {
        "status": "success",
        "message": message,
        "data": data,
        "timestamp": format_timestamp()
    }
