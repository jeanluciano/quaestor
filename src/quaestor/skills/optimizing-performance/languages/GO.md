# Go Performance Optimization

**Load this file when:** Optimizing performance in Go projects

## Profiling Tools

### Built-in pprof
```bash
# CPU profiling
go test -cpuprofile=cpu.prof -bench=.
go tool pprof cpu.prof

# Memory profiling
go test -memprofile=mem.prof -bench=.
go tool pprof mem.prof

# Web UI for profiles
go tool pprof -http=:8080 cpu.prof

# Goroutine profiling
go tool pprof http://localhost:6060/debug/pprof/goroutine

# Heap profiling
go tool pprof http://localhost:6060/debug/pprof/heap
```

### Benchmarking
```go
// Basic benchmark
func BenchmarkFibonacci(b *testing.B) {
    for i := 0; i < b.N; i++ {
        fibonacci(20)
    }
}

// With sub-benchmarks
func BenchmarkSizes(b *testing.B) {
    sizes := []int{10, 100, 1000}
    for _, size := range sizes {
        b.Run(fmt.Sprintf("size=%d", size), func(b *testing.B) {
            for i := 0; i < b.N; i++ {
                process(size)
            }
        })
    }
}

// Reset timer for setup
func BenchmarkWithSetup(b *testing.B) {
    data := setupExpensiveData()
    b.ResetTimer()  // Don't count setup time

    for i := 0; i < b.N; i++ {
        process(data)
    }
}
```

### Runtime Metrics
```go
import (
    "net/http"
    _ "net/http/pprof"  // Import for side effects
    "runtime"
)

func init() {
    // Enable profiling endpoint
    go func() {
        http.ListenAndServe("localhost:6060", nil)
    }()
}

// Monitor goroutines
func printStats() {
    fmt.Printf("Goroutines: %d\n", runtime.NumGoroutine())

    var m runtime.MemStats
    runtime.ReadMemStats(&m)
    fmt.Printf("Alloc: %d MB\n", m.Alloc/1024/1024)
    fmt.Printf("TotalAlloc: %d MB\n", m.TotalAlloc/1024/1024)
}
```

## Memory Management

### Avoiding Allocations
```go
// Bad: Allocates on every call
func process(data []byte) []byte {
    result := make([]byte, len(data))  // New allocation
    copy(result, data)
    return result
}

// Good: Reuse buffer
var bufferPool = sync.Pool{
    New: func() interface{} {
        return make([]byte, 1024)
    },
}

func process(data []byte) {
    buf := bufferPool.Get().([]byte)
    defer bufferPool.Put(buf)
    // Process with buf
}
```

### Preallocate Slices
```go
// Bad: Multiple allocations as slice grows
items := []Item{}
for i := 0; i < 1000; i++ {
    items = append(items, Item{i})  // Reallocates when cap exceeded
}

// Good: Single allocation
items := make([]Item, 0, 1000)
for i := 0; i < 1000; i++ {
    items = append(items, Item{i})  // No reallocation
}

// Or if final size is known
items := make([]Item, 1000)
for i := 0; i < 1000; i++ {
    items[i] = Item{i}
}
```

### String vs []byte
```go
// Bad: String concatenation allocates
var result string
for _, s := range strings {
    result += s  // New allocation each time
}

// Good: Use strings.Builder
var builder strings.Builder
builder.Grow(estimatedSize)  // Preallocate
for _, s := range strings {
    builder.WriteString(s)
}
result := builder.String()

// For byte operations, work with []byte
data := []byte("hello")
data = append(data, " world"...)  // Efficient
```

## Goroutine Optimization

### Worker Pool Pattern
```go
// Bad: Unlimited goroutines
for _, task := range tasks {
    go process(task)  // Could spawn millions!
}

// Good: Limited worker pool
func workerPool(tasks <-chan Task, workers int) {
    var wg sync.WaitGroup
    for i := 0; i < workers; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            for task := range tasks {
                process(task)
            }
        }()
    }
    wg.Wait()
}

// Usage
taskChan := make(chan Task, 100)
go workerPool(taskChan, 10)  // 10 workers
```

### Channel Patterns
```go
// Buffered channels reduce blocking
ch := make(chan int, 100)  // Buffer of 100

// Fan-out pattern for parallel work
func fanOut(in <-chan int, n int) []<-chan int {
    outs := make([]<-chan int, n)
    for i := 0; i < n; i++ {
        out := make(chan int)
        outs[i] = out
        go func() {
            for v := range in {
                out <- process(v)
            }
            close(out)
        }()
    }
    return outs
}

// Fan-in pattern to merge results
func fanIn(channels ...<-chan int) <-chan int {
    out := make(chan int)
    var wg sync.WaitGroup

    for _, ch := range channels {
        wg.Add(1)
        go func(c <-chan int) {
            defer wg.Done()
            for v := range c {
                out <- v
            }
        }(ch)
    }

    go func() {
        wg.Wait()
        close(out)
    }()

    return out
}
```

## Data Structure Optimization

### Map Preallocation
```go
// Bad: Map grows as needed
m := make(map[string]int)
for i := 0; i < 10000; i++ {
    m[fmt.Sprint(i)] = i  // Reallocates periodically
}

// Good: Preallocate
m := make(map[string]int, 10000)
for i := 0; i < 10000; i++ {
    m[fmt.Sprint(i)] = i  // No reallocation
}
```

### Struct Field Alignment
```go
// Bad: Poor alignment (40 bytes due to padding)
type BadLayout struct {
    a bool   // 1 byte + 7 padding
    b int64  // 8 bytes
    c bool   // 1 byte + 7 padding
    d int64  // 8 bytes
    e bool   // 1 byte + 7 padding
}

// Good: Optimal alignment (24 bytes)
type GoodLayout struct {
    b int64  // 8 bytes
    d int64  // 8 bytes
    a bool   // 1 byte
    c bool   // 1 byte
    e bool   // 1 byte + 5 padding
}
```

## I/O Optimization

### Buffered I/O
```go
// Bad: Unbuffered reads
file, _ := os.Open("file.txt")
scanner := bufio.NewScanner(file)

// Good: Buffered with custom size
file, _ := os.Open("file.txt")
reader := bufio.NewReaderSize(file, 64*1024)  // 64KB buffer
scanner := bufio.NewScanner(reader)
```

### Connection Pooling
```go
// HTTP client with connection pooling
client := &http.Client{
    Transport: &http.Transport{
        MaxIdleConns:        100,
        MaxIdleConnsPerHost: 10,
        IdleConnTimeout:     90 * time.Second,
    },
    Timeout: 10 * time.Second,
}

// Database connection pool
db, _ := sql.Open("postgres", dsn)
db.SetMaxOpenConns(25)
db.SetMaxIdleConns(5)
db.SetConnMaxLifetime(5 * time.Minute)
```

## Performance Anti-Patterns

### Unnecessary Interface Conversions
```go
// Bad: Interface conversion in hot path
func process(items []interface{}) {
    for _, item := range items {
        v := item.(MyType)  // Type assertion overhead
        use(v)
    }
}

// Good: Use concrete types
func process(items []MyType) {
    for _, item := range items {
        use(item)  // Direct access
    }
}
```

### Defer in Loops
```go
// Bad: Defers accumulate in loop
for _, file := range files {
    f, _ := os.Open(file)
    defer f.Close()  // All close calls deferred until function returns!
}

// Good: Close immediately or use function
for _, file := range files {
    func() {
        f, _ := os.Open(file)
        defer f.Close()  // Deferred to end of this closure
        process(f)
    }()
}
```

### Lock Contention
```go
// Bad: Lock held during expensive operation
mu.Lock()
result := expensiveComputation(data)
cache[key] = result
mu.Unlock()

// Good: Minimize lock time
result := expensiveComputation(data)
mu.Lock()
cache[key] = result
mu.Unlock()

// Better: Use sync.Map for concurrent reads
var cache sync.Map
cache.Store(key, value)
val, ok := cache.Load(key)
```

## Compiler Optimizations

### Escape Analysis
```go
// Bad: Escapes to heap
func makeSlice() *[]int {
    s := make([]int, 1000)
    return &s  // Pointer returned, allocates on heap
}

// Good: Stays on stack
func makeSlice() []int {
    s := make([]int, 1000)
    return s  // Value returned, can stay on stack
}

// Check with: go build -gcflags='-m'
```

### Inline Functions
```go
// Small functions are inlined automatically
func add(a, b int) int {
    return a + b  // Will be inlined
}

// Prevent inlining if needed: //go:noinline
```

## Performance Checklist

**Before Optimizing:**
- [ ] Profile with pprof to identify bottlenecks
- [ ] Write benchmarks for hot paths
- [ ] Measure allocations with `-benchmem`
- [ ] Check for goroutine leaks

**Go-Specific Optimizations:**
- [ ] Preallocate slices and maps with known capacity
- [ ] Use `strings.Builder` for string concatenation
- [ ] Implement worker pools instead of unlimited goroutines
- [ ] Use buffered channels to reduce blocking
- [ ] Reuse buffers with `sync.Pool`
- [ ] Minimize allocations in hot paths
- [ ] Order struct fields by size (largest first)
- [ ] Use concrete types instead of interfaces in hot paths
- [ ] Avoid `defer` in tight loops
- [ ] Use `sync.Map` for concurrent read-heavy maps

**After Optimizing:**
- [ ] Re-profile to verify improvements
- [ ] Compare benchmarks: `benchstat old.txt new.txt`
- [ ] Check memory allocations decreased
- [ ] Monitor goroutine count in production
- [ ] Use `go test -race` to check for race conditions

## Tools and Packages

**Profiling:**
- `pprof` - Built-in profiler
- `go-torch` - Flamegraph generation
- `benchstat` - Compare benchmark results
- `trace` - Execution tracer

**Optimization:**
- `sync.Pool` - Object pooling
- `sync.Map` - Concurrent map
- `strings.Builder` - Efficient string building
- `bufio` - Buffered I/O

**Analysis:**
- `-gcflags='-m'` - Escape analysis
- `go test -race` - Race detector
- `go test -benchmem` - Memory allocations
- `goleak` - Goroutine leak detection

---

*Go-specific performance optimization with goroutines, channels, and profiling*
