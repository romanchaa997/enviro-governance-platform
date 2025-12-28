"""Governance service - multi-vector voting and decision aggregation."""

import logging
from typing import List, Dict, Optional
from datetime import datetime
from statistics import mean, stdev

from sqlalchemy.orm import Session
from app.models import Decision, VotingVector
from app.schemas import (
    VoterWeight, VotingVector as VectorSchema,
    GovernanceVoteResponse
)

logger = logging.getLogger(__name__)


class GovernanceService:
    """Service for multi-vector governance voting and consensus building."""

    async def aggregate_votes(
        self,
        policy_id: str,
        voters: List[VoterWeight],
        vectors: List[VectorSchema],
        db: Session
    ) -> GovernanceVoteResponse:
        """Aggregate multi-vector votes using weighted consensus."""
        logger.info(f"Aggregating votes for policy {policy_id}")
        
        # Calculate aggregate score
        aggregate_score = self._calculate_aggregate_score(vectors)
        
        # Calculate vector breakdown
        vector_breakdown = {v.name: v.score for v in vectors}
        
        # Calculate voter consensus
        voter_consensus = self._calculate_consensus(vectors, voters)
        
        # Generate recommendation
        recommendation = self._generate_recommendation(aggregate_score, voter_consensus)
        
        # Generate explanation
        explanation = self._generate_explanation(
            policy_id, vectors, aggregate_score, voter_consensus
        )
        
        return GovernanceVoteResponse(
            policy_id=policy_id,
            aggregate_score=aggregate_score,
            vector_breakdown=vector_breakdown,
            voter_consensus=voter_consensus,
            recommendation=recommendation,
            explanation=explanation,
            timestamp=datetime.utcnow(),
            confidence=min(0.95, 0.5 + (voter_consensus * 0.45))
        )

    def _calculate_aggregate_score(self, vectors: List[VectorSchema]) -> float:
        """Calculate weighted aggregate score from voting vectors."""
        if not vectors:
            return 0.0
        
        # If vectors have individual weights, use them; otherwise equal weight
        has_weights = any(v.weight is not None for v in vectors)
        
        if has_weights:
            total_weight = sum(v.weight or 1.0 for v in vectors)
            weighted_sum = sum((v.score * (v.weight or 1.0)) for v in vectors)
            return weighted_sum / total_weight if total_weight > 0 else 0.0
        else:
            # Equal weight for all vectors
            return mean([v.score for v in vectors]) if vectors else 0.0
    
    def _calculate_consensus(self, vectors: List[VectorSchema], voters: List[VoterWeight]) -> float:
        """Calculate voter consensus level (0-1)."""
        if len(vectors) < 2:
            return 1.0  # Perfect consensus with one vector
        
        scores = [v.score for v in vectors]
        # Calculate normalized standard deviation
        # Lower std = higher consensus
        avg = mean(scores)
        if avg == 0:
            return 1.0
        
        try:
            std = stdev(scores) if len(scores) > 1 else 0
            # Normalize to 0-1 where 1 is perfect consensus
            consensus = max(0, 1 - (std / 2))  # Max std of ~2 gives 0 consensus
            return round(consensus, 3)
        except:
            return 0.5
    
    def _generate_recommendation(self, aggregate_score: float, consensus: float) -> str:
        """Generate policy recommendation based on scores."""
        # Require both high score and good consensus
        if aggregate_score > 0.6 and consensus > 0.6:
            return "APPROVE"
        elif aggregate_score < -0.4 or consensus < 0.3:
            return "REJECT"
        else:
            return "NEEDS_REVIEW"
    
    def _generate_explanation(self, policy_id: str, vectors: List[VectorSchema], 
                             aggregate_score: float, consensus: float) -> str:
        """Generate AI explanation of voting decision."""
        # Find strongest and weakest vectors
        strongest = max(vectors, key=lambda v: v.score) if vectors else None
        weakest = min(vectors, key=lambda v: v.score) if vectors else None
        
        explanation = f"Policy {policy_id} analyzed across {len(vectors)} dimensions. "
        
        if strongest:
            explanation += f"Strongest support: {strongest.name} (score: {strongest.score}). "
        
        if weakest:
            explanation += f"Weakest area: {weakest.name} (score: {weakest.score}). "
        
        explanation += f"Overall consensus level: {consensus * 100:.0f}% with aggregate score of {aggregate_score:.2f} on scale -1 to +1. "
        
        # Add contextual interpretation
        if aggregate_score > 0.7:
            explanation += "Strong policy alignment across stakeholders. "
        elif aggregate_score > 0.3:
            explanation += "Moderate support with some concerns. "
        elif aggregate_score > -0.3:
            explanation += "Mixed feedback requires further deliberation. "
        else:
            explanation += "Significant concerns raised by stakeholders. "
        
        explanation += "Recommendation based on multi-vector analysis and stakeholder weights."
        
        return explanation
