# System Architecture

## Overview

enviro-governance-platform is a B2B SaaS platform combining AI-driven environmental remediation intelligence with transparent multi-stakeholder decision-making. It integrates biological agents (fungi, bacteria, CRISPR), explainable AI, and multi-vector governance voting systems.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React/Vue)                      │
│              (Policy Dashboard, PoC Agent UI)                │
└────────────────────┬────────────────────────────────────────┘
                     │ REST/GraphQL
┌────────────────────▼────────────────────────────────────────┐
│                   API Gateway                               │
│              (FastAPI/Node.js)                              │
│  - Authentication (JWT)                                     │
│  - Rate limiting, Monitoring                                │
└────────┬─────────────────────────────────────┬──────────────┘
         │                                     │
    ┌────▼────────────┐           ┌───────────▼──────┐
    │ Remediation     │           │  Governance      │
    │ Agent Service   │           │  Engine Service  │
    │  (FastAPI)      │           │   (FastAPI)      │
    ├─────────────────┤           ├──────────────────┤
    │ - Fungi Agent   │           │ - Multi-vector   │
    │ - Bacteria      │           │   voting logic   │
    │ - CRISPR        │           │ - Policy consensus│
    │ - LLM explainer │           │ - Audit logging  │
    └────┬────────────┘           └────┬─────────────┘
         │                             │
         └─────────┬───────────────────┘
                   │ SQL/ORM (SQLAlchemy)
         ┌─────────▼──────────────┐
         │   PostgreSQL Database  │
         │                        │
         │ Tables:                │
         │ - users               │
         │ - organizations       │
         │ - remediation_plans   │
         │ - agents              │
         │ - voting_vectors      │
         │ - decisions           │
         │ - audit_logs          │
         └────────────────────────┘
```

## Core Modules

### 1. Remediation Agent Module

**Purpose**: Generate biological remediation strategies for environmental contamination.

**Components**:
- **Fungal Remediation Agent**: Mycoremediation using species like Pleurotus, Trametes, Aspergillus
- **Bacterial Consortium**: Nitrifying bacteria, denitrifiers, metal-oxidizing bacteria
- **CRISPR Engineering**: Synthetic biology pathways for advanced scenarios
- **LLM Explainer**: Provides risk assessments, timelines, and implementation guidance

**API Endpoint**:
```
POST /v1/remediation/plan
```

**Request Schema**:
```python
class RemediationRequest(BaseModel):
    pollution_description: str
    site_type: str  # "wastewater_treatment_plant", "contaminated_land", etc.
    location: str
    budget_tier: str  # "low", "medium", "high"
    deadline_months: Optional[int]
```

**Response Schema**:
```python
class RemediationStrategy(BaseModel):
    agent_type: str
    name: str
    effectiveness: float  # 0.0-1.0
    timeline_days: int
    cost_estimate: float
    risks: List[str]
    explanation: str
    implementation_steps: List[str]

class RemediationResponse(BaseModel):
    strategies: List[RemediationStrategy]
    recommended_order: List[int]
    total_timeline_days: int
```

### 2. Multi-Vector Governance Engine

**Purpose**: Enable transparent, multi-stakeholder decision-making on environmental policies using weighted voting across multiple value dimensions.

**Voting Vectors** (configurable):
1. **Environmental Impact**: Long-term ecological benefit
2. **Health Benefit**: Public health improvements
3. **Economic Cost**: Financial burden (negative scoring)
4. **Implementation Speed**: Time-to-deployment
5. **Social Equity**: Distribution of benefits/burdens
6. **Technical Feasibility**: Implementation complexity

**Stakeholders** (weighted per decision):
- Environmental Agency (0.35)
- Health Department (0.30)
- Finance Ministry (0.20)
- Civil Society/NGOs (0.15)

**API Endpoint**:
```
POST /v1/governance/vote
```

**Request Schema**:
```python
class VoterWeight(BaseModel):
    id: str
    weight: float

class VotingVector(BaseModel):
    name: str
    score: float  # -1.0 to 1.0

class GovernanceVoteRequest(BaseModel):
    policy_id: str
    voters: List[VoterWeight]
    vectors: List[VotingVector]
    context: Optional[str]

class GovernanceVoteResponse(BaseModel):
    policy_id: str
    aggregate_score: float
    vector_breakdown: Dict[str, float]
    recommendation: str  # "APPROVE", "REJECT", "NEEDS_REVIEW"
    explanation: str
    voter_consensus: float  # 0.0-1.0
```

### 3. Database Layer

**ORM**: SQLAlchemy 2.0  
**Database**: PostgreSQL 12+  
**Migrations**: Alembic

**Core Tables**:

#### `users`
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    password_hash VARCHAR NOT NULL,
    organization_id UUID FOREIGN KEY,
    role VARCHAR DEFAULT 'user',  -- 'user', 'admin', 'analyst'
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

#### `remediation_plans`
```sql
CREATE TABLE remediation_plans (
    id UUID PRIMARY KEY,
    user_id UUID FOREIGN KEY,
    organization_id UUID FOREIGN KEY,
    pollution_description TEXT NOT NULL,
    site_type VARCHAR NOT NULL,
    location VARCHAR NOT NULL,
    strategies JSONB NOT NULL,  -- Array of strategy objects
    selected_strategy_index INT,
    status VARCHAR DEFAULT 'draft',  -- 'draft', 'active', 'completed'
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

#### `decisions`
```sql
CREATE TABLE decisions (
    id UUID PRIMARY KEY,
    policy_id VARCHAR UNIQUE NOT NULL,
    organization_id UUID FOREIGN KEY,
    voting_data JSONB NOT NULL,
    aggregate_score FLOAT NOT NULL,
    status VARCHAR DEFAULT 'pending',  -- 'pending', 'approved', 'rejected'
    audit_log_id UUID FOREIGN KEY,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

#### `audit_logs`
```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY,
    user_id UUID FOREIGN KEY,
    action VARCHAR NOT NULL,
    resource_type VARCHAR,
    resource_id VARCHAR,
    changes JSONB,
    ip_address VARCHAR,
    created_at TIMESTAMP
);
```

## Technology Stack

### Backend
- **Framework**: FastAPI (async, modern Python)
- **Server**: Uvicorn
- **Database**: PostgreSQL 12+
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic
- **Authentication**: JWT (PyJWT)
- **Validation**: Pydantic
- **LLM Integration**: OpenAI API / LangChain
- **Task Queue**: Celery + Redis (for async remediation planning)
- **Monitoring**: Prometheus, Grafana

### Frontend
- **Framework**: React 18 / Vue 3 (TBD)
- **State Management**: Redux / Pinia
- **UI Components**: Material-UI / Tailwind CSS
- **Visualization**: Plotly.js (for voting results)

### Infrastructure
- **Containerization**: Docker
- **Orchestration**: Kubernetes (production)
- **CI/CD**: GitHub Actions
- **Cloud**: AWS/GCP/Azure (configurable)
- **Cache**: Redis

## Deployment Architecture

### Development
```bash
Docker Compose (backend + PostgreSQL + Redis)
```

### Staging/Production
```
Kubernetes Cluster
├── Backend Service (FastAPI replicas)
├── Frontend Service (React SPA)
├── PostgreSQL StatefulSet
├── Redis Cache
└── Nginx Ingress
```

## API Versioning

All endpoints follow `/v1/` prefix. Future versions (v2, v3) will be backwards-compatible with route aliases.

## Security Considerations

- **Authentication**: JWT tokens, 15-minute expiry
- **HTTPS**: Enforced on all endpoints
- **Rate Limiting**: 1000 requests/min per API key
- **CORS**: Configurable per-environment
- **SQL Injection**: Protected via SQLAlchemy parameterized queries
- **CSRF**: Standard CSRF tokens for state-changing operations
- **Audit Trail**: All state changes logged with user ID, IP, timestamp

## Performance Targets

- **Remediation Plan Generation**: < 2 seconds (API response)
- **Governance Vote Aggregation**: < 500ms
- **Database Query**: < 100ms (P95)
- **API Throughput**: 1000+ RPS (rate-limited)
- **Uptime**: 99.9% SLA

## Scalability

- **Horizontal Scaling**: Stateless FastAPI instances
- **Database**: Connection pooling (pgBouncer), read replicas for reports
- **Caching**: Redis for voting results, popular remediation strategies
- **Async Tasks**: Celery workers for long-running agent planning
