# Performance Tests

This directory contains performance and stress tests that are excluded from regular test runs.

## Running Performance Tests

### Run all performance tests:
```bash
pytest tests/performance/
```

### Run with full stress testing:
```bash
FULL_STRESS_TEST=1 pytest tests/performance/
```

### Run specific performance test:
```bash
pytest tests/performance/test_stress.py::test_memory_leak_detection
```

## Test Categories

- **Stress Tests**: High-load scenarios with many iterations
- **Memory Tests**: Memory leak detection and resource usage
- **Concurrency Tests**: Multi-threaded and async operation tests
- **Performance Baselines**: Benchmarking system performance

## Environment Variables

- `FULL_STRESS_TEST=1`: Run tests with full iterations (slower but more thorough)
- Default behavior: Run with reduced iterations for faster feedback

## Adding New Performance Tests

When adding new performance tests:
1. Place them in this directory
2. Use environment variables to control test intensity
3. Document expected runtime and resource usage
4. Ensure tests can run in both quick and full modes