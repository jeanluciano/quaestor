# Detection & Analysis

This file contains detailed patterns for project analysis, framework detection, and agent orchestration.

## Phase 1: Agent-Orchestrated Discovery

I coordinate specialized agents for parallel analysis:

### Agent Execution Strategy

```yaml
Parallel Agent Execution:
  Framework & Dependencies:
    agent: researcher
    timeout: 10 seconds
    analyzes:
      - Primary programming language and framework
      - Dependencies from package.json/requirements.txt/Cargo.toml/go.mod
      - Test framework and current coverage
      - Build tools and scripts
    output: "Structured YAML with framework, dependencies, and tools"

  Architecture Patterns:
    agent: architect
    timeout: 10 seconds
    analyzes:
      - Architecture patterns (MVC, DDD, VSA, Clean Architecture)
      - Component relationships and boundaries
      - API design patterns
      - Database architecture
      - Technical debt and complexity hotspots
    output: "Structured analysis with patterns, strengths, and concerns"

  Security Assessment:
    agent: security
    timeout: 10 seconds
    analyzes:
      - Security patterns and anti-patterns
      - Common vulnerabilities
      - Authentication/authorization approach
      - Data handling and encryption
      - Dependency security
    output: "Security assessment with risks and recommendations"
```

### Result Consolidation

After all agents complete, consolidate findings:

```yaml
consolidated_analysis:
  framework: "[from researcher agent]"
  language: "[detected primary language]"
  architecture: "[from architect agent]"
  security: "[from security agent]"
  complexity: "[calculated score 0.0-1.0]"
  phase: "[new|growth|legacy based on analysis]"
```

## Phase 2.1: Language Detection

Detect the primary language from package files:

```yaml
language_detection_patterns:
  Python:
    files: [requirements.txt, pyproject.toml, setup.py, Pipfile]
    confidence: high
    indicators:
      - "import statements in .py files"
      - "pip/poetry/pipenv config"

  TypeScript:
    files: [package.json with "typescript" dependency, tsconfig.json]
    confidence: high
    indicators:
      - ".ts or .tsx files"
      - "typescript in devDependencies"

  JavaScript:
    files: [package.json without typescript]
    confidence: medium
    indicators:
      - ".js or .jsx files"
      - "node_modules directory"

  Rust:
    files: [Cargo.toml, Cargo.lock]
    confidence: high
    indicators:
      - ".rs files"
      - "cargo workspace config"

  Go:
    files: [go.mod, go.sum]
    confidence: high
    indicators:
      - ".go files"
      - "go directive in go.mod"

  Java:
    files: [pom.xml, build.gradle, build.gradle.kts]
    confidence: high
    indicators:
      - ".java files"
      - "maven/gradle config"

  Ruby:
    files: [Gemfile, Gemfile.lock]
    confidence: high
    indicators:
      - ".rb files"
      - "bundler config"
```

### Detection Algorithm

```
1. Check for language-specific config files (highest confidence)
2. Count files by extension in src/ directory
3. Parse package managers to identify language
4. Assign confidence score based on indicators
5. Select language with highest confidence
```

## Phase 2.2: Load Language Configuration

For the detected language, load defaults from `src/quaestor/core/languages.yaml`:

```yaml
# Example for Python
python:
  lint_command: "ruff check ."
  format_command: "ruff format ."
  test_command: "pytest"
  coverage_command: "pytest --cov"
  type_check_command: "mypy ."
  quick_check_command: "ruff check . && pytest -x"
  full_check_command: "ruff check . && ruff format --check . && mypy . && pytest"
  code_formatter: "ruff"
  testing_framework: "pytest"
  coverage_threshold_percent: ">= 80%"

# Example for TypeScript/JavaScript
typescript:
  lint_command: "eslint ."
  format_command: "prettier --write ."
  test_command: "npm test"
  coverage_command: "npm run test:coverage"
  type_check_command: "tsc --noEmit"
  quick_check_command: "eslint . && npm test"
  full_check_command: "eslint . && prettier --check . && tsc --noEmit && npm test"
  code_formatter: "prettier"
  testing_framework: "jest"
  coverage_threshold_percent: ">= 80%"

# Example for Rust
rust:
  lint_command: "cargo clippy"
  format_command: "cargo fmt"
  test_command: "cargo test"
  coverage_command: "cargo tarpaulin"
  type_check_command: "cargo check"
  quick_check_command: "cargo clippy && cargo test"
  full_check_command: "cargo clippy && cargo fmt --check && cargo test"
  code_formatter: "rustfmt"
  testing_framework: "cargo test"
  coverage_threshold_percent: ">= 75%"
```

## Framework-Specific Intelligence

### React/Frontend Projects

```yaml
react_detection:
  indicators:
    - "react" in package.json dependencies
    - ".jsx or .tsx files"
    - "src/components/" directory structure

  analysis:
    state_management:
      patterns: [Redux, Context API, Zustand, Recoil, MobX]
      detection: "Search for store/context setup files"

    component_patterns:
      types: [HOC, Hooks, Render Props, Class Components]
      detection: "Analyze component file structure"

    architecture:
      types: [SPA, SSR, Static Site]
      detection: "Check for Next.js, Gatsby, or CRA setup"

    quality_gates:
      defaults: "ESLint + Prettier + TypeScript"
      detection: "Parse .eslintrc and tsconfig.json"
```

### Python/Backend Projects

```yaml
python_detection:
  frameworks:
    Django:
      indicators: ["django" in requirements, manage.py, settings.py]
      architecture: "MTV (Model-Template-View)"

    FastAPI:
      indicators: ["fastapi" in requirements, main.py with app = FastAPI()]
      architecture: "API-first, async-native"

    Flask:
      indicators: ["flask" in requirements, app.py]
      architecture: "Microframework, flexible"

  patterns:
    detection: [MVC, Repository, Service Layer, Domain-Driven Design]
    analysis: "Examine directory structure and import patterns"

  testing:
    frameworks: [pytest, unittest, nose2]
    detection: "Check test files and conftest.py"

  quality_gates:
    defaults: "ruff + mypy + pytest"
    detection: "Parse pyproject.toml and setup.cfg"
```

### Rust Projects

```yaml
rust_detection:
  frameworks:
    Axum:
      indicators: ["axum" in Cargo.toml, "use axum::"]
      architecture: "Async, Tower middleware"

    Rocket:
      indicators: ["rocket" in Cargo.toml, "#[rocket::"]
      architecture: "Type-safe, batteries-included"

    Actix:
      indicators: ["actix-web" in Cargo.toml, "use actix_web::"]
      architecture: "Actor-based, high performance"

  patterns:
    detection: [Hexagonal, Clean Architecture, Layered]
    analysis: "Examine module structure and trait boundaries"

  testing:
    default: "cargo test with built-in test framework"
    detection: "#[test] and #[cfg(test)] attributes"

  quality_gates:
    defaults: "clippy + rustfmt + cargo test"
    detection: "Cargo.toml and clippy.toml"
```

## Project Phase Detection

Analyze git history and project metrics to determine project phase:

```yaml
phase_detection:
  Startup (0-6 months):
    indicators:
      - Commit count: < 200
      - Contributors: 1-3
      - Files: < 100
      - Test coverage: < 60%
    focus: "MVP Foundation, Core Features, User Feedback"

  Growth (6-18 months):
    indicators:
      - Commit count: 200-1000
      - Contributors: 3-10
      - Files: 100-500
      - Test coverage: 60-80%
    focus: "Performance, Feature Expansion, Production Hardening"

  Enterprise (18+ months):
    indicators:
      - Commit count: > 1000
      - Contributors: > 10
      - Files: > 500
      - Test coverage: > 80%
    focus: "Architecture Evolution, Scalability, Platform Maturation"
```

## Error Handling & Graceful Degradation

```yaml
error_handling:
  researcher_agent_fails:
    fallback:
      - Use basic file detection (package.json, requirements.txt)
      - Count files by extension
      - Parse package manager files directly
    log: "Framework detection limited - manual review recommended"
    continue: true

  architect_agent_fails:
    fallback:
      - Use simplified pattern detection based on folder structure
      - Check for common patterns (models/, views/, controllers/)
      - Infer from file naming conventions
    log: "Architecture analysis incomplete - patterns may be missed"
    continue: true

  security_agent_fails:
    fallback:
      - Flag for manual security review
      - Skip security-specific recommendations
      - Use generic security best practices
    log: "Security assessment skipped - manual review required"
    continue: true

  timeout_handling:
    total_time_limit: 30 seconds
    individual_agent_timeout: 10 seconds
    strategy: "Kill agent on timeout, use partial results if available"

  missing_config_files:
    strategy: "Use sensible defaults for detected language"
    log: "Using default configuration for [language]"
    continue: true
```

## Performance Optimization

```yaml
optimization:
  parallel_execution:
    - Run all 3 agents simultaneously using Task tool
    - Agents are independent, no sequential dependencies
    - Reduces total analysis time from 30s to ~10s

  caching:
    - Cache language detection results during session
    - Cache parsed package manager files
    - Avoid redundant file system scans

  early_termination:
    - If all agents complete in < 5s, proceed immediately
    - Don't wait for full timeout period
```

---

*This file provides comprehensive detection patterns and agent orchestration strategies for intelligent project analysis.*
