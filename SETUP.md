# Local Development Setup

This guide provides step-by-step instructions for setting up the enviro-governance-platform for local development.

## Prerequisites

- Python 3.9+
- PostgreSQL 12+
- Node.js 16+ (for frontend)
- Git
- pip and poetry (Python dependency management)

## Backend Setup (FastAPI)

### 1. Clone the Repository

```bash
git clone https://github.com/romanchaa997/enviro-governance-platform.git
cd enviro-governance-platform
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create `.env` file in backend directory:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/enviro_governance
JWT_SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=your-api-key
REDIS_URL=redis://localhost:6379
```

### 5. Initialize PostgreSQL Database

```bash
# Create database
psql -U postgres -c "CREATE DATABASE enviro_governance;"

# Run migrations
alembic upgrade head
```

### 6. Start FastAPI Server

```bash
uvicorn app.main:app --reload
```

Server will be available at `http://localhost:8000`

## Database Schema Setup

### Core Tables

- `users` - User accounts and authentication
- `organizations` - B2B customers and municipalities
- `remediation_plans` - Generated remediation strategies
- `agents` - PoC agent configurations (fungi, bacteria, CRISPR)
- `voting_vectors` - Multi-vector decision engine (environment, health, economy, speed)
- `decisions` - City/region policy decisions
- `audit_logs` - Governance transparency and accountability

## PoC Agent Module

### Remediation Agent API

**Endpoint**: `POST /v1/remediation/plan`

**Request**:
```json
{
  "pollution_description": "Heavy metals in wastewater, high nitrogen levels",
  "site_type": "wastewater_treatment_plant",
  "location": "EU-region-1",
  "budget_tier": "medium"
}
```

**Response**:
```json
{
  "strategies": [
    {
      "agent_type": "fungal_remediation",
      "name": "Mycoremediation using Pleurotus species",
      "effectiveness": 0.85,
      "timeline_days": 90,
      "cost_estimate": 50000,
      "risks": ["Seasonal temperature sensitivity", "Maintenance requirements"],
      "explanation": "Pleurotus fungi excel at breaking down heavy metals..."
    },
    {
      "agent_type": "bacterial_consortium",
      "name": "Nitrifying bacteria and denitrifiers",
      "effectiveness": 0.78,
      "timeline_days": 60,
      "cost_estimate": 35000,
      "risks": ["pH optimization needed"],
      "explanation": "Consortium approach combines nitrifying and denitrifying bacteria..."
    }
  ],
  "recommended_order": [0, 1],
  "total_timeline_days": 150
}
```

## Multi-Vector Voting System

### Decision Engine API

**Endpoint**: `POST /v1/governance/vote`

**Request**:
```json
{
  "policy_id": "city-eco-001",
  "voters": [
    {"id": "health_dept", "weight": 0.3},
    {"id": "environment_agency", "weight": 0.35},
    {"id": "finance_ministry", "weight": 0.2},
    {"id": "civil_society", "weight": 0.15}
  ],
  "vectors": [
    {"name": "environmental_impact", "score": 0.9},
    {"name": "health_benefit", "score": 0.85},
    {"name": "economic_cost", "score": -0.3},
    {"name": "implementation_speed", "score": 0.7}
  ]
}
```

## Testing

```bash
# Run pytest suite
pytest tests/

# Run with coverage
pytest --cov=app tests/

# Run specific agent tests
pytest tests/agents/test_remediation.py -v
```

## API Documentation

Once server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Deployment

See `DEPLOYMENT.md` for production deployment instructions.

## Common Issues

### PostgreSQL Connection Error

Ensure PostgreSQL is running and DATABASE_URL is correct:
```bash
psql -U postgres -d enviro_governance -c "SELECT 1;"
```

### Port Already in Use

Change port in startup command:
```bash
uvicorn app.main:app --reload --port 8001
```

## Contributing

See `CONTRIBUTING.md` for development guidelines.
