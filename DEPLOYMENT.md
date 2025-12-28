# Production Deployment Guide

## Overview

This guide covers deploying enviro-governance-platform to production environments. We support AWS, GCP, and Azure deployments with Kubernetes orchestration.

## Pre-Deployment Checklist

- [ ] All tests passing (GitHub Actions CI/CD)
- [ ] Security audit completed
- [ ] Database migrations tested in staging
- [ ] Environment variables configured for production
- [ ] SSL/TLS certificates provisioned
- [ ] Backup and disaster recovery plan documented
- [ ] Monitoring and alerting configured
- [ ] Load testing completed

## Kubernetes Deployment

### Prerequisites

- Kubernetes 1.21+
- kubectl configured
- Helm 3.x
- Docker registry access (ECR, GCR, or ACR)

### 1. Build and Push Docker Images

```bash
# Build backend image
docker build -t enviro-governance-platform:latest -f Dockerfile.backend .
docker tag enviro-governance-platform:latest $REGISTRY/enviro-governance-platform:latest
docker push $REGISTRY/enviro-governance-platform:latest

# Build frontend image (optional)
docker build -t enviro-governance-frontend:latest -f Dockerfile.frontend .
docker tag enviro-governance-frontend:latest $REGISTRY/enviro-governance-frontend:latest
docker push $REGISTRY/enviro-governance-frontend:latest
```

### 2. Create Kubernetes Secrets

```bash
# Database credentials
kubectl create secret generic db-credentials \
  --from-literal=DB_URL=postgresql://user:password@postgres-service:5432/enviro_governance \
  -n enviro-governance

# API Keys and secrets
kubectl create secret generic api-secrets \
  --from-literal=JWT_SECRET_KEY=your-secret-key \
  --from-literal=OPENAI_API_KEY=your-api-key \
  -n enviro-governance

# TLS/SSL Certificates
kubectl create secret tls tls-secret \
  --cert=path/to/tls.crt \
  --key=path/to/tls.key \
  -n enviro-governance
```

### 3. Deploy PostgreSQL (if using managed service)

**Option A: Self-hosted PostgreSQL StatefulSet**

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
spec:
  serviceName: postgres-service
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:14
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_DB
          value: "enviro_governance"
        - name: POSTGRES_USER
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: DB_USER
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: DB_PASSWORD
        volumeMounts:
        - name: pgdata
          mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
  - metadata:
      name: pgdata
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 100Gi
```

**Option B: AWS RDS / Azure Database for PostgreSQL / GCP Cloud SQL**

Use managed database service for high availability (recommended for production).

### 4. Deploy Backend Service

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: enviro-governance-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: $REGISTRY/enviro-governance-platform:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: DB_URL
        - name: JWT_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: api-secrets
              key: JWT_SECRET_KEY
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-secrets
              key: OPENAI_API_KEY
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
---
apiVersion: v1
kind: Service
metadata:
  name: backend-service
spec:
  selector:
    app: backend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

### 5. Configure Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: enviro-governance-ingress
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - api.enviro-governance.com
    secretName: tls-secret
  rules:
  - host: api.enviro-governance.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: backend-service
            port:
              number: 80
```

### 6. Deploy Monitoring Stack

```bash
# Install Prometheus
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack \
  -n enviro-governance

# Install Grafana
helm repo add grafana https://grafana.github.io/helm-charts
helm install grafana grafana/grafana \
  -n enviro-governance
```

## Environment Configuration

### Production Environment Variables

```env
# Database
DATABASE_URL=postgresql://user:password@rds-endpoint:5432/enviro_governance
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# Application
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Security
JWT_SECRET_KEY=<secure-random-key>
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
CORS_ORIGINS=["https://app.enviro-governance.com"]

# LLM Integration
OPENAI_API_KEY=<your-api-key>
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.7

# Cache
REDIS_URL=redis://redis-service:6379
CACHE_TTL_SECONDS=3600

# Monitoring
SENTRY_DSN=<sentry-project-url>
PROMETHEUS_ENABLED=true

# Email (for notifications)
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=<sendgrid-api-key>
```

## Database Migrations

```bash
# Run migrations in production
alembic upgrade head

# Verify migrations
alembic current
alembic history
```

## Health Checks

### Endpoints

```
GET /health        - Basic health check
GET /ready         - Readiness probe (includes DB check)
GET /metrics       - Prometheus metrics
```

## Backup and Disaster Recovery

### PostgreSQL Backups

```bash
# Daily automated backup via AWS RDS
# Or manual backup:
pg_dump -h $DB_HOST -U $DB_USER $DB_NAME > backup_$(date +%Y%m%d).sql

# Restore from backup
psql -h $DB_HOST -U $DB_USER $DB_NAME < backup_20231215.sql
```

### Disaster Recovery Plan

1. **RTO (Recovery Time Objective)**: 1 hour
2. **RPO (Recovery Point Objective)**: 15 minutes
3. **Backup Location**: Multi-region cloud storage (S3, GCS, Azure Blob)
4. **Restore Testing**: Monthly DR drills

## Scaling and Performance

### Horizontal Scaling

```bash
# Scale backend replicas
kubectl scale deployment enviro-governance-backend --replicas=5 -n enviro-governance

# Monitor scaling
kubectl get hpa -n enviro-governance
```

### Auto-Scaling Configuration

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: enviro-governance-backend
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

## Logging and Monitoring

### Log Aggregation

```bash
# Deploy ELK Stack or use cloud-native solutions
helm install elastic elastic/elasticsearch -n enviro-governance
helm install kibana elastic/kibana -n enviro-governance
```

### Key Metrics to Monitor

- API response time (P95, P99)
- Database query latency
- Error rate (4xx, 5xx)
- CPU and memory usage
- Network I/O
- Cache hit rate
- JWT token validation rate

## Rollout Strategy

### Blue-Green Deployment

```bash
# Deploy new version to green environment
kubectl set image deployment/enviro-governance-backend \
  backend=$REGISTRY/enviro-governance-platform:v1.1.0

# Test green environment
# Switch traffic
kubectl patch service backend-service -p '{"spec":{"selector":{"version":"v1.1.0"}}}'
```

### Canary Deployment

```bash
# Deploy 10% traffic to new version
kubectl set image deployment/enviro-governance-backend \
  backend=$REGISTRY/enviro-governance-platform:v1.1.0 --record
```

## Troubleshooting

### Common Issues

#### Pod not starting
```bash
kubectl describe pod <pod-name> -n enviro-governance
kubectl logs <pod-name> -n enviro-governance
```

#### Database connection errors
```bash
# Test database connectivity
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT 1;"
```

#### High memory usage
```bash
kubectl top pods -n enviro-governance
kubectl logs <pod-name> --tail=100 -n enviro-governance
```

## Post-Deployment

1. Verify all services are running: `kubectl get pods -n enviro-governance`
2. Check logs: `kubectl logs -f deployment/enviro-governance-backend -n enviro-governance`
3. Test API endpoints
4. Verify database connectivity and migrations
5. Confirm monitoring and alerting are active
6. Document any customizations or deviations

## Support and Escalation

- Platform Issues: Create GitHub issue with deployment logs
- Security Issues: Email security@enviro-governance.com
- Performance Issues: Contact DevOps team with metrics
