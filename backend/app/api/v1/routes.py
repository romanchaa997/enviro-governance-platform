"""API v1 routes for remediation and governance endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.app import schemas, models
from backend.app.database import SessionLocal
from backend.app.services import RemediationService, GovernanceService

router = APIRouter(prefix="/api/v1", tags=["v1"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/remediation/plan", response_model=schemas.RemediationPlanSchema)
async def create_remediation_plan(
    request: schemas.RemediationPlanSchema,
    db: Session = Depends(get_db)
):
    """Create a remediation plan for contaminated ecosystem."""
    service = RemediationService(db)
    return service.generate_plan(request)

@router.post("/governance/vote", response_model=schemas.VotingVectorSchema)
async def cast_governance_vote(
    vote: schemas.VotingVectorSchema,
    db: Session = Depends(get_db)
):
    """Cast a multi-vector governance vote."""
    service = GovernanceService(db)
    return service.record_vote(vote)
