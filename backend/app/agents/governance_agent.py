"""Multi-vector Governance Agent for transparent decision-making."""

import logging
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum
import statistics

logger = logging.getLogger(__name__)

class GovernanceVector(str, Enum):
    ENVIRONMENT = "environment"
    HEALTH = "health"
    ECONOMY = "economy"
    SPEED = "speed"

@dataclass
class StakeholderVote:
    stakeholder_id: str
    environment_score: float  # 0-1
    health_score: float  # 0-1
    economy_score: float  # 0-1
    speed_score: float  # 0-1
    rationale: str

class GovernanceAgent:
    """Agent for managing multi-vector governance voting and consensus."""
    
    VECTORS = [GovernanceVector.ENVIRONMENT, GovernanceVector.HEALTH,
               GovernanceVector.ECONOMY, GovernanceVector.SPEED]
    
    @classmethod
    def record_vote(cls, vote: Dict[str, Any]) -> Dict[str, Any]:
        """Record a multi-vector stakeholder vote."""
        try:
            return {
                "status": "success",
                "vote_id": f"vote_{hash(str(vote))}",
                "vectors": {
                    "environment": vote.get("environment", 0.5),
                    "health": vote.get("health", 0.5),
                    "economy": vote.get("economy", 0.5),
                    "speed": vote.get("speed", 0.5)
                },
                "timestamp": "2025-12-28T15:00:00Z"
            }
        except Exception as e:
            logger.error(f"Error recording vote: {e}")
            return {"status": "error", "message": str(e)}
    
    @classmethod
    def calculate_consensus(cls, votes: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate consensus from multiple stakeholder votes."""
        if not votes:
            return {v.value: 0.5 for v in cls.VECTORS}
        
        env_scores = [v.get("environment", 0.5) for v in votes]
        health_scores = [v.get("health", 0.5) for v in votes]
        econ_scores = [v.get("economy", 0.5) for v in votes]
        speed_scores = [v.get("speed", 0.5) for v in votes]
        
        return {
            "environment": statistics.mean(env_scores),
            "health": statistics.mean(health_scores),
            "economy": statistics.mean(econ_scores),
            "speed": statistics.mean(speed_scores),
            "overall_consensus": statistics.mean(
                env_scores + health_scores + econ_scores + speed_scores
            )
        }
    
    @classmethod
    def recommend_policy(cls, consensus: Dict[str, float]) -> Dict[str, Any]:
        """Recommend environmental policy based on consensus."""
        if consensus["overall_consensus"] >= 0.75:
            recommendation = "STRONGLY RECOMMENDED"
        elif consensus["overall_consensus"] >= 0.65:
            recommendation = "RECOMMENDED"
        elif consensus["overall_consensus"] >= 0.5:
            recommendation = "REQUIRES REVISION"
        else:
            recommendation = "NOT RECOMMENDED"
        
        return {
            "recommendation": recommendation,
            "consensus_scores": consensus,
            "key_concern": min(consensus.items(), key=lambda x: x[1] if x[0] != "overall_consensus" else 1)[0]
        }
