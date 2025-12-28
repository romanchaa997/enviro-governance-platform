"""PoC Agent for bio-remediation strategy recommendations."""

import logging
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ContaminationType(str, Enum):
    HEAVY_METALS = "heavy_metals"
    ORGANIC_POLLUTANTS = "organic_pollutants"
    MICROPLASTICS = "microplastics"
    RADIOACTIVE = "radioactive"
    PERSISTENT_ORGANICS = "persistent_organics"

class RemediationTechnique(str, Enum):
    PHYTOREMEDIATION = "phytoremediation"
    MYCOREMEDIATION = "mycoremediation"
    BIOREMEDIATION = "bioremediation"
    CRISPR_ENGINEERING = "crispr_engineering"
    BACTERIAL_CONSORTIUM = "bacterial_consortium"

@dataclass
class RemediationStrategy:
    technique: RemediationTechnique
    effectiveness: float
    timeline: str
    cost_estimate: str
    risks: List[str]
    biodiversity_impact: str

class RemediationAgent:
    """Agent that recommends bio-remediation strategies based on contamination analysis."""
    
    STRATEGIES_DB = {
        ContaminationType.HEAVY_METALS: [
            RemediationStrategy(
                technique=RemediationTechnique.PHYTOREMEDIATION,
                effectiveness=0.75,
                timeline="12-24 months",
                cost_estimate="Low",
                risks=["Weather dependency", "Slow processing"],
                biodiversity_impact="Positive"
            ),
            RemediationStrategy(
                technique=RemediationTechnique.MYCOREMEDIATION,
                effectiveness=0.85,
                timeline="6-12 months",
                cost_estimate="Medium",
                risks=["Fungal management", "pH sensitivity"],
                biodiversity_impact="Very positive"
            ),
        ]
    }
    
    @classmethod
    def analyze_contamination(cls, description: str, contamination_type: str) -> Dict[str, Any]:
        """Analyze contamination and recommend strategies."""
        try:
            cont_type = ContaminationType(contamination_type.lower())
            strategies = cls.STRATEGIES_DB.get(cont_type, [])
            
            return {
                "status": "success",
                "contamination_type": cont_type.value,
                "strategies": [
                    {
                        "technique": s.technique.value,
                        "effectiveness": s.effectiveness,
                        "timeline": s.timeline,
                        "cost": s.cost_estimate,
                        "biodiversity_impact": s.biodiversity_impact,
                        "risks": s.risks
                    } for s in strategies
                ]
            }
        except Exception as e:
            logger.error(f"Error analyzing contamination: {e}")
            return {"status": "error", "message": str(e)}
    
    @classmethod
    def recommend_best_strategy(cls, contamination_type: str, priority: str = "effectiveness") -> Dict[str, Any]:
        """Recommend the best remediation strategy based on priority."""
        cont_type = ContaminationType(contamination_type.lower())
        strategies = cls.STRATEGIES_DB.get(cont_type, [])
        
        if priority == "cost":
            best = min(strategies, key=lambda s: s.cost_estimate)
        else:  # effectiveness
            best = max(strategies, key=lambda s: s.effectiveness)
        
        return {
            "recommended_technique": best.technique.value,
            "effectiveness": best.effectiveness,
            "timeline": best.timeline,
            "cost": best.cost_estimate,
            "rationale": f"Selected based on {priority}"
        }
