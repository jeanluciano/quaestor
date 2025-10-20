# Python Performance Optimization

**Load this file when:** Optimizing performance in Python projects

## Profiling Tools

### Execution Time Profiling
```bash
# cProfile - Built-in profiler
python -m cProfile -o profile.stats script.py
python -m pstats profile.stats

# py-spy - Sampling profiler (no code changes needed)
py-spy record -o profile.svg -- python script.py
py-spy top -- python script.py

# line_profiler - Line-by-line profiling
kernprof -l -v script.py
```

### Memory Profiling
```bash
# memory_profiler - Line-by-line memory usage
python -m memory_profiler script.py

# memray - Modern memory profiler
memray run script.py
memray flamegraph output.bin

# tracemalloc - Built-in memory tracking
# (use in code, see example below)
```

### Benchmarking
```bash
# pytest-benchmark
pytest tests/ --benchmark-only

# timeit - Quick microbenchmarks
python -m timeit "'-'.join(str(n) for n in range(100))"
```

## Python-Specific Optimization Patterns

### Async/Await Patterns
```python
import asyncio
import aiohttp

# Good: Parallel async operations
async def fetch_all(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(session, url) for url in urls]
        return await asyncio.gather(*tasks)

# Bad: Sequential async (defeats the purpose)
async def fetch_all_bad(urls):
    results = []
    async with aiohttp.ClientSession() as session:
        for url in urls:
            results.append(await fetch_url(session, url))
    return results
```

### List Comprehensions vs Generators
```python
# Generator (memory efficient for large datasets)
def process_large_file(filename):
    return (process_line(line) for line in open(filename))

# List comprehension (when you need all data in memory)
def process_small_file(filename):
    return [process_line(line) for line in open(filename)]

# Use itertools for complex generators
from itertools import islice, chain
first_10 = list(islice(generate_data(), 10))
```

### Efficient Data Structures
```python
# Use sets for membership testing
# Bad: O(n)
if item in my_list:  # Slow for large lists
    ...

# Good: O(1)
if item in my_set:  # Fast
    ...

# Use deque for queue operations
from collections import deque
queue = deque()
queue.append(item)      # O(1)
queue.popleft()         # O(1) vs list.pop(0) which is O(n)

# Use defaultdict to avoid key checks
from collections import defaultdict
counter = defaultdict(int)
counter[key] += 1  # No need to check if key exists
```

## GIL (Global Interpreter Lock) Considerations

### CPU-Bound Work
```python
# Use multiprocessing for CPU-bound tasks
from multiprocessing import Pool

def cpu_intensive_task(data):
    # Heavy computation
    return result

with Pool(processes=4) as pool:
    results = pool.map(cpu_intensive_task, data_list)
```

### I/O-Bound Work
```python
# Use asyncio or threading for I/O-bound tasks
import asyncio

async def io_bound_task(url):
    # Network I/O, file I/O
    return result

results = await asyncio.gather(*[io_bound_task(url) for url in urls])
```

## Common Python Anti-Patterns

### String Concatenation
```python
# Bad: O(n²) for n strings
result = ""
for s in strings:
    result += s

# Good: O(n)
result = "".join(strings)
```

### Unnecessary Lambda
```python
# Bad: Extra function call overhead
sorted_items = sorted(items, key=lambda x: x.value)

# Good: Direct attribute access
from operator import attrgetter
sorted_items = sorted(items, key=attrgetter('value'))
```

### Loop Invariant Code
```python
# Bad: Repeated calculation in loop
for item in items:
    expensive_result = expensive_function()
    process(item, expensive_result)

# Good: Calculate once
expensive_result = expensive_function()
for item in items:
    process(item, expensive_result)
```

## Performance Measurement

### Tracemalloc for Memory Tracking
```python
import tracemalloc

# Start tracking
tracemalloc.start()

# Your code here
data = [i for i in range(1000000)]

# Get memory usage
current, peak = tracemalloc.get_traced_memory()
print(f"Current: {current / 1024 / 1024:.2f} MB")
print(f"Peak: {peak / 1024 / 1024:.2f} MB")

tracemalloc.stop()
```

### Context Manager for Timing
```python
import time
from contextlib import contextmanager

@contextmanager
def timer(name):
    start = time.perf_counter()
    yield
    elapsed = time.perf_counter() - start
    print(f"{name}: {elapsed:.4f}s")

# Usage
with timer("Database query"):
    results = db.query(...)
```

## Database Optimization (Python-Specific)

### SQLAlchemy Best Practices
```python
# Bad: N+1 queries
for user in session.query(User).all():
    print(user.profile.bio)  # Separate query for each

# Good: Eager loading
from sqlalchemy.orm import joinedload

users = session.query(User).options(
    joinedload(User.profile)
).all()

# Good: Batch operations
session.bulk_insert_mappings(User, user_dicts)
session.commit()
```

## Caching Strategies

### Function Caching
```python
from functools import lru_cache, cache

# LRU cache with size limit
@lru_cache(maxsize=128)
def expensive_computation(n):
    # Heavy computation
    return result

# Unlimited cache (Python 3.9+)
@cache
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Manual cache with expiration
from cachetools import TTLCache
cache = TTLCache(maxsize=100, ttl=300)  # 5 minutes
```

## Performance Testing

### pytest-benchmark
```python
def test_processing_performance(benchmark):
    # Benchmark automatically handles iterations
    result = benchmark(process_data, large_dataset)
    assert result is not None

# Compare against baseline
def test_against_baseline(benchmark):
    benchmark.pedantic(
        process_data,
        args=(dataset,),
        iterations=10,
        rounds=100
    )
```

### Load Testing with Locust
```python
from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def load_homepage(self):
        self.client.get("/")

    @task(3)  # 3x more likely than homepage
    def load_api(self):
        self.client.get("/api/data")
```

## Performance Checklist

**Before Optimizing:**
- [ ] Profile to identify actual bottlenecks (don't guess!)
- [ ] Measure baseline performance
- [ ] Set performance targets

**Python-Specific Optimizations:**
- [ ] Use generators for large datasets
- [ ] Replace loops with list comprehensions where appropriate
- [ ] Use appropriate data structures (set, deque, defaultdict)
- [ ] Implement caching with @lru_cache or @cache
- [ ] Use async/await for I/O-bound operations
- [ ] Use multiprocessing for CPU-bound operations
- [ ] Avoid string concatenation in loops
- [ ] Minimize attribute lookups in hot loops
- [ ] Use __slots__ for classes with many instances

**After Optimizing:**
- [ ] Re-profile to verify improvements
- [ ] Check memory usage hasn't increased significantly
- [ ] Ensure code readability is maintained
- [ ] Add performance regression tests

## Tools and Libraries

**Profiling:**
- `cProfile` - Built-in execution profiler
- `py-spy` - Sampling profiler without code changes
- `memory_profiler` - Memory usage line-by-line
- `memray` - Modern memory profiler with flamegraphs

**Performance Testing:**
- `pytest-benchmark` - Benchmark tests
- `locust` - Load testing framework
- `hyperfine` - Command-line benchmarking

**Optimization:**
- `numpy` - Vectorized operations for numerical data
- `numba` - JIT compilation for numerical functions
- `cython` - Compile Python to C for speed

---

*Python-specific performance optimization with profiling tools and patterns*
