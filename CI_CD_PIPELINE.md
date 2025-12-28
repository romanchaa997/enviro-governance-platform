# CI/CD Pipeline Documentation

## Overview

Automated continuous integration and continuous deployment pipeline for the Enviro-Governance Platform using GitHub Actions.

## Pipeline Architecture

```
Pull Request → Lint/Format → Unit Tests → Integration Tests → Code Quality
     ↓
    Main Branch → Build → Deploy to Staging → E2E Tests → Deploy to Production
```

## Workflow Files

### 1. Lint & Format Check
**File**: `.github/workflows/lint.yml`

```yaml
name: Lint & Format Check

on:
  pull_request:
    paths:
      - '**.py'
      - '**.js'
      - '**.ts'
      - '**.tsx'

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - uses: actions/setup-node@v3
        with:
          node-version: '16'
      
      - name: Install linting tools
        run: |
          pip install flake8 black isort
          npm install -g eslint prettier
      
      - name: Python linting
        run: |
          flake8 backend/ --count --show-source --statistics
          black --check backend/
          isort --check-only backend/
      
      - name: JavaScript/TypeScript linting
        run: |
          cd frontend
          eslint src/ --max-warnings 0
          prettier --check src/
```

### 2. Unit Tests
**File**: `.github/workflows/unit-tests.yml`

```yaml
name: Unit Tests

on:
  pull_request:
  push:
    branches: [main]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.10', '3.11']
    
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-asyncio
      
      - name: Run unit tests
        run: |
          cd backend
          pytest tests/unit/ -v --cov=app --cov-report=xml --cov-report=term
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./backend/coverage.xml
          flags: backend
          fail_ci_if_error: true

  frontend-tests:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '16'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
      
      - name: Run tests
        run: |
          cd frontend
          npm run test -- --coverage --watchAll=false
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./frontend/coverage/coverage-final.json
          flags: frontend
          fail_ci_if_error: true
```

### 3. Integration Tests
**File**: `.github/workflows/integration-tests.yml`

```yaml
name: Integration Tests

on:
  pull_request:

jobs:
  integration-tests:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_DB: test_governance
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_password
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379
      
      rabbitmq:
        image: rabbitmq:3.12-alpine
        env:
          RABBITMQ_DEFAULT_USER: test_user
          RABBITMQ_DEFAULT_PASS: test_password
        ports:
          - 5672:5672
    
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-asyncio
      
      - name: Run database migrations
        env:
          DATABASE_URL: postgresql://test_user:test_password@localhost:5432/test_governance
        run: |
          cd backend
          alembic upgrade head
      
      - name: Run integration tests
        env:
          DATABASE_URL: postgresql://test_user:test_password@localhost:5432/test_governance
          REDIS_URL: redis://localhost:6379
          RABBITMQ_URL: amqp://test_user:test_password@localhost:5672//
        run: |
          cd backend
          pytest tests/integration/ -v --tb=short
```

### 4. Security Scanning
**File**: `.github/workflows/security.yml`

```yaml
name: Security Scan

on:
  pull_request:
  schedule:
    - cron: '0 0 * * *'  # Daily at midnight

jobs:
  security-scan:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'
      
      - name: Upload Trivy results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'
      
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Run Bandit security linter
        run: |
          pip install bandit
          bandit -r backend/ -f json -o bandit-report.json || true
```

### 5. Build & Push Docker Images
**File**: `.github/workflows/build.yml`

```yaml
name: Build & Push Docker Images

on:
  push:
    branches: [main]
    tags: ['v*']

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: Log in to GitHub Container Registry
        uses: docker/login-action@v2
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v4
        with:
          images: ghcr.io/${{ github.repository }}
          tags: |
            type=ref,event=branch
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=sha
      
      - name: Build and push backend
        uses: docker/build-push-action@v4
        with:
          context: ./backend
          push: true
          tags: ghcr.io/${{ github.repository }}/backend:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
      
      - name: Build and push frontend
        uses: docker/build-push-action@v4
        with:
          context: ./frontend
          push: true
          tags: ghcr.io/${{ github.repository }}/frontend:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

### 6. Deploy to Staging
**File**: `.github/workflows/deploy-staging.yml`

```yaml
name: Deploy to Staging

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: staging
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          role-to-assume: arn:aws:iam::${{ secrets.AWS_ACCOUNT_ID }}:role/github-actions-role
          aws-region: us-east-1
      
      - name: Update ECS task definition
        run: |
          BACKEND_IMAGE="ghcr.io/${{ github.repository }}/backend:${{ github.sha }}"
          FRONTEND_IMAGE="ghcr.io/${{ github.repository }}/frontend:${{ github.sha }}"
          
          aws ecs update-service \
            --cluster governance-staging \
            --service governance-app \
            --force-new-deployment
      
      - name: Wait for deployment
        run: |
          aws ecs wait services-stable \
            --cluster governance-staging \
            --services governance-app
      
      - name: Run smoke tests
        run: |
          curl -f https://staging.governance.example.com/health || exit 1
```

### 7. Deploy to Production
**File**: `.github/workflows/deploy-production.yml`

```yaml
name: Deploy to Production

on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          role-to-assume: arn:aws:iam::${{ secrets.AWS_ACCOUNT_ID }}:role/github-actions-role
          aws-region: us-east-1
      
      - name: Create deployment
        uses: actions/github-script@v6
        with:
          script: |
            const deployment = await github.rest.repos.createDeployment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              ref: context.ref,
              environment: 'production',
              production_environment: true,
              required_contexts: []
            });
            console.log(deployment);
      
      - name: Update Kubernetes deployment
        run: |
          aws eks update-kubeconfig --name governance-prod
          
          kubectl set image deployment/governance-app \
            backend=ghcr.io/${{ github.repository }}/backend:${{ github.event.release.tag_name }} \
            frontend=ghcr.io/${{ github.repository }}/frontend:${{ github.event.release.tag_name }} \
            -n governance
          
          kubectl rollout status deployment/governance-app -n governance
      
      - name: Run production smoke tests
        run: |
          curl -f https://governance.example.com/health || exit 1
```

## Pipeline Triggers

| Workflow | Trigger | Branch | Duration |
|----------|---------|--------|----------|
| Lint | Push, PR | All | ~5 min |
| Unit Tests | Push, PR | All | ~10 min |
| Integration Tests | PR | All | ~15 min |
| Security Scan | PR, Daily | All | ~10 min |
| Build | Push | main | ~15 min |
| Deploy Staging | Push | main | ~20 min |
| Deploy Production | Release | tags | ~30 min |

## Required Secrets

**GitHub Secrets**:
- `AWS_ACCOUNT_ID`: AWS account ID
- `CODECOV_TOKEN`: Codecov token for coverage reports

**AWS Secrets Manager**:
- `governance/db/password`: Database password
- `governance/jwt/secret`: JWT secret key
- `governance/github/token`: GitHub API token

## Status Checks

All PRs require passing:
- ✅ Lint & Format
- ✅ Unit Tests (Backend)
- ✅ Unit Tests (Frontend)
- ✅ Integration Tests
- ✅ Security Scan
- ✅ Code Coverage (80%+ required)

## Rollback Procedure

```bash
# Revert to previous release
git revert <commit-sha>
git push origin main

# Or trigger rollback workflow
gh workflow run rollback.yml -f version=v1.2.3
```

## Monitoring & Alerts

- **Slack Notifications**: Pipeline failures sent to #governance-deployments
- **Email Alerts**: Critical failures to ops@example.com
- **DataDog Integration**: Performance metrics tracked

## Performance Targets

- Build time: < 15 minutes
- Test suite: < 30 minutes
- Deployment: < 10 minutes
- Overall pipeline: < 60 minutes

