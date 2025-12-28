# Security Hardening Guide

## Authentication & Authorization

### JWT Configuration
```python
# backend/config/security.py
SECURE_ALGORITHM = "HS256"
TOKEN_EXPIRATION_HOURS = 24
REFRESH_TOKEN_EXPIRATION_DAYS = 7
SECRET_KEY = os.environ.get("JWT_SECRET_KEY")  # Min 32 chars
```

### RBAC Implementation
```python
class UserRole(str, Enum):
    ADMIN = "admin"
    MODERATOR = "moderator"
    STAKEHOLDER = "stakeholder"
    GUEST = "guest"

async def check_role(required_roles: List[UserRole]):
    async def role_checker(token: str = Depends(oauth2_scheme)):
        user = await get_user_from_token(token)
        if user.role not in required_roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return role_checker
```

## Data Protection

### Encryption at Rest
- **Database**: PostgreSQL with pgcrypto extension
- **Secrets**: AWS Secrets Manager or HashiCorp Vault
- **Sensitive fields**: AES-256 encryption for PII

### Encryption in Transit
- **TLS 1.3+**: All endpoints require HTTPS
- **HSTS**: Strict-Transport-Security header enabled
- **Certificate pinning**: For mobile applications

## API Security

### Rate Limiting
```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/proposals")
@limiter.limit("100/hour")
async def create_proposal(request: Request, proposal: ProposalSchema):
    pass
```

### CORS Configuration
```python
CORS_ORIGINS = [os.environ.get("FRONTEND_URL")]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ["GET", "POST", "PUT"]
CORS_ALLOW_HEADERS = ["Authorization", "Content-Type"]
```

## Input Validation

### Pydantic Schemas
```python
class ProposalCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=10, max_length=5000)
    vectors: List[str] = Field(..., min_items=1, max_items=10)
    
    @validator('title')
    def sanitize_title(cls, v):
        return v.strip()
```

### SQL Injection Prevention
- Use parameterized queries (SQLAlchemy ORM)
- Never concatenate user input into SQL
- Validate input types

## Dependency Management

### Security Scanning
```bash
# Scan for vulnerabilities
pip install safety
safety check

# Generate SBOM (Software Bill of Materials)
pip-audit --desc
```

### Dependencies to Lock
```
FastAPI==0.104.1
SQLAlchemy==2.0.23
Pydantic==2.5.0
python-jose==3.3.0
passlib==1.7.4
```

## Logging & Monitoring

### Security Logging
```python
import logging

security_logger = logging.getLogger("security")

# Log authentication failures
security_logger.warning(f"Failed login attempt: {username}")

# Log permission denials
security_logger.warning(f"Permission denied for user {user_id}: {resource}")

# Log suspicious activity
if login_attempts > 5:
    security_logger.critical(f"Brute force detected: {ip_address}")
```

### Monitoring Alerts
- Multiple failed login attempts (>5)
- Unauthorized API access attempts
- Rate limit violations
- Certificate expiration warnings

## Production Hardening

### Environment Configuration
```bash
# .env.production
DEBUG=false
ALLOWED_HOSTS=governance.example.com
SECURE_COOKIES=true
SAMESITE_COOKIES=Strict
X_FRAME_OPTIONS=DENY
CONTENT_SECURITY_POLICY="default-src 'self'"
```

### Secrets Management
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    jwt_secret_key: str
    api_keys: dict
    
    class Config:
        env_file = ".env"
        extra = "forbid"  # Reject unknown env vars
```

## Container Security

### Dockerfile Best Practices
```dockerfile
# Use minimal base image
FROM python:3.11-slim

# Run as non-root user
RUN useradd -m appuser
USER appuser

# Set security headers
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev && rm -rf /var/lib/apt/lists/*
```

### Container Scanning
```bash
# Scan image for vulnerabilities
docker scan governance-platform:latest

# Use signed images
docker trust inspect governance-platform:latest
```

## Database Security

### PostgreSQL Hardening
```sql
-- Disable superuser login
ALTER ROLE postgres WITH NOLOGIN;

-- Create restricted user
CREATE USER governance WITH PASSWORD 'strong_password';
GRANT CONNECT ON DATABASE governance_db TO governance;

-- Row-level security
ALTER TABLE proposals ENABLE ROW LEVEL SECURITY;
CREATE POLICY user_proposals ON proposals
  USING (created_by = current_user_id());
```

## Compliance

### Data Privacy (GDPR/CCPA)
- Data retention policies (max 2 years for proposals)
- Right to deletion implementation
- Data export functionality
- Privacy policy and consent tracking

### Audit Logging
```python
class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id: int = Column(Integer, primary_key=True)
    user_id: str
    action: str
    resource: str
    timestamp: datetime = Column(DateTime, default=datetime.utcnow)
    ip_address: str
    user_agent: str
```

## Incident Response

### Security Incident Plan
1. **Detection**: Monitor logs and alerts
2. **Containment**: Disable affected accounts/API keys
3. **Investigation**: Analyze attack vectors
4. **Recovery**: Restore from backups
5. **Communication**: Notify affected users
6. **Post-mortem**: Document lessons learned

### Emergency Procedures
```bash
# Revoke all tokens
redis-cli FLUSHDB

# Rotate credentials
aws secretsmanager rotate-secret --secret-id jwt-secret

# Block suspicious IPs
aws wafv2 create-ip-set --region us-east-1 ...
```

## Testing

### Security Testing Tools
- **OWASP ZAP**: Dynamic security scanning
- **Bandit**: Python code security analysis
- **SQLMap**: SQL injection testing
- **Burp Suite**: Web application testing

### Regular Security Audits
- Quarterly: Internal code review
- Semi-annual: Third-party penetration test
- Annually: Full security assessment

## Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [CWE/SANS Top 25](https://cwe.mitre.org/top25/)
- [Security.txt](https://securitytxt.org/)

## Security Contacts

- **Security Email**: security@governance.example.com
- **Incident Response**: 24/7 on-call team
- **Bug Bounty Program**: https://bugbounty.governance.example.com
