# User Validation Workflow

This file describes the mandatory user validation process that must occur before project initialization completes.

## Phase 3: User Validation ✅ **[MANDATORY]**

⚠️ **CRITICAL ENFORCEMENT RULE:**

```yaml
before_phase_4:
  MUST_PRESENT_ANALYSIS:
    - framework_detection_results
    - architecture_pattern_analysis
    - quality_standards_detected
    - project_phase_determination

  MUST_GET_USER_CHOICE:
    options:
      - "✅ Proceed with detected setup"
      - "🔄 Modify detected patterns"
      - "📝 Custom architecture description"
      - "🚫 Start with minimal setup"

  VIOLATION_CONSEQUENCES:
    - if_skipped: "IMMEDIATE STOP - Restart from Phase 3"
    - required_response: "I must validate this analysis with you before proceeding"
```

## Validation Template

I **MUST** present this analysis to the user:

```
## Project Analysis Validation ✋

**Detected Configuration:**
- Framework: [detected_framework]
- Architecture: [detected_pattern]
- Complexity: [score]/1.0
- Phase: [project_phase]

**Quality Standards:**
[detected_tools_and_standards]

**Files Analyzed:**
[list_of_key_files_examined]

## Your Options:
- ✅ Proceed with detected setup
- 🔄 Modify detected patterns
- 📝 Custom architecture description
- 🚫 Start with minimal setup

What would you prefer for the initial setup?
```

## Validation Components

### 1. Detected Configuration

Present the consolidated analysis from Phase 1:

```yaml
configuration_display:
  framework:
    format: "[Framework Name] with [Key Libraries]"
    examples:
      - "FastAPI with SQLAlchemy"
      - "React with TypeScript and Redux"
      - "Axum with Tokio and SQLx"

  architecture:
    format: "[Pattern Name] ([Key Characteristics])"
    examples:
      - "Hexagonal (Ports & Adapters)"
      - "Component-based with Redux state management"
      - "Clean Architecture with DDD"

  complexity:
    format: "[score]/1.0 ([complexity_level])"
    levels:
      - "0.0-0.3: Low"
      - "0.3-0.6: Moderate"
      - "0.6-0.8: High"
      - "0.8-1.0: Very High"

  phase:
    format: "[phase_name] ([duration])"
    phases:
      - "Startup (0-6 months)"
      - "Growth (6-18 months)"
      - "Enterprise (18+ months)"
      - "Legacy (maintenance mode)"
```

### 2. Quality Standards

Present the detected tools and standards:

```yaml
quality_standards_display:
  testing:
    format: "[framework] with [coverage]% coverage"
    examples:
      - "pytest with 75% coverage"
      - "jest with React Testing Library"
      - "cargo test with 80% coverage"

  linting:
    format: "[linter] with [config_file] config"
    examples:
      - "ruff with pyproject.toml config"
      - "ESLint with Airbnb config"
      - "clippy with custom clippy.toml"

  type_checking:
    format: "[type_checker] in [mode] mode"
    examples:
      - "mypy in strict mode"
      - "TypeScript strict mode"
      - "Rust's built-in type system"

  ci_cd:
    format: "[ci_system] detected"
    examples:
      - "GitHub Actions detected"
      - "GitLab CI configured"
      - "No CI detected"

  security:
    format: "[status]"
    examples:
      - "No major vulnerabilities detected"
      - "2 outdated dependencies found"
      - "Security scan recommended"
```

### 3. Files Analyzed

Show what was examined to build confidence:

```yaml
files_display:
  format: "- [file_path]: [what_was_found]"
  examples:
    - "pyproject.toml: FastAPI, SQLAlchemy, pytest dependencies"
    - "src/domain/: Clean domain layer detected"
    - "src/infrastructure/: Repository pattern found"
    - "tests/: Good test coverage structure"
    - "package.json: React 18, TypeScript 5, Jest"
    - "src/components/: Hooks-based components"
    - "Cargo.toml: axum, tokio, sqlx dependencies"
    - "src/lib.rs: Layered module structure"
```

## User Response Handling

### Option 1: ✅ Proceed with detected setup

```yaml
proceed:
  user_says: "Proceed with detected setup" | "Looks good" | "Yes" | "Continue"
  action: "Move to Phase 4 with all detected settings"
  no_changes: true
```

### Option 2: 🔄 Modify detected patterns

```yaml
modify:
  user_says: "Modify detected patterns" | "Change something" | "Adjust"
  follow_up_questions:
    - "What would you like to change?"
    - "Which aspect needs adjustment? (framework/architecture/quality standards)"

  common_modifications:
    - Change complexity threshold
    - Adjust test coverage requirements
    - Modify linting rules
    - Update architecture pattern choice
    - Change project phase classification

  example_dialogue:
    user: "Modify detected patterns"
    me: "What would you like to adjust?"
    user: "Change coverage requirement to 90%"
    me: "Updated coverage threshold to 90%. Anything else?"
    user: "No, proceed"
    me: "[Move to Phase 4 with modifications]"
```

### Option 3: 📝 Custom architecture description

```yaml
custom:
  user_says: "Custom architecture" | "I'll describe it" | "Let me explain"
  follow_up: "Please describe your project architecture"

  collect_information:
    - Architecture pattern (if different from detected)
    - Key components and their responsibilities
    - Technology choices and rationale
    - Quality standards and thresholds
    - Testing strategy

  example_dialogue:
    user: "Custom architecture description"
    me: "Please describe your architecture approach"
    user: "We use Clean Architecture with CQRS, event sourcing for writes..."
    me: "Got it. I'll use your custom architecture description. Proceed?"
    user: "Yes"
    me: "[Move to Phase 4 with custom architecture]"
```

### Option 4: 🚫 Start with minimal setup

```yaml
minimal:
  user_says: "Minimal setup" | "Keep it simple" | "Basic only"
  action: "Create minimal configuration without detected patterns"

  minimal_setup_includes:
    - Basic AGENT.md (standard workflow rules)
    - Basic ARCHITECTURE.md template (user fills in later)
    - CLAUDE.md entry point
    - Directory structure
    - No language-specific customization
    - No framework detection applied

  example_dialogue:
    user: "Start with minimal setup"
    me: "I'll create a minimal setup without framework-specific customization."
    me: "[Move to Phase 4 with minimal config]"
```

## Validation Examples

### Example 1: Python FastAPI Project

```
## Project Analysis Validation ✋

**Detected Configuration:**
- Framework: FastAPI with SQLAlchemy
- Architecture: Hexagonal (Ports & Adapters)
- Complexity: 0.65/1.0 (moderate)
- Phase: Growth (6-18 months)

**Quality Standards:**
- Testing: pytest with 75% coverage
- Linting: ruff with pyproject.toml config
- Type checking: mypy in strict mode
- CI/CD: GitHub Actions detected
- Security: No major vulnerabilities detected

**Files Analyzed:**
- pyproject.toml: FastAPI, SQLAlchemy, pytest dependencies
- src/domain/: Clean domain layer detected
- src/infrastructure/: Repository pattern found
- tests/: Good test coverage structure

## Your Options:
- ✅ Proceed with detected setup
- 🔄 Modify detected patterns
- 📝 Custom architecture description
- 🚫 Start with minimal setup

What would you prefer for the initial setup?
```

### Example 2: React TypeScript Project

```
## Project Analysis Validation ✋

**Detected Configuration:**
- Framework: React with TypeScript
- Architecture: Component-based with Redux state management
- Complexity: 0.70/1.0 (high)
- Phase: Growth (6-18 months)

**Quality Standards:**
- Testing: Jest with React Testing Library
- Linting: ESLint with Airbnb config
- Type checking: TypeScript strict mode
- CI/CD: GitHub Actions detected
- Security: 2 outdated dependencies (non-critical)

**Files Analyzed:**
- package.json: React 18.2, TypeScript 5.0, Jest, ESLint
- src/components/: Hooks-based component architecture
- src/store/: Redux Toolkit slices and sagas
- tests/: 82% test coverage

## Your Options:
- ✅ Proceed with detected setup
- 🔄 Modify detected patterns
- 📝 Custom architecture description
- 🚫 Start with minimal setup

What would you prefer for the initial setup?
```

### Example 3: Rust Axum Project

```
## Project Analysis Validation ✋

**Detected Configuration:**
- Framework: Axum with Tokio and SQLx
- Architecture: Layered with clear module boundaries
- Complexity: 0.55/1.0 (moderate)
- Phase: Startup (0-6 months)

**Quality Standards:**
- Testing: cargo test with 68% coverage
- Linting: clippy with custom rules
- Type checking: Rust's built-in system
- CI/CD: No CI detected
- Security: All dependencies up to date

**Files Analyzed:**
- Cargo.toml: axum 0.7, tokio 1.35, sqlx 0.7
- src/lib.rs: Well-structured module hierarchy
- src/handlers/: Clean separation of concerns
- tests/: Integration tests present

## Your Options:
- ✅ Proceed with detected setup
- 🔄 Modify detected patterns
- 📝 Custom architecture description
- 🚫 Start with minimal setup

What would you prefer for the initial setup?
```

## Enforcement Rules

### ❌ NEVER Skip Validation

```yaml
prohibited_actions:
  - Proceeding to Phase 4 without user approval
  - Assuming user wants default configuration
  - Auto-selecting "Proceed" option
  - Skipping validation "to save time"

required_behavior:
  - ALWAYS present full analysis
  - ALWAYS wait for explicit user choice
  - ALWAYS confirm understanding of user's choice
  - ALWAYS document which option was chosen
```

### ✅ Required Confirmation

Before moving to Phase 4, I must have:
1. Presented complete analysis to user
2. Shown all 4 options
3. Received explicit user selection
4. Confirmed understanding of selection

Only then can I proceed to Phase 4.

---

*This validation workflow ensures users have full control and understanding of their project setup before any files are generated.*
