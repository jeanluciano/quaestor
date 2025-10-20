---
name: Performance Optimization
description: Optimize performance with profiling, caching strategies, database query optimization, and bottleneck analysis. Use when improving response times, implementing caching layers, or scaling for high load.
---

# Performance Optimization

## Purpose
Provides performance best practices, profiling techniques, and optimization patterns for building high-performance applications.

## When to Use
- Analyzing performance bottlenecks
- Implementing caching strategies
- Optimizing database queries
- Reducing memory usage
- Improving application responsiveness
- Scaling systems for high load

## Performance Guidelines

### General Principles
- **Measure First**: Always profile before optimizing
- **Focus on Bottlenecks**: Optimize the slowest parts first
- **Trade-offs**: Balance performance vs maintainability
- **Premature Optimization**: Avoid optimizing without data
- **Monitoring**: Continuous performance monitoring in production

### Database Optimization
- ✅ Use connection pooling
- ✅ Implement proper indexing
- ✅ Optimize query patterns (avoid N+1 queries)
- ✅ Use database query caching
- ✅ Implement pagination for large datasets
- ✅ Use read replicas for read-heavy workloads
- ✅ Consider database sharding for scalability

### Memory Management
- ✅ Implement proper resource cleanup
- ✅ Use streaming for large files
- ✅ Avoid memory leaks (close connections, clear references)
- ✅ Monitor memory usage patterns
- ✅ Use memory-efficient data structures
- ✅ Implement garbage collection tuning if needed

### Caching Strategies
- ✅ Cache frequently accessed data
- ✅ Implement cache invalidation strategies
- ✅ Use appropriate cache TTL values
- ✅ Consider multi-level caching (L1/L2)
- ✅ Cache at multiple layers (application, database, CDN)

### Async Operations
- ✅ Use non-blocking I/O where appropriate
- ✅ Implement background job processing
- ✅ Use message queues for async tasks
- ✅ Avoid blocking the main thread
- ✅ Implement timeouts for external calls

## Caching Patterns

### Multi-Level Caching
```yaml
caching_strategy:
  level_1_application:
    type: "In-Memory"
    what_cached: "Hot data, session data"
    ttl: "5 minutes"
    size_limit: "100MB"

  level_2_distributed:
    type: "Redis"
    what_cached: "Shared data, computed results"
    ttl: "1 hour"
    invalidation: "Event-based"

  level_3_database:
    type: "Query Result Cache"
    what_cached: "Expensive query results"
    ttl: "15 minutes"

  level_4_cdn:
    type: "CDN Cache"
    what_cached: "Static assets, API responses"
    ttl: "24 hours"
```

### Cache Invalidation Strategies
```yaml
strategies:
  time_based:
    description: "TTL-based expiration"
    use_case: "Data that changes predictably"

  event_based:
    description: "Invalidate on data change"
    use_case: "Real-time consistency required"

  lazy_refresh:
    description: "Refresh on cache miss"
    use_case: "Acceptable stale data"

  write_through:
    description: "Update cache on write"
    use_case: "Strong consistency needed"
```

## Profiling Techniques

### Python Profiling
```bash
# Profile execution time
python -m cProfile -o profile.stats script.py
python -m pstats profile.stats

# Memory profiling
python -m memory_profiler script.py

# Line profiling
kernprof -l -v script.py
```

### Database Profiling
```sql
-- PostgreSQL
EXPLAIN ANALYZE SELECT ...;

-- MySQL
EXPLAIN SELECT ...;

-- Show slow queries
SHOW FULL PROCESSLIST;
```

### Application Monitoring
```bash
# Monitor system resources
top
htop

# Network monitoring
netstat -an
ss -s

# Application metrics
# Use APM tools: New Relic, DataDog, Prometheus
```

## Performance Patterns

### Connection Pooling
```python
# Database connection pool
pool = ConnectionPool(
    min_connections=5,
    max_connections=20,
    connection_timeout=30,
    idle_timeout=600
)
```

### Lazy Loading
```python
# Load data only when needed
def get_expensive_data():
    if not hasattr(self, '_cached_data'):
        self._cached_data = load_from_database()
    return self._cached_data
```

### Batch Processing
```python
# Process in batches instead of one-by-one
BATCH_SIZE = 1000
for i in range(0, len(items), BATCH_SIZE):
    batch = items[i:i + BATCH_SIZE]
    process_batch(batch)
```

### Async Operations
```python
# Non-blocking operations
async def fetch_data(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()
```

## Performance Budgets

### Response Time Targets
```yaml
performance_targets:
  page_load: "<2 seconds"
  api_response: "<200ms (p95)"
  database_query: "<50ms (p95)"
  cache_lookup: "<10ms"
```

### Resource Limits
```yaml
resource_limits:
  max_memory: "512MB per process"
  max_cpu: "80% sustained"
  max_connections: "100 per instance"
  max_request_size: "10MB"
```

## Optimization Checklist

### Before Optimization
- [ ] Profile to identify bottlenecks
- [ ] Set performance baselines
- [ ] Define success criteria
- [ ] Document current behavior

### During Optimization
- [ ] Optimize identified bottlenecks
- [ ] Implement caching where appropriate
- [ ] Optimize database queries
- [ ] Reduce unnecessary computations
- [ ] Implement async operations

### After Optimization
- [ ] Measure improvements
- [ ] Verify no regressions
- [ ] Update documentation
- [ ] Monitor in production
- [ ] Set up alerts for performance degradation

## Common Performance Anti-Patterns

### N+1 Query Problem
```python
# Bad: N+1 queries
for user in users:
    print(user.profile)  # Separate query for each

# Good: Eager loading
users = User.query.options(joinedload(User.profile)).all()
```

### Synchronous External Calls
```python
# Bad: Blocking calls
result1 = api_call_1()
result2 = api_call_2()

# Good: Parallel execution
results = await asyncio.gather(
    api_call_1(),
    api_call_2()
)
```

### Missing Indexes
```sql
-- Bad: Full table scan
SELECT * FROM users WHERE email = 'user@example.com';

-- Good: Indexed lookup
CREATE INDEX idx_users_email ON users(email);
SELECT * FROM users WHERE email = 'user@example.com';
```

## Monitoring and Alerting

### Key Metrics
```yaml
metrics_to_monitor:
  - response_time_p50
  - response_time_p95
  - response_time_p99
  - error_rate
  - throughput_requests_per_second
  - cpu_utilization
  - memory_utilization
  - database_connection_pool_usage
  - cache_hit_rate
```

### Alert Thresholds
```yaml
alerts:
  - metric: "response_time_p95"
    threshold: ">500ms"
    duration: "5 minutes"

  - metric: "error_rate"
    threshold: ">1%"
    duration: "2 minutes"

  - metric: "cpu_utilization"
    threshold: ">85%"
    duration: "10 minutes"
```

---
*Use this skill for performance analysis and optimization tasks*
