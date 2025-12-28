# Enviro-Governance Platform Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying the Enviro-Governance Platform across different environments: local development, staging, and production.

## Architecture

### Services

- **Backend API**: FastAPI service with multi-vector governance voting engine
- **Frontend**: React SPA with real-time governance interface
- **Database**: PostgreSQL with advanced voting schema
- **Cache**: Redis for session management and voting state
- **Message Queue**: RabbitMQ for asynchronous governance operations
- **Search Engine**: Elasticsearch for proposal and voting history search

## Prerequisites

### Development Environment

```bash
# Required tools
- Docker Desktop 4.0+
- Docker Compose 1.29+
- Node.js 16.x LTS
- Python 3.10+
- PostgreSQL 14 client tools
- Git 2.30+
```

### System Requirements

- **Development**: 4GB RAM, 20GB disk space
- **Staging**: 8GB RAM, 50GB disk space
- **Production**: 16GB RAM, 100GB disk space, auto-scaling configured

## Local Development Deployment

### 1. Clone Repository

```bash
git clone https://github.com/romanchaa997/enviro-governance-platform.git
cd enviro-governance-platform
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit configuration
vi .env
```

**Key Variables**:
```
DATABASE_URL=postgresql://user:password@localhost:5432/governance_db
REDIS_URL=redis://localhost:6379/0
FASTAPI_ENV=development
FRONTEND_PORT=3000
BACKEND_PORT=8000
JWT_SECRET_KEY=your-secret-key-here
```

### 3. Start Services

```bash
# Using Docker Compose
docker-compose -f docker-compose.yml up -d

# Verify services
docker-compose ps
```

### 4. Initialize Database

```bash
# Run migrations
cd backend
alembic upgrade head

# Seed initial data
python scripts/seed_database.py
```

### 5. Run Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Run Frontend

```bash
cd frontend
npm install
npm run dev
```

**Access Application**:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Staging Deployment

### 1. AWS Infrastructure Setup

```bash
# Using Terraform
cd infrastructure/terraform
terraform init
terraform plan
terraform apply -var-file=staging.tfvars
```

### 2. RDS Database Setup

```bash
# Create RDS instance
aws rds create-db-instance \
  --db-instance-identifier governance-staging \
  --db-instance-class db.t3.medium \
  --engine postgres \
  --master-username admin \
  --master-user-password $STAGING_DB_PASSWORD \
  --allocated-storage 100

# Update security groups
aws ec2 authorize-security-group-ingress \
  --group-id sg-staging \
  --protocol tcp \
  --port 5432 \
  --source-security-group-id sg-app-staging
```

### 3. ElastiCache Redis

```bash
aws elasticache create-cache-cluster \
  --cache-cluster-id governance-staging-cache \
  --engine redis \
  --cache-node-type cache.t3.micro \
  --num-cache-nodes 1
```

### 4. Deploy Application

```bash
# Build Docker image
docker build -t governance-platform:staging-1.0.0 .

# Push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

docker tag governance-platform:staging-1.0.0 $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/governance-platform:staging-1.0.0

docker push $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/governance-platform:staging-1.0.0
```

### 5. Deploy to ECS

```bash
# Update ECS task definition
aws ecs register-task-definition \
  --cli-input-json file://task-definition.json

# Update ECS service
aws ecs update-service \
  --cluster governance-staging \
  --service governance-app \
  --force-new-deployment
```

## Production Deployment

### 1. Kubernetes Cluster Setup

```bash
# Create EKS cluster using eksctl
exksctl create cluster \
  --name governance-prod \
  --version 1.27 \
  --region us-east-1 \
  --nodegroup-name standard \
  --node-type t3.xlarge \
  --nodes 3 \
  --nodes-min 3 \
  --nodes-max 10 \
  --managed

# Verify cluster
kubectl cluster-info
```

### 2. Install Service Mesh (Istio)

```bash
# Install Istio
istioctl install --set profile=production -y

# Enable sidecar injection
kubectl label namespace default istio-injection=enabled
```

### 3. RDS Database (Multi-AZ)

```bash
aws rds create-db-instance \
  --db-instance-identifier governance-prod \
  --db-instance-class db.r5.2xlarge \
  --engine postgres \
  --multi-az \
  --storage-encrypted \
  --allocated-storage 500 \
  --backup-retention-period 30
```

### 4. ElastiCache Redis Cluster

```bash
aws elasticache create-replication-group \
  --replication-group-description governance-prod-cache \
  --engine redis \
  --engine-version 7.0 \
  --cache-node-type cache.r6g.xlarge \
  --num-cache-clusters 3 \
  --automatic-failover-enabled
```

### 5. Kubernetes Deployment

```bash
# Create namespace
kubectl create namespace governance

# Create secrets
kubectl create secret generic db-credentials \
  --from-literal=username=admin \
  --from-literal=password=$PROD_DB_PASSWORD \
  -n governance

# Create ConfigMaps
kubectl create configmap app-config \
  --from-literal=redis_url=$REDIS_URL \
  --from-literal=jwt_secret=$JWT_SECRET \
  -n governance
```

### 6. Deploy Application

```bash
# Apply Kubernetes manifests
kubectl apply -f kubernetes/namespace.yaml
kubectl apply -f kubernetes/configmap.yaml
kubectl apply -f kubernetes/secrets.yaml
kubectl apply -f kubernetes/deployment.yaml
kubectl apply -f kubernetes/service.yaml
kubectl apply -f kubernetes/hpa.yaml
kubectl apply -f kubernetes/ingress.yaml

# Verify deployment
kubectl get deployments -n governance
kubectl get pods -n governance
kubectl get svc -n governance
```

### 7. SSL/TLS Certificate

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Create ClusterIssuer
kubectl apply -f kubernetes/cert-issuer.yaml
```

## Monitoring & Logging

### 1. Prometheus & Grafana

```bash
# Add Prometheus Helm repo
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install Prometheus
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace

# Access Grafana
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80
# Default credentials: admin/prom-operator
```

### 2. ELK Stack (Elasticsearch, Logstash, Kibana)

```bash
# Install Elasticsearch
helm install elasticsearch elastic/elasticsearch \
  --namespace logging \
  --create-namespace

# Install Kibana
helm install kibana elastic/kibana \
  --namespace logging

# Install Filebeat
helm install filebeat elastic/filebeat \
  --namespace logging
```

### 3. CloudWatch Integration

```bash
# Enable Container Insights
aws eks update-cluster-config \
  --name governance-prod \
  --logging '{"clusterLogging":[{"types":["api","audit"],"enabled":true,"logRetentionInDays":30}]}'
```

## Backup & Recovery

### 1. RDS Backup Strategy

```bash
# Automated backups enabled with 30-day retention
# Manual snapshot creation
aws rds create-db-snapshot \
  --db-instance-identifier governance-prod \
  --db-snapshot-identifier governance-prod-$(date +%Y%m%d)
```

### 2. Redis Persistence

- AOF (Append Only File) enabled
- Snapshots stored in S3
- Cross-region replication configured

### 3. Application Code Backup

```bash
# GitHub Actions automatic backup
# Disaster recovery tested monthly
```

## Health Checks & Status

### 1. Application Health Endpoint

```bash
curl http://localhost:8000/health

# Response:
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 2. Kubernetes Probes

```yaml
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
  initialDelaySeconds: 10
  periodSeconds: 5
```

## Scaling

### 1. Horizontal Pod Autoscaler

```bash
kubectl apply -f kubernetes/hpa.yaml

# Monitor scaling
kubectl get hpa -n governance --watch
```

### 2. Database Scaling

- Read replicas for read-heavy operations
- Vertical scaling for storage (up to 64TB)
- Connection pooling via PgBouncer

## Rollback Procedures

### 1. Kubernetes Rollback

```bash
# View rollout history
kubectl rollout history deployment/governance-app -n governance

# Rollback to previous version
kubectl rollout undo deployment/governance-app -n governance

# Rollback to specific revision
kubectl rollout undo deployment/governance-app --to-revision=3 -n governance
```

### 2. Database Rollback

```bash
# Restore from RDS snapshot
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier governance-prod-rollback \
  --db-snapshot-identifier governance-prod-$(date -d yesterday +%Y%m%d)
```

## Troubleshooting

### 1. Pod Crash Loop

```bash
kubectl logs pod-name -n governance --tail=100
kubectl describe pod pod-name -n governance
kubectl events -n governance --sort-by='.lastTimestamp'
```

### 2. Database Connection Issues

```bash
# Check connection string
echo $DATABASE_URL

# Test connection
psql -h $DB_HOST -U $DB_USER -d governance_db -c "SELECT version();"
```

### 3. Memory/CPU Issues

```bash
kubectl top nodes
kubectl top pods -n governance
kubectl describe node node-name
```

## Deployment Checklist

- [ ] Environment variables configured
- [ ] SSL certificates installed
- [ ] Database migrations completed
- [ ] Cache warmed up
- [ ] Monitoring and alerts configured
- [ ] Backup strategy verified
- [ ] Load testing completed
- [ ] Security scan passed
- [ ] Documentation updated
- [ ] Team notification sent
- [ ] Rollback plan tested
- [ ] Post-deployment verification successful

## Support & Resources

- **Documentation**: https://github.com/romanchaa997/enviro-governance-platform/wiki
- **Issues**: https://github.com/romanchaa997/enviro-governance-platform/issues
- **Slack Channel**: #governance-platform-ops
- **On-Call Runbook**: https://wiki.example.com/governance-runbook
