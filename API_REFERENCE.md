# Enviro-Governance Platform API Reference

## Base URL

```
https://api.governance.example.com/api/v1
```

## Authentication

All endpoints require JWT Bearer token in the `Authorization` header:

```
Authorization: Bearer <JWT_TOKEN>
```

## Proposal Endpoints

### Create Proposal

**POST** `/proposals`

Create a new environmental governance proposal.

```json
Request:
{
  "title": "Renewable Energy Initiative",
  "description": "Transition to 100% renewable energy",
  "category": "energy",
  "vectors": ["environmental", "economic", "social"],
  "deadline": "2024-02-15T23:59:59Z"
}

Response (201):
{
  "id": "prop_123abc",
  "title": "Renewable Energy Initiative",
  "status": "open",
  "created_at": "2024-01-15T10:30:00Z",
  "created_by": "user_456def"
}
```

### Get Proposals

**GET** `/proposals?page=1&limit=20&status=open`

Retrieve paginated list of proposals.

```json
Response (200):
{
  "data": [
    {
      "id": "prop_123abc",
      "title": "Renewable Energy Initiative",
      "status": "open",
      "voting_percentage": 65.5,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 150
  }
}
```

### Get Proposal Details

**GET** `/proposals/{proposal_id}`

Retrieve detailed information about a specific proposal.

```json
Response (200):
{
  "id": "prop_123abc",
  "title": "Renewable Energy Initiative",
  "description": "Transition to 100% renewable energy",
  "status": "open",
  "vectors": ["environmental", "economic", "social"],
  "votes_count": 245,
  "voting_results": {
    "environmental": 78.5,
    "economic": 65.2,
    "social": 72.1
  },
  "aggregate_score": 71.9,
  "deadline": "2024-02-15T23:59:59Z",
  "created_at": "2024-01-15T10:30:00Z"
}
```

## Voting Endpoints

### Cast Vote

**POST** `/proposals/{proposal_id}/votes`

Submit a vote on a proposal with multi-vector weights.

```json
Request:
{
  "vector_weights": {
    "environmental": 100,
    "economic": 75,
    "social": 85
  },
  "comment": "Strong environmental impact expected"
}

Response (201):
{
  "id": "vote_789ghi",
  "proposal_id": "prop_123abc",
  "user_id": "user_456def",
  "vector_weights": {"environmental": 100, "economic": 75, "social": 85},
  "created_at": "2024-01-15T11:00:00Z"
}
```

### Get Voting Results

**GET** `/proposals/{proposal_id}/voting-results`

Retrieve aggregated voting results with vector breakdown.

```json
Response (200):
{
  "proposal_id": "prop_123abc",
  "total_votes": 245,
  "vector_results": {
    "environmental": {"average": 78.5, "std_dev": 12.3},
    "economic": {"average": 65.2, "std_dev": 15.7},
    "social": {"average": 72.1, "std_dev": 11.2}
  },
  "aggregate_score": 71.9,
  "consensus_level": "moderate"
}
```

### Get User's Votes

**GET** `/users/{user_id}/votes`

Retrieve all votes cast by a specific user.

```json
Response (200):
{
  "user_id": "user_456def",
  "votes": [
    {
      "id": "vote_789ghi",
      "proposal_id": "prop_123abc",
      "vector_weights": {"environmental": 100, "economic": 75, "social": 85},
      "created_at": "2024-01-15T11:00:00Z"
    }
  ]
}
```

## Governance Engine Endpoints

### Get Governance Analysis

**GET** `/governance/analysis/{proposal_id}`

Retrieve AI-powered governance analysis and recommendations.

```json
Response (200):
{
  "proposal_id": "prop_123abc",
  "governance_status": "approved",
  "confidence_score": 0.87,
  "recommendation": "Recommend immediate implementation",
  "risk_assessment": "low",
  "impact_areas": ["climate", "energy", "economics"],
  "analysis": {
    "strengths": ["High environmental impact", "Strong community support"],
    "weaknesses": ["High initial cost"],
    "opportunities": ["Job creation", "Technology innovation"],
    "threats": ["Political resistance"]
  }
}
```

### Get Remediation Suggestions

**GET** `/governance/{proposal_id}/remediation`

Retrieve AI-generated environmental remediation suggestions.

```json
Response (200):
{
  "proposal_id": "prop_123abc",
  "remediation_strategies": [
    {
      "id": "rem_001",
      "strategy": "Fungal bioremediation",
      "effectiveness": 0.82,
      "timeframe": "6-12 months",
      "cost_estimate": "$500K-$750K",
      "description": "Deploy Pestalotipora microspora for contamination removal"
    },
    {
      "id": "rem_002",
      "strategy": "Bacterial consortium",
      "effectiveness": 0.75,
      "timeframe": "12-18 months",
      "cost_estimate": "$300K-$450K",
      "description": "Application of engineered bacterial strains"
    }
  ]
}
```

## User Endpoints

### Get User Profile

**GET** `/users/{user_id}`

Retrieve user profile information.

```json
Response (200):
{
  "id": "user_456def",
  "email": "user@example.com",
  "name": "John Doe",
  "role": "stakeholder",
  "organization": "Environmental Council",
  "voting_weight": 1.5,
  "votes_count": 23,
  "created_at": "2023-06-01T08:00:00Z"
}
```

### Update User Profile

**PUT** `/users/{user_id}`

Update user profile information.

```json
Request:
{
  "name": "John Doe Jr.",
  "organization": "Environmental Council 2.0"
}

Response (200):
{
  "id": "user_456def",
  "name": "John Doe Jr.",
  "organization": "Environmental Council 2.0"
}
```

## Agent Endpoints

### Get Available Agents

**GET** `/agents`

Retrieve list of available AI remediation agents.

```json
Response (200):
{
  "agents": [
    {
      "id": "agent_fungal_01",
      "name": "Fungal Remediation Agent",
      "type": "biological",
      "capability": "Heavy metal removal",
      "effectiveness_range": [0.70, 0.90],
      "status": "active"
    },
    {
      "id": "agent_bacterial_01",
      "name": "Bacterial Consortium Agent",
      "type": "biological",
      "capability": "Organic pollutant degradation",
      "effectiveness_range": [0.65, 0.85],
      "status": "active"
    }
  ]
}
```

### Execute Agent

**POST** `/agents/{agent_id}/execute`

Trigger agent execution for remediation task.

```json
Request:
{
  "proposal_id": "prop_123abc",
  "parameters": {
    "target_contaminant": "heavy_metals",
    "site_area": 5000,
    "priority": "high"
  }
}

Response (202):
{
  "execution_id": "exec_789xyz",
  "agent_id": "agent_fungal_01",
  "status": "processing",
  "created_at": "2024-01-15T12:00:00Z"
}
```

## Error Responses

All errors follow this format:

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Missing required parameter: title",
    "details": {
      "field": "title",
      "requirement": "String (3-200 characters)"
    }
  }
}
```

### Common Status Codes

| Code | Meaning |
|------|----------|
| 200 | OK - Request succeeded |
| 201 | Created - Resource created |
| 202 | Accepted - Processing request |
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Invalid/missing token |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource doesn't exist |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error |

## Rate Limiting

API requests are rate-limited:

- **1000 requests** per hour per API key
- **50 requests** per minute for public endpoints
- **200 requests** per minute for authenticated endpoints

Rate limit headers are included in responses:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1705324800
```

## Pagination

List endpoints support pagination with query parameters:

```
GET /proposals?page=2&limit=50&sort=created_at&order=desc
```

Parameters:
- `page` - Page number (default: 1)
- `limit` - Items per page (default: 20, max: 100)
- `sort` - Field to sort by (default: created_at)
- `order` - Sort order: asc/desc (default: desc)

## Webhook Events

Webhooks are triggered for the following events:

- `proposal.created` - New proposal published
- `proposal.closed` - Voting period ended
- `vote.submitted` - User submitted vote
- `governance.decision_made` - Governance engine made recommendation
- `agent.execution_complete` - Remediation agent completed task

## SDK Examples

### Python

```python
from enviro_governance import GovernanceClient

client = GovernanceClient(api_key="YOUR_API_KEY")

# Create proposal
proposal = client.proposals.create(
    title="Renewable Energy Initiative",
    description="...",
    vectors=["environmental", "economic", "social"]
)

# Cast vote
vote = client.votes.create(
    proposal_id=proposal.id,
    vector_weights={"environmental": 100, "economic": 75}
)
```

### JavaScript

```javascript
const client = new GovernanceClient({apiKey: 'YOUR_API_KEY'});

// Create proposal
const proposal = await client.proposals.create({
  title: 'Renewable Energy Initiative',
  vectors: ['environmental', 'economic', 'social']
});

// Cast vote
const vote = await client.votes.create({
  proposalId: proposal.id,
  vectorWeights: {environmental: 100, economic: 75}
});
```

## Support

For API support, contact:
- **Documentation**: https://docs.governance.example.com
- **Issues**: https://github.com/romanchaa997/enviro-governance-platform/issues
- **Email**: api-support@governance.example.com
