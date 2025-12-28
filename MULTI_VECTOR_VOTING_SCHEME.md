# Multi-Vector Voting Scheme: Technical Documentation

## Executive Summary

The Enviro-Governance Platform implements a sophisticated **multi-vector voting and consensus mechanism** designed to aggregate decisions from multiple stakeholder perspectives across environmental governance domains. This scheme enables transparent, multi-stakeholder decision-making while maintaining explainability and fairness.

## 1. Core Voting Architecture

### 1.1 Voting Vectors

Voting vectors represent independent decision dimensions, each capturing a distinct stakeholder perspective or evaluation criterion:

```
Vector = {
    name: str,                # e.g., "environmental_impact", "cost_effectiveness"
    description: str,         # Detailed explanation of the vector
    score: float [-1.0, 1.0], # -1: Strongly against, 0: Neutral, +1: Strongly for
    weight: float [0, 1.0],  # Relative importance (optional, defaults to equal)
    metadata: dict            # Context-specific data
}
```

### 1.2 Voter Weights

Each stakeholder (voter) is assigned a weight reflecting their expertise and constituency:

```
Voter = {
    id: str,              # Unique identifier
    name: str,            # Full stakeholder name
    weight: float [0,1.0] # Voting power (all weights sum to 1.0)
}
```

## 2. Aggregation Algorithm

### 2.1 Weighted Aggregate Score

The primary decision metric combines all vector scores with optional weights:

```
Aggregate Score = Σ(Vector_i × Weight_i) / Σ(Weight_i)
Range: [-1.0, +1.0]
```

**Interpretation:**
- **+1.0**: Unanimous strong approval
- **+0.6 to +1.0**: Clear approval
- **-0.4 to +0.6**: Mixed sentiment (needs review)
- **-1.0 to -0.4**: Clear rejection
- **-1.0**: Unanimous strong disapproval

### 2.2 Consensus Measurement

Consensus quantifies stakeholder agreement across voting vectors:

```
Consensus = max(0, 1 - (StdDev(scores) / 2))
Range: [0.0, 1.0]
```

Where:
- **1.0 (100%)**: Perfect agreement across all vectors
- **0.6-0.99 (60-99%)**: Strong consensus with minor dissent
- **0.3-0.59 (30-59%)**: Weak consensus, significant disagreement
- **0.0-0.29 (0-29%)**: Consensus absent, major divisions

## 3. Decision Recommendation Matrix

Final policy recommendations are determined by both aggregate score AND consensus:

| Aggregate Score | Consensus | Recommendation | Action |
|---|---|---|---|
| > +0.6 | > 0.6 | **APPROVE** | Implementation |
| +0.3 to +0.6 | > 0.6 | NEEDS_REVIEW | Further deliberation |
| -0.4 to +0.3 | Any | NEEDS_REVIEW | Committee discussion |
| < -0.4 | Any | **REJECT** | Alternative proposals |
| Any | < 0.3 | NEEDS_REVIEW | Stakeholder reconciliation |

## 4. Explainability Layer

Every decision is accompanied by an AI-generated explanation:

```
Explanation = {
    policy_id: str,
    strongest_vector: str,      # Highest scoring dimension
    weakest_vector: str,        # Lowest scoring dimension
    consensus_interpretation: str,
    aggregate_interpretation: str,
    recommendation_rationale: str,
    dissenting_voices: list,    # Vectors with significant divergence
    suggested_modifications: list  # Areas for improvement
}
```

## 5. Real-World Example: WWTP Policy Decision

### Policy: "Implement CRISPR-based remediation for nitrogen removal"

**Voters:**
- Environmental Agency (0.35 weight)
- Public Health Department (0.3 weight)
- Municipal Budget Committee (0.2 weight)
- Civil Society Organizations (0.15 weight)

**Voting Vectors:**

| Vector | Score | Description |
|---|---|---|
| Environmental Impact | +0.95 | 95% effectiveness, ecosystem benefits |
| Health Benefits | +0.80 | Reduces nitrogen pollutants, respiratory health |
| Cost Effectiveness | -0.60 | High capital costs, extended ROI timeline |
| Public Acceptance | -0.30 | GMO concerns, public perception risks |
| Regulatory Compliance | +0.70 | Meets new EU water directives |
| Long-term Sustainability | +0.85 | Self-reproducing organisms, minimal maintenance |

**Calculation:**
```
Aggregate = (0.95×0.35 + 0.80×0.3 - 0.60×0.2 - 0.30×0.15 + 0.70 + 0.85) / 6
          = (0.3325 + 0.24 - 0.12 - 0.045 + 0.70 + 0.85) / 6
          = 1.9575 / 6
          = +0.53 (MIXED SENTIMENT)

Scores: [0.95, 0.80, -0.60, -0.30, 0.70, 0.85]
StdDev = 0.71
Consensus = 1 - (0.71/2) = 0.645 (GOOD)

Recommendation: NEEDS_REVIEW (Good consensus but mixed aggregate)
```

**Generated Explanation:**
"Policy shows strong environmental benefits (environmental impact: 0.95, sustainability: 0.85) and regulatory alignment, but cost concerns and public acceptance risks require mitigation. With 64.5% stakeholder consensus, propose phased pilot program in controlled district with public engagement campaign before full deployment."

## 6. Database Schema

### VotingVector Table
```sql
CREATE TABLE voting_vectors (
    id UUID PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description VARCHAR(500),
    range_min FLOAT DEFAULT -1.0,
    range_max FLOAT DEFAULT 1.0,
    default_weight FLOAT DEFAULT 1.0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### Decision Table (voting_data JSON)
```sql
CREATE TABLE decisions (
    id UUID PRIMARY KEY,
    policy_id VARCHAR(255) UNIQUE NOT NULL,
    policy_description VARCHAR(2000),
    voting_data JSONB NOT NULL, -- {"voters": [...], "vectors": [...]}
    aggregate_score FLOAT NOT NULL,
    vector_breakdown JSONB NOT NULL, -- {"vector_name": score, ...}
    voter_consensus FLOAT NOT NULL,
    recommendation VARCHAR(50) NOT NULL, -- APPROVE, REJECT, NEEDS_REVIEW
    explanation TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    audit_log_id UUID REFERENCES audit_logs(id),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

## 7. API Endpoints

### Submit Governance Vote
```
POST /v1/governance/vote

Request:
{
    "policy_id": "city-eco-remediation-001",
    "voters": [
        {"id": "env_agency", "weight": 0.35},
        {"id": "health_dept", "weight": 0.3}
    ],
    "vectors": [
        {"name": "environmental_impact", "score": 0.95},
        {"name": "cost_effectiveness", "score": -0.60}
    ]
}

Response:
{
    "policy_id": "city-eco-remediation-001",
    "aggregate_score": 0.53,
    "vector_breakdown": {...},
    "voter_consensus": 0.645,
    "recommendation": "NEEDS_REVIEW",
    "explanation": "...",
    "timestamp": "2025-12-28T10:00:00Z",
    "confidence": 0.89
}
```

## 8. Confidence Scoring

Each decision includes a confidence metric:

```
Confidence = min(0.95, 0.5 + (Consensus × 0.45))
```

- Ranges from 0.5 to 0.95
- Reflects the reliability of the recommendation
- Lower confidence = more uncertainty = recommendation for human review

## 9. Audit Trail

All voting decisions are immutably logged:

```
Audit Entry = {
    timestamp: datetime,
    policy_id: str,
    aggregate_score: float,
    consensus: float,
    recommendation: str,
    votes: list[{voter_id, vector_scores}],
    decision_made_by: str,
    implementation_status: str,
    outcome_metrics: dict
}
```

## 10. Extension: Domain-Specific Vectors

The system supports custom vectors per domain:

### Wastewater Treatment Vectors
- Treatment Efficiency
- Environmental Impact
- Cost per Treatment Unit
- Regulatory Compliance
- Workforce Requirements

### Policy Vectors
- Environmental Benefit
- Economic Impact
- Social Acceptance
- Implementation Feasibility
- Long-term Sustainability

## 11. Security & Governance

- **Vote Immutability**: All votes recorded with cryptographic verification
- **Stakeholder Verification**: Multi-factor authentication for voter identities
- **Weight Auditability**: Changes to voter weights require consensus
- **Transparency**: Public dashboard showing all voting data and explanations
- **Appeal Mechanism**: Stakeholders can request reconsideration with new evidence

## 12. Future Enhancements

1. **Blockchain Integration**: Store voting records on-chain for immutability
2. **Machine Learning**: Predict policy outcomes based on historical voting patterns
3. **Weighted Consensus**: Account for stakeholder credibility scores
4. **Dynamic Vectors**: Automatically adjust vectors based on domain-specific ML models
5. **Natural Language Processing**: Extract voting vectors from stakeholder narratives
6. **Prediction Markets**: Allow stakeholders to bet on policy outcomes

## References

- Arrow's Impossibility Theorem (voting theory foundations)
- Borda Count (weighted aggregation inspiration)
- Condorcet Method (consensus measurement)
- Shapley Value (fair power distribution)

---

**Version**: 1.0.0  
**Last Updated**: December 2025  
**Maintainer**: Enviro-Governance Platform Team
