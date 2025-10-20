# Language-Specific Quality Standards

This file describes quality gates, validation commands, and standards for different programming languages.

## Quality Gate Overview

**All Implementations Must Pass:**
- ✅ Linting (0 errors, warnings acceptable with justification)
- ✅ Formatting (consistent code style)
- ✅ Tests (all passing, appropriate coverage)
- ✅ Type checking (if applicable to language)
- ✅ Documentation (comprehensive and up-to-date)

---

## Python Standards

### Validation Commands

```bash
# Linting
ruff check . --fix

# Formatting
ruff format .

# Tests
pytest -v

# Type Checking
mypy . --ignore-missing-imports

# Coverage
pytest --cov --cov-report=html

# Full Validation Pipeline
ruff check . && ruff format . && mypy . && pytest
```

### Required Standards

```yaml
Code Style:
  - Line length: 120 characters (configurable)
  - Imports: Sorted with isort style
  - Docstrings: Google or NumPy style
  - Type hints: Everywhere (functions, methods, variables)

Testing:
  - Framework: pytest
  - Coverage: >= 80%
  - Test files: test_*.py or *_test.py
  - Fixtures: Prefer pytest fixtures over setup/teardown
  - Assertions: Use pytest assertions, not unittest

Documentation:
  - All modules: Docstring with purpose
  - All classes: Docstring with attributes
  - All functions: Docstring with args, returns, raises
  - Complex logic: Inline comments for clarity

Error Handling:
  - Use specific exceptions (not bare except)
  - Custom exceptions for domain errors
  - Proper exception chaining
  - Clean resource management (context managers)
```

### Python Quality Checklist

**Before Declaring Complete:**
- [ ] All functions have type hints
- [ ] All functions have docstrings (Google/NumPy style)
- [ ] No linting errors (`ruff check .`)
- [ ] Code formatted consistently (`ruff format .`)
- [ ] Type checking passes (`mypy .`)
- [ ] All tests pass (`pytest`)
- [ ] Test coverage >= 80%
- [ ] No bare except clauses
- [ ] Proper exception handling
- [ ] Resources properly managed

---

## Rust Standards

### Validation Commands

```bash
# Linting
cargo clippy -- -D warnings

# Formatting
cargo fmt

# Tests
cargo test

# Type Checking (implicit)
cargo check

# Documentation
cargo doc --no-deps --open

# Full Validation Pipeline
cargo clippy -- -D warnings && cargo fmt --check && cargo test
```

### Required Standards

```yaml
Code Style:
  - Follow: Rust API guidelines
  - Formatting: rustfmt (automatic)
  - Naming: snake_case for functions, PascalCase for types
  - Modules: Clear separation of concerns

Testing:
  - Framework: Built-in test framework
  - Coverage: >= 75%
  - Unit tests: In same file with #[cfg(test)]
  - Integration tests: In tests/ directory
  - Doc tests: In documentation examples

Documentation:
  - All public items: /// documentation
  - Modules: //! module-level docs
  - Examples: Working examples in docs
  - Safety: Document unsafe blocks thoroughly

Error Handling:
  - Use Result<T, E> for fallible operations
  - Use Option<T> for optional values
  - No .unwrap() in production code
  - Custom error types with thiserror or anyhow
  - Proper error context with context/wrap_err
```

### Rust Quality Checklist

**Before Declaring Complete:**
- [ ] No clippy warnings (`cargo clippy -- -D warnings`)
- [ ] Code formatted (`cargo fmt --check`)
- [ ] All tests pass (`cargo test`)
- [ ] No unwrap() calls in production code
- [ ] Result<T, E> used for all fallible operations
- [ ] All public items documented
- [ ] Examples in documentation tested
- [ ] Unsafe blocks documented with safety comments
- [ ] Proper error types defined
- [ ] Resource cleanup handled (Drop trait if needed)

---

## JavaScript/TypeScript Standards

### Validation Commands

**JavaScript:**
```bash
# Linting
npx eslint . --fix

# Formatting
npx prettier --write .

# Tests
npm test

# Full Validation Pipeline
npx eslint . && npx prettier --check . && npm test
```

**TypeScript:**
```bash
# Linting
npx eslint . --fix

# Formatting
npx prettier --write .

# Type Checking
npx tsc --noEmit

# Tests
npm test

# Full Validation Pipeline
npx eslint . && npx prettier --check . && npx tsc --noEmit && npm test
```

### Required Standards

```yaml
Code Style:
  - Line length: 100-120 characters
  - Semicolons: Consistent (prefer with)
  - Quotes: Single or double (consistent)
  - Trailing commas: Always in multiline

Testing:
  - Framework: Jest, Mocha, or Vitest
  - Coverage: >= 80%
  - Test files: *.test.js, *.spec.js
  - Mocking: Prefer dependency injection
  - Async: Use async/await, not callbacks

Documentation:
  - JSDoc for all exported functions
  - README for packages
  - Type definitions (TypeScript or JSDoc)
  - API documentation for libraries

TypeScript Specific:
  - Strict mode enabled
  - No 'any' types (use 'unknown' if needed)
  - Proper interface/type definitions
  - Generic types where appropriate
  - Discriminated unions for state

Error Handling:
  - Try/catch for async operations
  - Error boundaries (React)
  - Proper promise handling
  - No unhandled promise rejections
```

### JavaScript/TypeScript Quality Checklist

**Before Declaring Complete:**
- [ ] No linting errors (`eslint .`)
- [ ] Code formatted (`prettier --check .`)
- [ ] Type checking passes (TS: `tsc --noEmit`)
- [ ] All tests pass (`npm test`)
- [ ] Test coverage >= 80%
- [ ] No 'any' types (TypeScript)
- [ ] All exported functions have JSDoc
- [ ] Async operations properly handled
- [ ] Error boundaries implemented (React)
- [ ] No console.log in production code

---

## Go Standards

### Validation Commands

```bash
# Linting
golangci-lint run

# Formatting
gofmt -w .
# OR
go fmt ./...

# Tests
go test ./...

# Coverage
go test -cover ./...

# Race Detection
go test -race ./...

# Full Validation Pipeline
gofmt -w . && golangci-lint run && go test ./...
```

### Required Standards

```yaml
Code Style:
  - Follow: Effective Go guidelines
  - Formatting: gofmt (automatic)
  - Naming: MixedCaps, not snake_case
  - Package names: Short, concise, lowercase

Testing:
  - Framework: Built-in testing package
  - Coverage: >= 75%
  - Test files: *_test.go
  - Table-driven tests: Prefer for multiple cases
  - Benchmarks: Include for performance-critical code

Documentation:
  - Package: Package-level doc comment
  - Exported: All exported items documented
  - Examples: Provide examples for complex APIs
  - README: Clear usage instructions

Error Handling:
  - Return errors, don't panic
  - Use errors.New or fmt.Errorf
  - Wrap errors with context (errors.Wrap)
  - Check all errors explicitly
  - No ignored errors (use _ = explicitly)
```

### Go Quality Checklist

**Before Declaring Complete:**
- [ ] Code formatted (`gofmt` or `go fmt`)
- [ ] No linting issues (`golangci-lint run`)
- [ ] All tests pass (`go test ./...`)
- [ ] No race conditions (`go test -race ./...`)
- [ ] Test coverage >= 75%
- [ ] All exported items documented
- [ ] All errors checked explicitly
- [ ] No panics in library code
- [ ] Proper error wrapping with context
- [ ] Resource cleanup with defer

---

## Generic Language Standards

**For languages not specifically covered above, apply these general standards:**

### General Quality Gates

```yaml
Syntax & Structure:
  - Valid syntax (runs without parse errors)
  - Consistent indentation (2 or 4 spaces)
  - Clear variable naming
  - Functions <= 50 lines (guideline)
  - Nesting depth <= 3 levels

Testing:
  - Unit tests for core functionality
  - Integration tests for workflows
  - Edge case coverage
  - Error path testing
  - Reasonable coverage (>= 70%)

Documentation:
  - README with setup instructions
  - Function/method documentation
  - Complex algorithms explained
  - API documentation (if library)
  - Usage examples

Error Handling:
  - Proper exception/error handling
  - No swallowed errors
  - Meaningful error messages
  - Graceful failure modes
  - Resource cleanup

Code Quality:
  - No code duplication
  - Clear separation of concerns
  - Meaningful names
  - Single responsibility principle
  - No magic numbers/strings
```

### Generic Quality Checklist

**Before Declaring Complete:**
- [ ] Code runs without errors
- [ ] All tests pass
- [ ] Documentation complete
- [ ] Error handling in place
- [ ] No obvious code smells
- [ ] Functions reasonably sized
- [ ] Clear variable names
- [ ] No TODO comments left
- [ ] Resources properly managed
- [ ] Code reviewed for clarity

---

## Cross-Language Quality Principles

### SOLID Principles

**Apply regardless of language:**

```yaml
Single Responsibility:
  - Each class/module has one reason to change
  - Clear, focused purpose
  - Avoid "god objects"

Open/Closed:
  - Open for extension, closed for modification
  - Use interfaces/traits for extensibility
  - Avoid modifying working code

Liskov Substitution:
  - Subtypes must be substitutable for base types
  - Honor contracts in inheritance
  - Avoid breaking parent behavior

Interface Segregation:
  - Many specific interfaces > one general interface
  - Clients shouldn't depend on unused methods
  - Keep interfaces focused

Dependency Inversion:
  - Depend on abstractions, not concretions
  - High-level modules independent of low-level
  - Use dependency injection
```

### Code Smell Detection

**Watch for these issues:**

```yaml
Long Methods:
  - Threshold: > 50 lines
  - Action: Extract smaller methods
  - Tool: Refactorer agent

Deep Nesting:
  - Threshold: > 3 levels
  - Action: Flatten with early returns
  - Tool: Refactorer agent

Duplicate Code:
  - Detection: Similar code blocks
  - Action: Extract to shared function
  - Tool: Refactorer agent

Large Classes:
  - Threshold: > 300 lines
  - Action: Split responsibilities
  - Tool: Architect + Refactorer agents

Magic Numbers:
  - Detection: Unexplained constants
  - Action: Named constants
  - Tool: Implementer agent

Poor Naming:
  - Detection: Unclear variable names
  - Action: Rename to be descriptive
  - Tool: Refactorer agent
```

---

## Quality Enforcement

### Continuous Validation

**Every 3 Edits:**
```yaml
Checkpoint:
  1. Run relevant tests
  2. Check linting
  3. Verify type checking (if applicable)
  4. If any fail:
     - Fix immediately
     - Re-validate
  5. Continue implementation
```

### Pre-Completion Validation

**Before Declaring Complete:**
```yaml
Full Quality Suite:
  1. Run full test suite
  2. Run full linter
  3. Run type checker
  4. Check documentation
  5. Review specification compliance
  6. Verify all acceptance criteria met

  If ANY fail:
    - Fix issues
    - Re-run full suite
    - Only complete when all pass
```

### Post-Implementation Review

**After Implementation Complete:**
```yaml
Final Review:
  - Code review checklist
  - Security review (if applicable)
  - Performance review (if concerns)
  - Documentation completeness
  - Specification alignment
  - Ready for PR review
```

---

*Comprehensive quality standards for production-ready implementation across multiple languages*
