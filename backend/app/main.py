"""FastAPI application entry point for enviro-governance-platform."""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from datetime import datetime
from typing import Optional, List

from sqlalchemy.orm import Session

# Import routers and schemas (will be created)
from app.schemas import (
    RemediationRequest,
    RemediationResponse,
    GovernanceVoteRequest,
    GovernanceVoteResponse,
)
from app.services.remediation_service import RemediationService
from app.services.governance_service import GovernanceService
from app.database import get_db, engine, Base

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Enviro-Governance Platform API",
    description="AI-driven environmental remediation with multi-stakeholder governance",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure per environment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
remediation_service = RemediationService()
governance_service = GovernanceService()


# Health check endpoints
@app.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


@app.get("/ready")
async def readiness_check(db: Session = Depends(get_db)):
    """Readiness probe - includes database check."""
    try:
        # Test database connection
        db.execute("SELECT 1")
        return {
            "status": "ready",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service unavailable")


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    # Will be implemented with prometheus_client
    return {"message": "Metrics endpoint - to be implemented"}


# ============================================================================
# REMEDIATION AGENT ENDPOINTS
# ============================================================================

@app.post("/v1/remediation/plan", response_model=RemediationResponse)
async def create_remediation_plan(
    request: RemediationRequest,
    db: Session = Depends(get_db)
):
    """Generate remediation strategies for environmental contamination.
    
    Args:
        request: RemediationRequest with pollution description, site type, location, budget tier
        db: Database session
    
    Returns:
        RemediationResponse with list of strategies, recommended order, timeline
    
    Example:
        {
            "pollution_description": "Heavy metals and nitrogen in wastewater",
            "site_type": "wastewater_treatment_plant",
            "location": "EU-region-1",
            "budget_tier": "medium"
        }
    """
    try:
        # Validate input
        if not request.pollution_description or len(request.pollution_description) < 10:
            raise HTTPException(
                status_code=400,
                detail="Pollution description must be at least 10 characters"
            )
        
        # Generate remediation strategies
        response = await remediation_service.generate_strategies(
            pollution_description=request.pollution_description,
            site_type=request.site_type,
            location=request.location,
            budget_tier=request.budget_tier,
            db=db
        )
        
        logger.info(f"Remediation plan created for {request.site_type} in {request.location}")
        return response
        
    except Exception as e:
        logger.error(f"Error creating remediation plan: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# GOVERNANCE VOTING ENDPOINTS
# ============================================================================

@app.post("/v1/governance/vote", response_model=GovernanceVoteResponse)
async def submit_governance_vote(
    request: GovernanceVoteRequest,
    db: Session = Depends(get_db)
):
    """Submit and aggregate multi-vector governance votes.
    
    Args:
        request: GovernanceVoteRequest with policy, voters, vectors
        db: Database session
    
    Returns:
        GovernanceVoteResponse with aggregate score, vector breakdown, recommendation
    
    Example:
        {
            "policy_id": "city-eco-001",
            "voters": [
                {"id": "health_dept", "weight": 0.3},
                {"id": "environment_agency", "weight": 0.35}
            ],
            "vectors": [
                {"name": "environmental_impact", "score": 0.9},
                {"name": "health_benefit", "score": 0.85}
            ]
        }
    """
    try:
        # Validate weights sum to 1.0
        total_weight = sum(v.weight for v in request.voters)
        if abs(total_weight - 1.0) > 0.01:  # Allow small floating point errors
            raise HTTPException(
                status_code=400,
                detail=f"Voter weights must sum to 1.0, got {total_weight}"
            )
        
        # Aggregate votes
        response = await governance_service.aggregate_votes(
            policy_id=request.policy_id,
            voters=request.voters,
            vectors=request.vectors,
            db=db
        )
        
        logger.info(f"Governance vote aggregated for policy {request.policy_id}")
        return response
        
    except Exception as e:
        logger.error(f"Error aggregating governance votes: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint with API documentation links."""
    return {
        "message": "Enviro-Governance Platform API v1.0.0",
        "documentation": "/docs",
        "redoc": "/redoc",
        "health": "/health",
        "endpoints": {
            "remediation": "/v1/remediation/plan",
            "governance": "/v1/governance/vote"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
