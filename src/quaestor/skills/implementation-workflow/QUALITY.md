# Quality Standards - Language Dispatch

This file provides an overview of quality standards and directs you to language-specific quality gates.

## When to Load This File

- User asks: "What are the quality standards?"
- Need overview of validation approach
- Choosing which language file to load

## Quality Philosophy

**All implementations must pass these gates:**
- ✅ Linting (0 errors, warnings with justification)
- ✅ Formatting (consistent code style)
- ✅ Tests (all passing, appropriate coverage)
- ✅ Type checking (if language supports it)
- ✅ Documentation (comprehensive and current)

## Language-Specific Standards

**Load the appropriate file based on detected project language:**

### Python Projects
**When to load:** `pyproject.toml`, `requirements.txt`, or `*.py` files detected

**Load:** `@languages/PYTHON.md`

**Quick commands:**
```bash
ruff check . && ruff format . && mypy . && pytest
```

---

### Rust Projects
**When to load:** `Cargo.toml` or `*.rs` files detected

**Load:** `@languages/RUST.md`

**Quick commands:**
```bash
cargo clippy -- -D warnings && cargo fmt --check && cargo test
```

---

### JavaScript/TypeScript Projects
**When to load:** `package.json`, `tsconfig.json`, or `*.js`/`*.ts` files detected

**Load:** `@languages/JAVASCRIPT.md`

**Quick commands:**
```bash
# TypeScript
npx eslint . && npx prettier --check . && npx tsc --noEmit && npm test

# JavaScript
npx eslint . && npx prettier --check . && npm test
```

---

### Go Projects
**When to load:** `go.mod` or `*.go` files detected

**Load:** `@languages/GO.md`

**Quick commands:**
```bash
gofmt -w . && golangci-lint run && go test ./...
```

---

### Other Languages
**When to load:** No specific language detected, or unsupported language (PHP, Ruby, C++, C#, Java, etc.)

**Load:** `@languages/GENERIC.md`

**Provides:** General quality principles applicable across languages

---

## Progressive Loading Pattern

**Don't load all language files!** Only load the relevant one:

1. **Detect project language** (from file extensions, config files)
2. **Load specific standards** for that language only
3. **Apply language-specific validation** commands
4. **Fallback to generic** if language not covered

## Continuous Validation

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

## Pre-Completion Validation

**Before marking work complete:**
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

## Quality Enforcement Strategy

```yaml
Detect Language:
  - Check for language-specific files (pyproject.toml, Cargo.toml, etc.)
  - Identify from file extensions
  - User can override if auto-detection fails

Load Standards:
  - Load @languages/PYTHON.md for Python
  - Load @languages/RUST.md for Rust
  - Load @languages/JAVASCRIPT.md for JS/TS
  - Load @languages/GO.md for Go
  - Load @languages/GENERIC.md for others

Apply Validation:
  - Run language-specific commands
  - Check against language-specific standards
  - Enforce coverage requirements
  - Validate documentation completeness

Report Results:
  - Clear pass/fail for each gate
  - Specific error messages
  - Actionable fix suggestions
```

## When Standards Apply

**During Implementation:**
- After every 3 edits (checkpoint validation)
- Before declaring task complete (full validation)
- When explicitly requested by user

**Quality Gates Must Pass:**
- To move from implementation → review phase
- To mark specification acceptance criteria complete
- Before creating pull request

## Cross-Language Principles

**These apply regardless of language:**

```yaml
SOLID Principles:
  - Single Responsibility
  - Open/Closed
  - Liskov Substitution
  - Interface Segregation
  - Dependency Inversion

Code Quality:
  - No duplication
  - Clear naming
  - Reasonable function size (<= 50 lines guideline)
  - Low nesting depth (<= 3 levels)
  - Proper error handling

Testing:
  - Unit tests for business logic
  - Integration tests for workflows
  - Edge case coverage
  - Error path coverage
  - Reasonable coverage targets

Documentation:
  - README for setup
  - API documentation
  - Complex logic explained
  - Usage examples
```

---

*Load language-specific files for detailed standards - avoid loading all language contexts unnecessarily*
