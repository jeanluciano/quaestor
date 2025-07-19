"""Performance and stress tests.

These tests are excluded from regular test runs and should be run explicitly:
- Run with: pytest tests/performance/
- Or with environment variable: FULL_STRESS_TEST=1 pytest

Tests in this directory:
- May take longer to execute
- Use more resources (CPU, memory)
- Test edge cases and stress scenarios
"""
