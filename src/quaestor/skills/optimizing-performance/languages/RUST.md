# Rust Performance Optimization

**Load this file when:** Optimizing performance in Rust projects

## Profiling Tools

### Benchmarking with Criterion
```bash
# Add to Cargo.toml
[dev-dependencies]
criterion = "0.5"

[[bench]]
name = "my_benchmark"
harness = false

# Run benchmarks
cargo bench

# Compare against baseline
cargo bench --baseline master
```

### CPU Profiling
```bash
# perf (Linux)
cargo build --release
perf record --call-graph dwarf ./target/release/myapp
perf report

# Instruments (macOS)
cargo instruments --release --template "Time Profiler"

# cargo-flamegraph
cargo install flamegraph
cargo flamegraph

# samply (cross-platform)
cargo install samply
samply record ./target/release/myapp
```

### Memory Profiling
```bash
# valgrind (memory leaks, cache performance)
cargo build
valgrind --tool=massif ./target/debug/myapp

# dhat (heap profiling)
# Add dhat crate to project

# cargo-bloat (binary size analysis)
cargo install cargo-bloat
cargo bloat --release
```

## Zero-Cost Abstractions

### Avoiding Unnecessary Allocations
```rust
// Bad: Allocates on every call
fn process_string(s: String) -> String {
    s.to_uppercase()
}

// Good: Borrows, no allocation
fn process_string(s: &str) -> String {
    s.to_uppercase()
}

// Best: In-place modification where possible
fn process_string_mut(s: &mut String) {
    *s = s.to_uppercase();
}
```

### Stack vs Heap Allocation
```rust
// Stack: Fast, known size at compile time
let numbers = [1, 2, 3, 4, 5];

// Heap: Flexible, runtime-sized data
let numbers = vec![1, 2, 3, 4, 5];

// Use Box<[T]> for fixed-size heap data (smaller than Vec)
let numbers: Box<[i32]> = vec![1, 2, 3, 4, 5].into_boxed_slice();
```

### Iterator Chains vs For Loops
```rust
// Good: Zero-cost iterator chains (compiled to efficient code)
let sum: i32 = numbers
    .iter()
    .filter(|&&n| n > 0)
    .map(|&n| n * 2)
    .sum();

// Also good: Manual loop (similar performance)
let mut sum = 0;
for &n in numbers.iter() {
    if n > 0 {
        sum += n * 2;
    }
}

// Choose iterators for readability, loops for complex logic
```

## Compilation Optimizations

### Release Profile Tuning
```toml
[profile.release]
opt-level = 3           # Maximum optimization
lto = "fat"             # Link-time optimization
codegen-units = 1       # Better optimization, slower compile
strip = true            # Strip symbols from binary
panic = "abort"         # Smaller binary, no stack unwinding

[profile.release-with-debug]
inherits = "release"
debug = true           # Keep debug symbols for profiling
```

### Target CPU Features
```bash
# Use native CPU features
RUSTFLAGS="-C target-cpu=native" cargo build --release

# Or in .cargo/config.toml
[build]
rustflags = ["-C", "target-cpu=native"]
```

## Memory Layout Optimization

### Struct Field Ordering
```rust
// Bad: Wasted padding (24 bytes)
struct BadLayout {
    a: u8,   // 1 byte + 7 padding
    b: u64,  // 8 bytes
    c: u8,   // 1 byte + 7 padding
}

// Good: Minimal padding (16 bytes)
struct GoodLayout {
    b: u64,  // 8 bytes
    a: u8,   // 1 byte
    c: u8,   // 1 byte + 6 padding
}

// Use #[repr(C)] for consistent layout
#[repr(C)]
struct FixedLayout {
    // Fields laid out in declaration order
}
```

### Enum Optimization
```rust
// Consider enum size (uses largest variant)
enum Large {
    Small(u8),
    Big([u8; 1000]),  // Entire enum is 1000+ bytes!
}

// Better: Box large variants
enum Optimized {
    Small(u8),
    Big(Box<[u8; 1000]>),  // Enum is now pointer-sized
}
```

## Concurrency Patterns

### Using Rayon for Data Parallelism
```rust
use rayon::prelude::*;

// Sequential
let sum: i32 = data.iter().map(|x| expensive(x)).sum();

// Parallel (automatic work stealing)
let sum: i32 = data.par_iter().map(|x| expensive(x)).sum();
```

### Async Runtime Optimization
```rust
// tokio - For I/O-heavy workloads
#[tokio::main(flavor = "multi_thread", worker_threads = 4)]
async fn main() {
    // Async I/O operations
}

// async-std - Alternative runtime
// Choose based on ecosystem compatibility
```

## Common Rust Performance Patterns

### String Handling
```rust
// Avoid unnecessary clones
// Bad
fn process(s: String) -> String {
    let upper = s.clone().to_uppercase();
    upper
}

// Good
fn process(s: &str) -> String {
    s.to_uppercase()
}

// Use Cow for conditional cloning
use std::borrow::Cow;

fn maybe_uppercase<'a>(s: &'a str, uppercase: bool) -> Cow<'a, str> {
    if uppercase {
        Cow::Owned(s.to_uppercase())
    } else {
        Cow::Borrowed(s)
    }
}
```

### Collection Preallocation
```rust
// Bad: Multiple reallocations
let mut vec = Vec::new();
for i in 0..1000 {
    vec.push(i);
}

// Good: Single allocation
let mut vec = Vec::with_capacity(1000);
for i in 0..1000 {
    vec.push(i);
}

// Best: Use collect with size_hint
let vec: Vec<_> = (0..1000).collect();
```

### Minimize Clones
```rust
// Bad: Unnecessary clones in loop
for item in &items {
    let owned = item.clone();
    process(owned);
}

// Good: Borrow when possible
for item in &items {
    process_borrowed(item);
}

// Use Rc/Arc only when necessary
use std::rc::Rc;
let shared = Rc::new(expensive_data);
let clone1 = Rc::clone(&shared);  // Cheap pointer clone
```

## Performance Anti-Patterns

### Unnecessary Dynamic Dispatch
```rust
// Bad: Dynamic dispatch overhead
fn process(items: &[Box<dyn Trait>]) {
    for item in items {
        item.method();  // Virtual call
    }
}

// Good: Static dispatch via generics
fn process<T: Trait>(items: &[T]) {
    for item in items {
        item.method();  // Direct call, can be inlined
    }
}
```

### Lock Contention
```rust
// Bad: Holding lock during expensive operation
let data = mutex.lock().unwrap();
let result = expensive_computation(&data);
drop(data);

// Good: Release lock quickly
let cloned = {
    let data = mutex.lock().unwrap();
    data.clone()
};
let result = expensive_computation(&cloned);
```

## Benchmarking with Criterion

### Basic Benchmark
```rust
use criterion::{black_box, criterion_group, criterion_main, Criterion};

fn fibonacci_benchmark(c: &mut Criterion) {
    c.bench_function("fib 20", |b| {
        b.iter(|| fibonacci(black_box(20)))
    });
}

criterion_group!(benches, fibonacci_benchmark);
criterion_main!(benches);
```

### Parameterized Benchmarks
```rust
fn bench_sizes(c: &mut Criterion) {
    let mut group = c.benchmark_group("process");

    for size in [10, 100, 1000, 10000].iter() {
        group.bench_with_input(
            BenchmarkId::from_parameter(size),
            size,
            |b, &size| {
                b.iter(|| process_data(black_box(size)))
            },
        );
    }

    group.finish();
}
```

## Performance Checklist

**Before Optimizing:**
- [ ] Profile with release build to identify bottlenecks
- [ ] Measure baseline with criterion benchmarks
- [ ] Use cargo-flamegraph to visualize hot paths

**Rust-Specific Optimizations:**
- [ ] Enable LTO in release profile
- [ ] Use target-cpu=native for CPU-specific features
- [ ] Preallocate collections with `with_capacity`
- [ ] Prefer borrowing (&T) over owned (T) in APIs
- [ ] Use iterators over manual loops
- [ ] Minimize clones - use Rc/Arc only when needed
- [ ] Order struct fields by size (largest first)
- [ ] Box large enum variants
- [ ] Use rayon for CPU-bound parallelism
- [ ] Avoid unnecessary dynamic dispatch

**After Optimizing:**
- [ ] Re-benchmark to verify improvements
- [ ] Check binary size with cargo-bloat
- [ ] Profile memory with valgrind/dhat
- [ ] Add regression tests with criterion baselines

## Tools and Crates

**Profiling:**
- `criterion` - Statistical benchmarking
- `flamegraph` - Flamegraph generation
- `cargo-instruments` - macOS profiling
- `perf` - Linux performance analysis
- `dhat` - Heap profiling

**Optimization:**
- `rayon` - Data parallelism
- `tokio` / `async-std` - Async runtime
- `parking_lot` - Faster mutex/rwlock
- `smallvec` - Stack-allocated vectors
- `once_cell` - Lazy static initialization

**Analysis:**
- `cargo-bloat` - Binary size analysis
- `cargo-udeps` - Find unused dependencies
- `twiggy` - Code size profiler

---

*Rust-specific performance optimization with zero-cost abstractions and profiling tools*
