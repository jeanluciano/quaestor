# Generic Performance Optimization

**Load this file when:** Optimizing performance in any language or need language-agnostic patterns

## Universal Principles

### Measure First
- Never optimize without profiling
- Establish baseline metrics before changes
- Focus on bottlenecks, not micro-optimizations
- Use 80/20 rule: 80% of time spent in 20% of code

### Performance Budgets
```yaml
response_time_targets:
  api_endpoint: "<200ms (p95)"
  page_load: "<2 seconds"
  database_query: "<50ms (p95)"
  cache_lookup: "<10ms"

resource_limits:
  max_memory: "512MB per process"
  max_cpu: "80% sustained"
  max_connections: "100 per instance"
```

## Database Optimization

### Indexing Strategy
```sql
-- Identify slow queries
-- PostgreSQL
SELECT query, mean_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- Add indexes for frequently queried columns
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_orders_user_created ON orders(user_id, created_at);

-- Composite indexes for common query patterns
CREATE INDEX idx_search ON products(category, price, created_at);
```

### Query Optimization
```sql
-- Use EXPLAIN to understand query plans
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'user@example.com';

-- Avoid SELECT *
-- Bad
SELECT * FROM users;

-- Good
SELECT id, name, email FROM users;

-- Use LIMIT for pagination
SELECT id, name FROM users ORDER BY created_at DESC LIMIT 20 OFFSET 0;

-- Use EXISTS instead of COUNT for checking existence
-- Bad
SELECT COUNT(*) FROM orders WHERE user_id = 123;

-- Good
SELECT EXISTS(SELECT 1 FROM orders WHERE user_id = 123);
```

### Connection Pooling
```yaml
connection_pool_config:
  min_connections: 5
  max_connections: 20
  connection_timeout: 30s
  idle_timeout: 10m
  max_lifetime: 1h
```

## Caching Strategies

### Multi-Level Caching
```yaml
caching_layers:
  L1_application:
    type: "In-Memory (LRU)"
    size: "100MB"
    ttl: "5 minutes"
    use_case: "Hot data, session data"

  L2_distributed:
    type: "Redis"
    ttl: "1 hour"
    use_case: "Shared data across instances"

  L3_database:
    type: "Query Result Cache"
    ttl: "15 minutes"
    use_case: "Expensive query results"

  L4_cdn:
    type: "CDN"
    ttl: "24 hours"
    use_case: "Static assets, public API responses"
```

### Cache Invalidation Patterns
```yaml
strategies:
  time_based:
    description: "TTL-based expiration"
    use_case: "Data with predictable change patterns"
    example: "Weather data, stock prices"

  event_based:
    description: "Invalidate on data change events"
    use_case: "Real-time consistency required"
    example: "User profile updates"

  write_through:
    description: "Update cache on write"
    use_case: "Strong consistency needed"
    example: "Shopping cart, user sessions"

  lazy_refresh:
    description: "Refresh on cache miss"
    use_case: "Acceptable stale data"
    example: "Analytics dashboards"
```

## Network Optimization

### HTTP/2 and HTTP/3
```yaml
benefits:
  - Multiplexing: Multiple requests over single connection
  - Header compression: Reduced overhead
  - Server push: Proactive resource sending
  - Binary protocol: Faster parsing
```

### Compression
```yaml
compression_config:
  enabled: true
  min_size: "1KB"  # Don't compress tiny responses
  types:
    - "text/html"
    - "text/css"
    - "application/javascript"
    - "application/json"
  level: 6  # Balance speed vs size
```

### Connection Management
```yaml
keep_alive:
  enabled: true
  timeout: "60s"
  max_requests: 100

timeouts:
  connect: "10s"
  read: "30s"
  write: "30s"
  idle: "120s"
```

## Monitoring and Observability

### Key Metrics to Track
```yaml
application_metrics:
  - response_time_p50
  - response_time_p95
  - response_time_p99
  - error_rate
  - throughput_rps

system_metrics:
  - cpu_utilization
  - memory_utilization
  - disk_io
  - network_io

database_metrics:
  - query_execution_time
  - connection_pool_usage
  - slow_query_count
  - cache_hit_rate
```

### Alert Thresholds
```yaml
alerts:
  critical:
    - metric: "error_rate"
      threshold: ">5%"
      duration: "2 minutes"

    - metric: "response_time_p99"
      threshold: ">1000ms"
      duration: "5 minutes"

  warning:
    - metric: "cpu_utilization"
      threshold: ">80%"
      duration: "10 minutes"

    - metric: "memory_utilization"
      threshold: ">85%"
      duration: "5 minutes"
```

## Load Balancing

### Strategies
```yaml
round_robin:
  description: "Distribute requests evenly"
  use_case: "Homogeneous backend servers"

least_connections:
  description: "Route to server with fewest connections"
  use_case: "Varying request processing times"

ip_hash:
  description: "Consistent routing based on client IP"
  use_case: "Session affinity required"

weighted:
  description: "Route based on server capacity"
  use_case: "Heterogeneous server specs"
```

### Health Checks
```yaml
health_check:
  interval: "10s"
  timeout: "5s"
  unhealthy_threshold: 3
  healthy_threshold: 2
  path: "/health"
```

## CDN Configuration

### Caching Rules
```yaml
static_assets:
  pattern: "*.{js,css,png,jpg,svg,woff2}"
  cache_control: "public, max-age=31536000, immutable"

api_responses:
  pattern: "/api/public/*"
  cache_control: "public, max-age=300, s-maxage=600"

html_pages:
  pattern: "*.html"
  cache_control: "public, max-age=60, s-maxage=300"
```

### Geographic Distribution
```yaml
regions:
  - us-east: "Primary"
  - us-west: "Failover"
  - eu-west: "Regional"
  - ap-southeast: "Regional"

routing:
  policy: "latency-based"
  fallback: "round-robin"
```

## Horizontal Scaling Patterns

### Stateless Services
```yaml
principles:
  - No local state storage
  - Session data in external store (Redis, database)
  - Any instance can handle any request
  - Easy to add/remove instances
```

### Message Queues
```yaml
use_cases:
  - Decouple services
  - Handle traffic spikes
  - Async processing
  - Retry logic

patterns:
  work_queue:
    description: "Distribute tasks to workers"
    example: "Image processing, email sending"

  pub_sub:
    description: "Event broadcasting"
    example: "User registration notifications"
```

## Anti-Patterns to Avoid

### N+1 Query Problem
```sql
-- Bad: N+1 queries (1 for users + N for profiles)
SELECT * FROM users;
-- Then for each user:
SELECT * FROM profiles WHERE user_id = ?;

-- Good: Single join query
SELECT u.*, p.*
FROM users u
LEFT JOIN profiles p ON u.id = p.user_id;
```

### Chatty Interfaces
```yaml
bad:
  requests: 100
  description: "100 separate API calls to get data"
  latency: "100 * 50ms = 5000ms"

good:
  requests: 1
  description: "Single batch API call"
  latency: "200ms"
```

### Synchronous External Calls
```yaml
bad:
  pattern: "Sequential blocking calls"
  time: "call1 (500ms) + call2 (500ms) + call3 (500ms) = 1500ms"

good:
  pattern: "Parallel async calls"
  time: "max(call1, call2, call3) = 500ms"
```

## Performance Testing Strategy

### Load Testing
```yaml
scenarios:
  smoke_test:
    users: 1
    duration: "1 minute"
    purpose: "Verify system works"

  load_test:
    users: "normal_traffic"
    duration: "15 minutes"
    purpose: "Performance under normal load"

  stress_test:
    users: "2x_normal"
    duration: "30 minutes"
    purpose: "Find breaking point"

  spike_test:
    users: "0 → 1000 → 0"
    duration: "10 minutes"
    purpose: "Handle sudden traffic spikes"

  endurance_test:
    users: "normal_traffic"
    duration: "24 hours"
    purpose: "Memory leaks, degradation"
```

### Performance Regression Tests
```yaml
approach:
  - Baseline metrics from production
  - Run automated perf tests in CI
  - Compare against baseline
  - Fail build if regression > threshold

thresholds:
  response_time: "+10%"
  throughput: "-5%"
  error_rate: "+1%"
```

## Checklist

**Initial Assessment:**
- [ ] Identify performance requirements
- [ ] Establish current baseline metrics
- [ ] Profile to find bottlenecks

**Database Optimization:**
- [ ] Add indexes for common queries
- [ ] Implement connection pooling
- [ ] Cache query results
- [ ] Use batch operations

**Caching:**
- [ ] Implement multi-level caching
- [ ] Define cache invalidation strategy
- [ ] Monitor cache hit rates

**Network:**
- [ ] Enable compression
- [ ] Use HTTP/2 or HTTP/3
- [ ] Implement CDN for static assets
- [ ] Configure appropriate timeouts

**Monitoring:**
- [ ] Track key performance metrics
- [ ] Set up alerts for anomalies
- [ ] Implement distributed tracing
- [ ] Create performance dashboards

**Testing:**
- [ ] Run load tests
- [ ] Conduct stress tests
- [ ] Set up performance regression tests
- [ ] Monitor in production

---

*Language-agnostic performance optimization patterns applicable to any technology stack*
