"""Pydantic schemas for API validation and documentation."""

from pydantic import BaseModel, Field, EmailStr, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


# ============================================================================
# REMEDIATION AGENT SCHEMAS
# ============================================================================

class RemediationStrategy(BaseModel):
    """Single remediation strategy result."""
    agent_type: str = Field(..., description="Type: fungal, bacterial, crispr, hybrid")
    name: str = Field(..., description="Human-readable strategy name")
    effectiveness: float = Field(..., ge=0.0, le=1.0, description="Effectiveness score 0-1")
    timeline_days: int = Field(..., ge=1, description="Days to implement")
    cost_estimate: float = Field(..., ge=0, description="Estimated cost in EUR")
    risks: List[str] = Field(default_factory=list, description="Known risks")
    explanation: str = Field(..., description="AI-generated explanation")
    implementation_steps: List[str] = Field(default_factory=list)

    class Config:
        schema_extra = {
            "example": {
                "agent_type": "fungal_remediation",
                "name": "Mycoremediation using Pleurotus species",
                "effectiveness": 0.85,
                "timeline_days": 90,
                "cost_estimate": 50000,
                "risks": ["Seasonal sensitivity"],
                "explanation": "Pleurotus fungi excel at heavy metal degradation..."
            }
        }


class RemediationRequest(BaseModel):
    """Request to generate remediation plan."""
    pollution_description: str = Field(..., min_length=10, max_length=2000)
    site_type: str = Field(..., description="wastewater_treatment_plant, contaminated_land, etc")
    location: str = Field(..., min_length=2, max_length=255)
    budget_tier: str = Field(..., description="low, medium, high")
    deadline_months: Optional[int] = Field(None, ge=1, le=36)

    @validator('budget_tier')
    def validate_budget_tier(cls, v):
        if v not in ['low', 'medium', 'high']:
            raise ValueError('budget_tier must be low, medium, or high')
        return v

    class Config:
        schema_extra = {
            "example": {
                "pollution_description": "Heavy metals in wastewater, high nitrogen levels",
                "site_type": "wastewater_treatment_plant",
                "location": "EU-region-1",
                "budget_tier": "medium"
            }
        }


class RemediationResponse(BaseModel):
    """Response with generated remediation strategies."""
    strategies: List[RemediationStrategy]
    recommended_order: List[int] = Field(..., description="Indices of strategies in recommended order")
    total_timeline_days: int
    combined_cost: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# GOVERNANCE VOTING SCHEMAS
# ============================================================================

class VoterWeight(BaseModel):
    """Stakeholder voter with weight."""
    id: str = Field(..., description="Unique voter identifier")
    name: Optional[str] = Field(None, description="Voter organization name")
    weight: float = Field(..., ge=0.0, le=1.0, description="Voting weight/influence")

    class Config:
        schema_extra = {
            "example": {"id": "health_dept", "name": "Health Department", "weight": 0.3}
        }


class VotingVector(BaseModel):
    """Single voting dimension with score."""
    name: str = Field(..., description="Vector name: environmental_impact, health_benefit, etc")
    score: float = Field(..., ge=-1.0, le=1.0, description="Score for this vector")
    weight: Optional[float] = Field(None, ge=0.0, le=1.0, description="Vector weight (optional)")

    class Config:
        schema_extra = {
            "example": {
                "name": "environmental_impact",
                "score": 0.9,
                "weight": 0.35
            }
        }


class GovernanceVoteRequest(BaseModel):
    """Request to aggregate governance votes."""
    policy_id: str = Field(..., min_length=3, max_length=255, description="Unique policy identifier")
    policy_description: Optional[str] = Field(None, max_length=2000)
    voters: List[VoterWeight] = Field(..., min_items=1, max_items=50)
    vectors: List[VotingVector] = Field(..., min_items=1, max_items=20)
    context: Optional[str] = Field(None, max_length=1000, description="Additional context")

    @validator('voters')
    def validate_voter_weights(cls, v):
        total = sum(voter.weight for voter in v)
        if abs(total - 1.0) > 0.01:
            raise ValueError(f'Voter weights must sum to 1.0, got {total}')
        return v

    class Config:
        schema_extra = {
            "example": {
                "policy_id": "city-eco-001",
                "voters": [
                    {"id": "env_agency", "weight": 0.35},
                    {"id": "health_dept", "weight": 0.30}
                ],
                "vectors": [
                    {"name": "environmental_impact", "score": 0.9},
                    {"name": "health_benefit", "score": 0.85}
                ]
            }
        }


class GovernanceVoteResponse(BaseModel):
    """Response with aggregated voting results."""
    policy_id: str
    aggregate_score: float = Field(..., ge=-1.0, le=1.0, description="Weighted aggregate score")
    vector_breakdown: Dict[str, float] = Field(..., description="Score for each vector")
    voter_consensus: float = Field(..., ge=0.0, le=1.0, description="Consensus level")
    recommendation: str = Field(..., description="APPROVE, REJECT, NEEDS_REVIEW")
    explanation: str = Field(..., description="AI-generated policy explanation")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in recommendation")

    @validator('recommendation')
    def validate_recommendation(cls, v):
        if v not in ['APPROVE', 'REJECT', 'NEEDS_REVIEW']:
            raise ValueError('recommendation must be APPROVE, REJECT, or NEEDS_REVIEW')
        return v


# ============================================================================
# HEALTH & METRICS SCHEMAS
# ============================================================================

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: datetime
    version: str


class ReadinessResponse(BaseModel):
    """Readiness probe response."""
    status: str
    database: str
    timestamp: datetime
    services: Optional[Dict[str, str]] = None


# ============================================================================
# ERROR SCHEMAS
# ============================================================================

class ErrorDetail(BaseModel):
    """Error response detail."""
    detail: str
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ValidationError(BaseModel):
    """Validation error response."""
    detail: str
    field: str
    value: Any = None
