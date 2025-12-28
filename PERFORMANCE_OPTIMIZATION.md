# Performance Optimization Guide

## Executive Summary
The Enviro-Governance Platform targets 10,000 votes/second throughput with <100ms p99 latency. This guide details optimization strategies across the stack, from database tuning to frontend caching.

## Database Optimization

### 1. Query Optimization

```sql
-- BAD: Full table scan
SELECT * FROM votes WHERE decision_id = ?;

-- GOOD: Indexed query
CREATE INDEX idx_votes_decision_id ON votes(decision_id);

-- EXPLAIN ANALYSIS to verify
EXPLAIN ANALYZE SELECT * FROM votes WHERE decision_id = ?;
```

### 2. Connection Pooling

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,  # Maintain 20 connections
    max_overflow=40,  # Allow 40 additional overflow connections
    pool_pre_ping=True,  # Test connections before use
    pool_recycle=3600,  # Recycle connections every hour
)
```

### 3. Batch Operations

```python
# Instead of 1000 individual inserts
from sqlalchemy import insert

votes_data = [
    {"voter_id": "...", "vote": "yes"},
    # 999 more votes
]

# Batch insert (10-100x faster)
stmt = insert(votes_table)
db.execute(stmt, votes_data)
db.commit()
```

### 4. Partitioning Strategy

```sql
-- Time-based partitioning for votes
CREATE TABLE votes_2024_q1 PARTITION OF votes
    FOR VALUES FROM ('2024-01-01') TO ('2024-04-01');

-- Decision-based partitioning
CREATE TABLE votes_region_us PARTITION OF votes
    FOR VALUES IN ('US-EAST', 'US-WEST');
```

## Caching Strategy

### 1. Redis Multi-Level Caching

```python
class VotingCache:
    CACHE_LEVELS = {
        'L1_HOT': 300,      # 5 minutes - active votes
        'L2_WARM': 3600,    # 1 hour - recent decisions
        'L3_COLD': 86400,   # 1 day - historical data
    }

    async def get_decision_results(self, decision_id: str):
        # Try L1 cache
        result = await self.redis.get(f"decision:{decision_id}:hot")
        if result:
            return json.loads(result)
        
        # Try L2 cache
        result = await self.redis.get(f"decision:{decision_id}:warm")
        if result:
            return json.loads(result)
        
        # Query database
        result = await self.db.query_decision(decision_id)
        
        # Populate L1 cache
        await self.redis.setex(
            f"decision:{decision_id}:hot",
            self.CACHE_LEVELS['L1_HOT'],
            json.dumps(result)
        )
        return result
```

### 2. Cache Invalidation Patterns

```python
class CacheInvalidation:
    @staticmethod
    async def on_vote_cast(vote_data):
        decision_id = vote_data.decision_id
        
        # Invalidate all cache levels for this decision
        await redis.delete(f"decision:{decision_id}:hot")
        await redis.delete(f"decision:{decision_id}:warm")
        
        # Invalidate aggregation cache
        await redis.delete(f"agg:{decision_id}:scores")
        
        # Use cache versioning for instant invalidation
        await redis.incr(f"version:{decision_id}")
```

## API Performance

### 1. Response Compression

```python
from fastapi.middleware.gzip import GZIPMiddleware

app.add_middleware(
    GZIPMiddleware,
    minimum_size=1000,  # Only compress responses > 1KB
    compresslevel=6,    # Balance between compression ratio and speed
)
```

### 2. Request/Response Validation Optimization

```python
from pydantic import BaseModel, Field, validator

class VoteRequest(BaseModel):
    voter_id: str = Field(min_length=1, max_length=255)
    vote: str = Field(regex="^(yes|no|abstain)$")
    
    # Use @validator for complex logic
    @validator('voter_id')
    def validate_voter(cls, v):
        # Cache validation results
        cached = cache.get(f"voter_valid:{v}")
        if cached is not None:
            return v
        # Perform validation
        cache.set(f"voter_valid:{v}", True, ttl=3600)
        return v
```

### 3. Pagination Optimization

```python
@app.get("/api/v1/decisions")
async def list_decisions(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),  # Cap page size
    sort_by: str = "created_at",
):
    # Use keyset pagination for large offsets
    # Instead of OFFSET 1000000, use WHERE id > last_id
    
    offset = (page - 1) * per_page
    
    # Bad for large offsets
    # results = db.query(...).offset(offset).limit(per_page)
    
    # Good for large offsets (keyset pagination)
    results = db.query(...).where(
        Decision.id > request.last_id
    ).limit(per_page)
```

## Frontend Optimization

### 1. Code Splitting

```javascript
// React.lazy for route-based splitting
const VotingModule = React.lazy(() => 
    import('./modules/VotingModule')
);

const DashboardModule = React.lazy(() =>
    import('./modules/DashboardModule')
);

function App() {
    return (
        <Suspense fallback={<Spinner />}>
            <Routes>
                <Route path="/voting" element={<VotingModule />} />
                <Route path="/dashboard" element={<DashboardModule />} />
            </Routes>
        </Suspense>
    );
}
```

### 2. Virtual Scrolling for Large Lists

```javascript
import { FixedSizeList } from 'react-window';

function VotingResultsList({ votes }) {
    return (
        <FixedSizeList
            height={600}
            itemCount={votes.length}
            itemSize={50}
            width="100%"
        >
            {({ index, style }) => (
                <div style={style}>
                    {votes[index].voter_id}: {votes[index].vote}
                </div>
            )}
        </FixedSizeList>
    );
}
```

### 3. Web Workers for Heavy Computation

```javascript
// main.js
const worker = new Worker('voting-calculator.worker.js');

worker.postMessage({
    type: 'calculate',
    votes: largeVotesArray,
    weights: weightFactors,
});

worker.onmessage = (event) => {
    const result = event.data;  // Calculated result
    updateUI(result);
};

// voting-calculator.worker.js
self.onmessage = (event) => {
    const { votes, weights } = event.data;
    
    // Heavy computation happens in worker thread
    const result = calculateConsensus(votes, weights);
    
    self.postMessage(result);
};
```

## Message Queue Optimization

### 1. Consumer Groups for Load Distribution

```python
# Kafka consumer group for parallel vote processing
from kafka import KafkaConsumer

consumer = KafkaConsumer(
    'voting-topic',
    group_id='voting-processors',
    auto_offset_reset='earliest',
    max_poll_records=1000,  # Process in batches
    session_timeout_ms=30000,
    fetch_min_bytes=1024 * 100,  # Batch at least 100KB
)

for batch in consumer:
    # Process 1000 votes at once
    process_vote_batch(batch)
```

### 2. Dead-Letter Queue Implementation

```python
class VoteProcessor:
    async def process_vote(self, vote):
        try:
            await self.store_vote(vote)
        except Exception as e:
            # Send to DLQ for retry
            await self.dlq.publish(
                topic='votes-dlq',
                message=vote,
                retry_count=vote.get('retry_count', 0) + 1
            )
            if vote.get('retry_count', 0) > 3:
                # Log to monitoring system
                logger.error(f"Vote processing failed: {vote}")
```

## Search Optimization (Elasticsearch)

### 1. Index Optimization

```json
{
  "settings": {
    "number_of_shards": 5,
    "number_of_replicas": 1,
    "refresh_interval": "30s",
    "index.codec": "best_compression"
  },
  "mappings": {
    "properties": {
      "decision_id": {
        "type": "keyword",
        "index": true
      },
      "vote_type": {
        "type": "keyword",
        "eager_global_ordinals": true
      },
      "timestamp": {
        "type": "date",
        "format": "epoch_millis"
      }
    }
  }
}
```

### 2. Aggregation Pipeline Optimization

```python
# Avoid expensive aggregations during peak load
async def get_vote_stats(decision_id, cache_ttl=300):
    cache_key = f"stats:{decision_id}"
    
    # Check cache first
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # Pre-calculate and cache
    stats = await elasticsearch.search({
        "aggs": {
            "vote_breakdown": {
                "terms": {"field": "vote_type"},
                "size": 3
            }
        }
    })
    
    await redis.setex(cache_key, cache_ttl, json.dumps(stats))
    return stats
```

## Monitoring & Profiling

### 1. APM Instrumentation

```python
from opentelemetry import trace, metrics
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

jaeger_exporter = JaegerExporter(
    agent_host_name="jaeger-collector",
    agent_port=6831,
)

trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)

@app.post("/api/v1/voting/cast-vote")
@trace.span("cast_vote")
async def cast_vote(vote: VoteRequest):
    # Spans are automatically tracked
    pass
```

### 2. Performance Benchmarking

```python
import asyncio
import time
from statistics import mean, stdev

async def benchmark_vote_casting(num_votes=10000):
    times = []
    
    for _ in range(num_votes):
        start = time.perf_counter()
        await cast_vote(test_vote)
        end = time.perf_counter()
        times.append(end - start)
    
    print(f"Average: {mean(times)*1000:.2f}ms")
    print(f"Std Dev: {stdev(times)*1000:.2f}ms")
    print(f"P99: {sorted(times)[int(len(times)*0.99)]*1000:.2f}ms")
    print(f"Throughput: {num_votes/(sum(times)):.0f} votes/sec")
```

## Scaling Guidelines

### Horizontal Scaling Checklist
- [ ] Database: Read replicas configured
- [ ] Cache: Redis Cluster with auto-rebalancing
- [ ] API: 5+ replicas with auto-scaling policies
- [ ] Message Queue: Multiple consumer groups
- [ ] Load Balancer: Health checks configured

### Performance Targets by Load
```
100 votes/sec:   Single instance sufficient
1,000 votes/sec:   3 API instances, 1 database
10,000 votes/sec:  10+ API instances, replicated DB, Redis cluster
```

## Cost Optimization

### 1. Spot Instances for Non-Critical Services
```yaml
kubernetes:
  nodePool:
    spot:
      enabled: true
      savings: "70%"
      useCase: "background_jobs, analytics"
```

### 2. Reserved Capacity for Predictable Load
```
Monthly voting sessions: 4
Each session: 2 hours
Total monthly: 8 hours
Reserved instances: 3 (covers all sessions)
Savings vs on-demand: 40%
```
