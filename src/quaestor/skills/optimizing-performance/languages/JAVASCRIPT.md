# JavaScript/Node.js Performance Optimization

**Load this file when:** Optimizing performance in JavaScript or Node.js projects

## Profiling Tools

### Node.js Built-in Profiler
```bash
# CPU profiling
node --prof app.js
node --prof-process isolate-0x*.log > processed.txt

# Inspect with Chrome DevTools
node --inspect app.js
# Open chrome://inspect

# Heap snapshots
node --inspect --inspect-brk app.js
# Take heap snapshots in DevTools
```

### Clinic.js Suite
```bash
# Install clinic
npm install -g clinic

# Doctor - Overall health check
clinic doctor -- node app.js

# Flame - Flamegraph profiling
clinic flame -- node app.js

# Bubbleprof - Async operations
clinic bubbleprof -- node app.js

# Heap profiler
clinic heapprofiler -- node app.js
```

### Performance Measurement
```bash
# 0x - Flamegraph generator
npx 0x app.js

# autocannon - HTTP load testing
npx autocannon http://localhost:3000

# lighthouse - Frontend performance
npx lighthouse https://example.com
```

## V8 Optimization Patterns

### Hidden Classes and Inline Caches
```javascript
// Bad: Dynamic property addition breaks hidden class
function Point(x, y) {
    this.x = x;
    this.y = y;
}
const p1 = new Point(1, 2);
p1.z = 3;  // Deoptimizes!

// Good: Consistent object shape
function Point(x, y, z = 0) {
    this.x = x;
    this.y = y;
    this.z = z;  // Always present
}
```

### Avoid Polymorphism in Hot Paths
```javascript
// Bad: Type changes break optimization
function add(a, b) {
    return a + b;
}
add(1, 2);      // Optimized for numbers
add("a", "b");  // Deoptimized! Now handles strings too

// Good: Separate functions for different types
function addNumbers(a, b) {
    return a + b;  // Always numbers
}

function concatStrings(a, b) {
    return a + b;  // Always strings
}
```

### Array Optimization
```javascript
// Bad: Mixed types in array
const mixed = [1, "two", 3, "four"];  // Slow property access

// Good: Homogeneous arrays
const numbers = [1, 2, 3, 4];  // Fast element access
const strings = ["one", "two", "three"];

// Use typed arrays for numeric data
const buffer = new Float64Array(1000);  // Faster than regular arrays
```

## Event Loop Optimization

### Avoid Blocking the Event Loop
```javascript
// Bad: Synchronous operations block event loop
const data = fs.readFileSync('large-file.txt');
const result = heavyComputation(data);

// Good: Async operations
const data = await fs.promises.readFile('large-file.txt');
const result = await processAsync(data);

// For CPU-intensive work, use worker threads
const { Worker } = require('worker_threads');
const worker = new Worker('./cpu-intensive.js');
```

### Batch Async Operations
```javascript
// Bad: Sequential async calls
for (const item of items) {
    await processItem(item);  // Waits for each
}

// Good: Parallel execution
await Promise.all(items.map(item => processItem(item)));

// Better: Controlled concurrency with p-limit
const pLimit = require('p-limit');
const limit = pLimit(10);  // Max 10 concurrent

await Promise.all(
    items.map(item => limit(() => processItem(item)))
);
```

## Memory Management

### Avoid Memory Leaks
```javascript
// Bad: Global variables and closures retain memory
let cache = {};  // Never cleared
function addToCache(key, value) {
    cache[key] = value;  // Grows indefinitely
}

// Good: Use WeakMap for caching
const cache = new WeakMap();
function addToCache(obj, value) {
    cache.set(obj, value);  // Auto garbage collected
}

// Good: Implement cache eviction
const LRU = require('lru-cache');
const cache = new LRU({ max: 500 });
```

### Stream Large Data
```javascript
// Bad: Load entire file in memory
const data = await fs.promises.readFile('large-file.txt');
const processed = data.toString().split('\n').map(process);

// Good: Stream processing
const readline = require('readline');
const stream = fs.createReadStream('large-file.txt');
const rl = readline.createInterface({ input: stream });

for await (const line of rl) {
    process(line);  // Process one line at a time
}
```

## Database Query Optimization

### Connection Pooling
```javascript
// Bad: Create new connection per request
async function query(sql) {
    const conn = await mysql.createConnection(config);
    const result = await conn.query(sql);
    await conn.end();
    return result;
}

// Good: Use connection pool
const pool = mysql.createPool(config);
async function query(sql) {
    return pool.query(sql);  // Reuses connections
}
```

### Batch Database Operations
```javascript
// Bad: Multiple round trips
for (const user of users) {
    await db.insert('users', user);
}

// Good: Single batch insert
await db.batchInsert('users', users, 1000);  // Chunks of 1000
```

## HTTP Server Optimization

### Compression
```javascript
const compression = require('compression');
app.use(compression({
    level: 6,  // Balance between speed and compression
    threshold: 1024  // Only compress responses > 1KB
}));
```

### Caching Headers
```javascript
app.get('/static/*', (req, res) => {
    res.setHeader('Cache-Control', 'public, max-age=31536000');
    res.setHeader('ETag', computeETag(file));
    res.sendFile(file);
});
```

### Keep-Alive Connections
```javascript
const http = require('http');
const server = http.createServer({
    keepAlive: true,
    keepAliveTimeout: 60000  // 60 seconds
}, app);
```

## Frontend Performance

### Code Splitting
```javascript
// Dynamic imports for code splitting
const HeavyComponent = lazy(() => import('./HeavyComponent'));

// Route-based code splitting
const routes = [
    {
        path: '/dashboard',
        component: lazy(() => import('./Dashboard'))
    }
];
```

### Memoization
```javascript
// React.memo for expensive components
const ExpensiveComponent = React.memo(({ data }) => {
    return <div>{expensiveRender(data)}</div>;
});

// useMemo for expensive computations
const sortedData = useMemo(() => {
    return data.sort(compare);
}, [data]);

// useCallback for stable function references
const handleClick = useCallback(() => {
    doSomething(id);
}, [id]);
```

### Virtual Scrolling
```javascript
// For large lists, render only visible items
import { FixedSizeList } from 'react-window';

<FixedSizeList
    height={600}
    itemCount={10000}
    itemSize={50}
    width="100%"
>
    {Row}
</FixedSizeList>
```

## Performance Anti-Patterns

### Unnecessary Re-renders
```javascript
// Bad: Creates new object on every render
function MyComponent() {
    const style = { color: 'red' };  // New object each render
    return <div style={style}>Text</div>;
}

// Good: Define outside or use useMemo
const style = { color: 'red' };
function MyComponent() {
    return <div style={style}>Text</div>;
}
```

### Expensive Operations in Render
```javascript
// Bad: Expensive computation in render
function MyComponent({ items }) {
    const sorted = items.sort();  // Sorts on every render!
    return <List data={sorted} />;
}

// Good: Memoize expensive computations
function MyComponent({ items }) {
    const sorted = useMemo(() => items.sort(), [items]);
    return <List data={sorted} />;
}
```

## Benchmarking

### Simple Benchmarks
```javascript
const { performance } = require('perf_hooks');

function benchmark(fn, iterations = 1000) {
    const start = performance.now();
    for (let i = 0; i < iterations; i++) {
        fn();
    }
    const end = performance.now();
    console.log(`Avg: ${(end - start) / iterations}ms`);
}

benchmark(() => myFunction());
```

### Benchmark.js
```javascript
const Benchmark = require('benchmark');
const suite = new Benchmark.Suite;

suite
    .add('Array#forEach', function() {
        [1,2,3].forEach(x => x * 2);
    })
    .add('Array#map', function() {
        [1,2,3].map(x => x * 2);
    })
    .on('complete', function() {
        console.log('Fastest is ' + this.filter('fastest').map('name'));
    })
    .run();
```

## Performance Checklist

**Before Optimizing:**
- [ ] Profile with Chrome DevTools or clinic.js
- [ ] Identify hot paths and bottlenecks
- [ ] Measure baseline performance

**Node.js Optimizations:**
- [ ] Use worker threads for CPU-intensive tasks
- [ ] Implement connection pooling for databases
- [ ] Enable compression middleware
- [ ] Use streams for large data processing
- [ ] Implement caching (Redis, in-memory)
- [ ] Batch async operations with controlled concurrency
- [ ] Monitor event loop lag

**Frontend Optimizations:**
- [ ] Implement code splitting
- [ ] Use React.memo for expensive components
- [ ] Implement virtual scrolling for large lists
- [ ] Optimize bundle size (tree shaking, minification)
- [ ] Use Web Workers for heavy computations
- [ ] Implement service workers for offline caching
- [ ] Lazy load images and components

**After Optimizing:**
- [ ] Re-profile to verify improvements
- [ ] Check memory usage for leaks
- [ ] Run load tests (autocannon, artillery)
- [ ] Monitor with APM tools

## Tools and Libraries

**Profiling:**
- `clinic.js` - Performance profiling suite
- `0x` - Flamegraph profiler
- `node --inspect` - Chrome DevTools integration
- `autocannon` - HTTP load testing

**Optimization:**
- `p-limit` - Concurrency control
- `lru-cache` - LRU caching
- `compression` - Response compression
- `react-window` - Virtual scrolling
- `workerpool` - Worker thread pools

**Monitoring:**
- `prom-client` - Prometheus metrics
- `newrelic` / `datadog` - APM
- `clinic-doctor` - Health diagnostics

---

*JavaScript/Node.js-specific performance optimization with V8 patterns and profiling tools*
