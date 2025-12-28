# Governance Multi-Vector Voting Schema

## Overview
The Enviro-Governance Platform implements a sophisticated multi-vector voting system that enables stakeholders to participate in environmental decision-making through multiple weighted dimensions. This schema supports democratic governance while accommodating different stakeholder perspectives and expertise levels.

## Core Voting Vectors

### 1. Democratic Vote (Single-Citizen-One-Vote)
**Weight Factor:** 0.30 (30%)
**Description:** Standard democratic voting mechanism where each registered citizen has one vote per decision.

```python
class DemocraticVote(BaseModel):
    voter_id: str
    decision_id: str
    vote: Literal['yes', 'no', 'abstain']
    timestamp: datetime
    ipfs_hash: str  # Blockchain verification
    signature: str  # Cryptographic signature
```

**Calculation:**
```
democratic_score = (yes_votes - no_votes) / total_votes * 0.30
```

### 2. Expert Consensus (Domain-Weighted Voting)
**Weight Factor:** 0.35 (35%)
**Description:** Weighted voting from certified experts with domain expertise in environmental science, climate, biodiversity, and sustainability.

```python
class ExpertVote(BaseModel):
    expert_id: str
    expertise_domain: Literal['climate', 'biodiversity', 'sustainability', 'water_systems', 'soil_science']
    expert_level: Literal['level_1', 'level_2', 'level_3']  # 1=Bachelors, 2=Masters, 3=PhD
    vote: Literal['yes', 'no', 'abstain']
    confidence_score: float  # 0.0 to 1.0
    justification: str
    peer_review_count: int
    timestamp: datetime
```

**Weight Multipliers:**
- Level 1: 1.0x
- Level 2: 1.5x
- Level 3: 2.0x
- Confidence: vote_weight * confidence_score

**Calculation:**
```
expert_score = sum(expert_votes * level_multiplier * confidence) / total_expert_votes * 0.35
```

### 3. Community Impact Score (Stakeholder-Weighted)
**Weight Factor:** 0.20 (20%)
**Description:** Direct stakeholders (affected communities, local organizations) vote with impact weighting based on proximity and demographic exposure.

```python
class CommunityImpactVote(BaseModel):
    community_id: str
    stakeholder_category: Literal['local_resident', 'indigenous_community', 'local_org', 'business_impacted']
    distance_from_project_km: float
    population_affected: int
    vote: Literal['yes', 'no', 'abstain']
    affected_sectors: List[str]  # agriculture, fishing, tourism, health, etc.
    impact_severity: Literal['low', 'medium', 'high', 'critical']
    timestamp: datetime
```

**Impact Multipliers:**
- Local Resident: 1.0x (distance-based decay: -0.05x per 10km beyond 50km)
- Indigenous Community: 1.5x
- Local Organization: 0.8x
- Business Impacted: 0.6x
- Impact Severity: low=0.8x, medium=1.0x, high=1.2x, critical=1.5x

**Calculation:**
```
affected_weight = base_multiplier * impact_multiplier * distance_decay_factor
impact_score = sum(community_votes * affected_weight) / total_stakeholders * 0.20
```

### 4. Environmental Data Integration (AI-Verified)
**Weight Factor:** 0.15 (15%)
**Description:** Algorithmic consensus based on scientific data analysis, environmental modeling, and sensor networks.

```python
class EnvironmentalDataVote(BaseModel):
    data_source_id: str
    data_type: Literal['sensor_network', 'satellite_imagery', 'ml_model', 'blockchain_verified']
    confidence_interval: Tuple[float, float]  # 95% CI
    recommendation: Literal['support', 'oppose', 'neutral']
    supporting_datasets: List[str]
    verification_method: str
    timestamp: datetime
    peer_verified: bool
    peer_reviewer_count: int
```

**Calculation:**
```
data_score = (support_count - oppose_count) / total_data_sources * 0.15
final_data_weight = data_score * avg_confidence_interval * peer_verification_boost
```

## Final Decision Algorithm

```python
def calculate_final_vote_score(decision_id: str) -> VoteResult:
    democratic = get_democratic_score(decision_id)      # 0.30
    expert = get_expert_score(decision_id)              # 0.35
    community = get_community_score(decision_id)        # 0.20
    environmental = get_environmental_score(decision_id) # 0.15
    
    final_score = (
        democratic * 0.30 +
        expert * 0.35 +
        community * 0.20 +
        environmental * 0.15
    )
    
    # Threshold: > 0.5 = Approve, < 0.5 = Reject, == 0.5 = Stalemate
    decision = 'APPROVED' if final_score > 0.5 else 'REJECTED' if final_score < 0.5 else 'STALEMATE'
    
    return VoteResult(
        decision_id=decision_id,
        final_score=final_score,
        decision=decision,
        component_scores={
            'democratic': democratic,
            'expert': expert,
            'community': community,
            'environmental': environmental
        },
        timestamp=datetime.now(),
        on_chain_hash=blockchain_hash(final_score)
    )
```

## Database Schema (PostgreSQL)

```sql
-- Main Voting Table
CREATE TABLE voting_decisions (
    id UUID PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    decision_category VARCHAR(100),
    voting_start_date TIMESTAMP NOT NULL,
    voting_end_date TIMESTAMP NOT NULL,
    final_score DECIMAL(5,4),
    decision_status VARCHAR(50),
    ipfs_hash VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Democratic Votes
CREATE TABLE democratic_votes (
    id UUID PRIMARY KEY,
    decision_id UUID NOT NULL REFERENCES voting_decisions(id),
    voter_id VARCHAR(255) NOT NULL,
    vote VARCHAR(10) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ipfs_hash VARCHAR(100),
    signature VARCHAR(255),
    UNIQUE(decision_id, voter_id)
);

-- Expert Votes
CREATE TABLE expert_votes (
    id UUID PRIMARY KEY,
    decision_id UUID NOT NULL REFERENCES voting_decisions(id),
    expert_id VARCHAR(255) NOT NULL,
    expertise_domain VARCHAR(100) NOT NULL,
    expert_level VARCHAR(20) NOT NULL,
    vote VARCHAR(10) NOT NULL,
    confidence_score DECIMAL(3,2),
    justification TEXT,
    peer_review_count INT DEFAULT 0,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Community Impact Votes
CREATE TABLE community_impact_votes (
    id UUID PRIMARY KEY,
    decision_id UUID NOT NULL REFERENCES voting_decisions(id),
    community_id VARCHAR(255) NOT NULL,
    stakeholder_category VARCHAR(100) NOT NULL,
    distance_from_project_km DECIMAL(8,2),
    population_affected INT,
    vote VARCHAR(10) NOT NULL,
    affected_sectors TEXT ARRAY,
    impact_severity VARCHAR(20),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Environmental Data Votes
CREATE TABLE environmental_data_votes (
    id UUID PRIMARY KEY,
    decision_id UUID NOT NULL REFERENCES voting_decisions(id),
    data_source_id VARCHAR(255) NOT NULL,
    data_type VARCHAR(100) NOT NULL,
    confidence_lower DECIMAL(5,4),
    confidence_upper DECIMAL(5,4),
    recommendation VARCHAR(20),
    supporting_datasets TEXT ARRAY,
    verification_method TEXT,
    peer_verified BOOLEAN,
    peer_reviewer_count INT DEFAULT 0,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Vote Aggregation Cache
CREATE TABLE vote_aggregation_cache (
    id UUID PRIMARY KEY,
    decision_id UUID NOT NULL UNIQUE REFERENCES voting_decisions(id),
    democratic_score DECIMAL(5,4),
    expert_score DECIMAL(5,4),
    community_score DECIMAL(5,4),
    environmental_score DECIMAL(5,4),
    final_score DECIMAL(5,4),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Security & Verification Mechanisms

### Blockchain Integration
- All final vote hashes stored on Ethereum (optimized chain)
- Smart contract verification of vote totals
- Immutable audit trail

### Vote Integrity
- Cryptographic signatures for all votes
- Zero-knowledge proofs for voter privacy
- Duplicate vote prevention via voter ID hashing
- Time-locked voting windows

### Anti-Manipulation
- Sybil attack prevention via identity verification
- Vote timing analysis to detect coordinated voting
- Outlier detection for unusual voting patterns
- Automatic flagging for peer review

## Implementation Example (FastAPI)

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import hashlib

router = APIRouter(prefix="/api/v1/voting")

@router.post("/cast-vote")
async def cast_vote(
    vote_data: DemocraticVote,
    db: Session = Depends(get_db)
):
    # Verify voter hasn't already voted
    existing = db.query(DemocraticVotes).filter(
        DemocraticVotes.decision_id == vote_data.decision_id,
        DemocraticVotes.voter_id == vote_data.voter_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=409, detail="Duplicate vote attempt")
    
    # Verify voting window
    decision = db.query(VotingDecision).filter(
        VotingDecision.id == vote_data.decision_id
    ).first()
    
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")
    
    if datetime.now() > decision.voting_end_date:
        raise HTTPException(status_code=400, detail="Voting window closed")
    
    # Store vote
    vote = DemocraticVotes(
        decision_id=vote_data.decision_id,
        voter_id=vote_data.voter_id,
        vote=vote_data.vote,
        timestamp=datetime.now(),
        signature=vote_data.signature
    )
    
    db.add(vote)
    db.commit()
    
    return {"status": "success", "vote_id": str(vote.id)}

@router.get("/decision/{decision_id}/results")
async def get_vote_results(decision_id: str, db: Session = Depends(get_db)):
    # Calculate final score
    result = calculate_final_vote_score(decision_id)
    return result
```

## Performance Optimizations

1. **Vote Aggregation Caching**: Pre-calculated scores updated incrementally
2. **Index Strategy**:
   - decision_id + voter_id on democratic_votes
   - decision_id + timestamp on all vote tables
   - Partial indexes for active decisions only
3. **Batch Processing**: Aggregate scores every 5 minutes or 1000 votes
4. **Read Replicas**: Voting counts distributed across read-only replicas

## Future Enhancements

1. **Liquid Democracy**: Allow vote delegation to trusted representatives
2. **Quadratic Voting**: Enable voters to allocate variable vote strength
3. **Temporal Weighting**: Recent votes weighted more heavily for emerging issues
4. **API Integration**: Real-time data feeds from environmental sensors
5. **ML Model Integration**: Predictive environmental impact scoring
6. **Cross-chain Voting**: Multi-chain consensus for global decisions
