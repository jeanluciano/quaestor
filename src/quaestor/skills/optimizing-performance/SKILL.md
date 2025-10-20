---
name: Optimizing Performance
description: Optimize performance with profiling, caching strategies, database query optimization, and bottleneck analysis. Use when improving response times, implementing caching layers, or scaling for high load.
---

# Optimizing Performance

I help you identify and fix performance bottlenecks using language-specific profiling tools, optimization patterns, and best practices.

## When to Use Me

**Performance analysis:**
- "Profile this code for bottlenecks"
- "Analyze performance issues"
- "Why is this slow?"

**Optimization:**
- "Optimize database queries"
- "Improve response time"
- "Reduce memory usage"

**Scaling:**
- "Implement caching strategy"
- "Optimize for high load"
- "Scale this service"

## How I Work - Progressive Loading

I load only the performance guidance relevant to your language:

```yaml
Language Detection:
  "Python project" → Load @languages/PYTHON.md
  "Rust project" → Load @languages/RUST.md
  "JavaScript/Node.js" → Load @languages/JAVASCRIPT.md
  "Go project" → Load @languages/GO.md
  "Any language" → Load @languages/GENERIC.md
```

**Don't load all files!** Start with language detection, then load specific guidance.

## Core Principles

### 1. Measure First
**Never optimize without data.** Profile to find actual bottlenecks, don't guess.

- Establish baseline metrics
- Profile to identify hot paths
- Focus on the 20% of code that takes 80% of time
- Measure improvements after optimization

### 2. Performance Budgets
Set clear targets before optimizing:

```yaml
targets:
  api_response: "<200ms (p95)"
  page_load: "<2 seconds"
  database_query: "<50ms (p95)"
  cache_lookup: "<10ms"
```

### 3. Trade-offs
Balance performance vs:
- Code readability
- Maintainability
- Development time
- Memory usage

Premature optimization is the root of all evil. Optimize when:
- Profiling shows clear bottleneck
- Performance requirement not met
- User experience degraded

## Quick Wins (Language-Agnostic)

### Database
- Add indexes for frequently queried columns
- Implement connection pooling
- Use batch operations instead of loops
- Cache expensive query results

### Caching
- Implement multi-level caching (L1: in-memory, L2: Redis, L3: database, L4: CDN)
- Define cache invalidation strategy
- Monitor cache hit rates

### Network
- Enable compression for responses
- Use HTTP/2 or HTTP/3
- Implement CDN for static assets
- Configure appropriate timeouts

## Language-Specific Guidance

### Python
**Load:** `@languages/PYTHON.md`

**Quick reference:**
- Profiling: `cProfile`, `py-spy`, `memory_profiler`
- Patterns: Generators, async/await, list comprehensions
- Anti-patterns: String concatenation in loops, GIL contention
- Tools: `pytest-benchmark`, `locust`

### Rust
**Load:** `@languages/RUST.md`

**Quick reference:**
- Profiling: `cargo bench`, `flamegraph`, `perf`
- Patterns: Zero-cost abstractions, iterator chains, preallocated collections
- Anti-patterns: Unnecessary allocations, large enum variants
- Tools: `criterion`, `rayon`, `parking_lot`

### JavaScript/Node.js
**Load:** `@languages/JAVASCRIPT.md`

**Quick reference:**
- Profiling: `clinic.js`, `0x`, Chrome DevTools
- Patterns: Event loop optimization, worker threads, streaming
- Anti-patterns: Blocking event loop, memory leaks, unnecessary re-renders
- Tools: `autocannon`, `react-window`, `p-limit`

### Go
**Load:** `@languages/GO.md`

**Quick reference:**
- Profiling: `pprof`, `go test -bench`, `go tool trace`
- Patterns: Goroutine pools, buffered channels, `sync.Pool`
- Anti-patterns: Unlimited goroutines, defer in loops, lock contention
- Tools: `benchstat`, `sync.Map`, `strings.Builder`

### Generic Patterns
**Load:** `@languages/GENERIC.md`

**When to use:** Database optimization, caching strategies, load balancing, monitoring - applicable to any language.

## Optimization Workflow

### Phase 1: Baseline
1. Define performance requirements
2. Measure current performance
3. Identify user-facing metrics (response time, throughput)

### Phase 2: Profile
1. Use language-specific profiling tools
2. Identify hot paths (where time is spent)
3. Find memory bottlenecks
4. Check for resource leaks

### Phase 3: Optimize
1. Focus on biggest bottleneck first
2. Apply language-specific optimizations
3. Implement caching where appropriate
4. Optimize database queries

### Phase 4: Verify
1. Re-profile to measure improvements
2. Run performance regression tests
3. Monitor in production
4. Set up alerts for degradation

## Common Bottlenecks

### Database
- Missing indexes
- N+1 query problem
- No connection pooling
- Expensive joins
→ **Load** `@languages/GENERIC.md` for DB optimization

### Memory
- Memory leaks
- Excessive allocations
- Large object graphs
- No pooling
→ **Load** language-specific file for memory management

### Network
- No compression
- Chatty API calls
- Synchronous external calls
- No CDN
→ **Load** `@languages/GENERIC.md` for network optimization

### Concurrency
- Lock contention
- Excessive threading/goroutines
- Blocking operations
- Poor work distribution
→ **Load** language-specific file for concurrency patterns

## Success Criteria

**Optimization complete when:**
- ✅ Performance targets met
- ✅ No regressions in functionality
- ✅ Code remains maintainable
- ✅ Improvements verified with profiling
- ✅ Production metrics show improvement
- ✅ Alerts configured for degradation

## Next Steps

- Use profiling tools to identify bottlenecks
- Load language-specific guidance
- Apply targeted optimizations
- Set up monitoring and alerts

---

*Load language-specific files for detailed profiling tools, optimization patterns, and best practices*
