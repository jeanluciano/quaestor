# Complete Initialization Examples

This file provides complete end-to-end examples of project initialization for different project types.

## Example 1: Python FastAPI Project

### User Request
```
User: "Initialize Quaestor in this Python project"
```

### My Response - Phase 1 & 2 (Analysis)
```
🔍 Analyzing your project...

Spawning specialized agents for analysis:
- researcher: Analyzing dependencies and framework
- architect: Evaluating architecture patterns
- security: Assessing security posture

[Agents complete in ~8 seconds]
```

### My Response - Phase 3 (Validation)
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

### User Response
```
User: "Proceed with detected setup"
```

### My Response - Phase 4 (Completion)
```
✅ Initialization complete!

**Generated Documentation:**
- .quaestor/AGENT.md (AI behavioral rules)
- .quaestor/ARCHITECTURE.md (with Python quality standards)
- CLAUDE.md (main entry point)

**Directory Structure:**
- .quaestor/specs/draft/
- .quaestor/specs/active/
- .quaestor/specs/completed/
- .quaestor/specs/archived/

**Next Steps:**
1. Review .quaestor/ARCHITECTURE.md Section 3 to customize commands
2. Create your first specification: "Create a spec for..."
3. Start development with Research → Plan → Implement workflow
```

### Generated ARCHITECTURE.md (Section 3 excerpt)
```markdown
## 3. CODE QUALITY STANDARDS

### Linting and Formatting
- **Linter**: `ruff check .`
- **Formatter**: `ruff format .`
- **Code Formatter**: ruff
- **Quick Check**: `ruff check . && pytest -x`
- **Full Validation**: `ruff check . && ruff format --check . && mypy . && pytest`

### Testing Requirements
- **Test Runner**: `pytest`
- **Coverage**: `pytest --cov`
- **Coverage Threshold**: >= 80%
- **Testing Framework**: pytest
```

---

## Example 2: React TypeScript Project with Modifications

### User Request
```
User: "Set up Quaestor with intelligent project analysis"
```

### My Response - Phase 1 & 2 (Analysis)
```
🔍 Analyzing your project...

Spawning specialized agents:
- researcher: Framework and dependency analysis
- architect: Architecture pattern evaluation
- security: Security assessment

[Analysis complete in ~9 seconds]
```

### My Response - Phase 3 (Validation)
```
## Project Analysis Validation ✋

**Detected Configuration:**
- Framework: React with TypeScript
- Architecture: Component-based with Redux state management
- Complexity: 0.70/1.0 (high)
- Phase: Growth (6-18 months)

**Quality Standards:**
- Testing: Jest with React Testing Library, 82% coverage
- Linting: ESLint with Airbnb config
- Type checking: TypeScript strict mode
- CI/CD: GitHub Actions detected
- Security: 2 outdated dependencies (non-critical)

**Files Analyzed:**
- package.json: React 18.2, TypeScript 5.0, Jest, ESLint
- src/components/: Hooks-based component architecture
- src/store/: Redux Toolkit slices and sagas
- tests/: Comprehensive test suite

## Your Options:
- ✅ Proceed with detected setup
- 🔄 Modify detected patterns
- 📝 Custom architecture description
- 🚫 Start with minimal setup

What would you prefer for the initial setup?
```

### User Response (Modification Path)
```
User: "Modify detected patterns"
```

### My Follow-up
```
What would you like to adjust?

Options to modify:
- Coverage threshold (currently >= 80%)
- Linting rules
- Architecture pattern description
- Project phase classification
- Quality standards
```

### User Modification
```
User: "Change coverage requirement to 90% and add stricter ESLint rules"
```

### My Confirmation
```
Updated:
- Coverage threshold: >= 90%
- ESLint: Added stricter rules to config

Anything else to modify?
```

### User Confirmation
```
User: "No, proceed"
```

### My Response - Phase 4 (Completion)
```
✅ Initialization complete with your customizations!

**Generated Documentation:**
- .quaestor/AGENT.md
- .quaestor/ARCHITECTURE.md (with TypeScript quality standards + your customizations)
- CLAUDE.md

**Customizations Applied:**
- Coverage threshold set to >= 90%
- Stricter ESLint configuration documented

**Next Steps:**
1. Review .quaestor/ARCHITECTURE.md - your customizations are in Section 3
2. Run your first quality check: `npm run lint && npm test`
3. Create specifications and start development
```

---

## Example 3: Rust Axum Project with Custom Architecture

### User Request
```
User: "Analyze my project structure and initialize Quaestor"
```

### My Response - Phase 3 (Validation)
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
- Type checking: Rust's built-in type system
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

What would you prefer?
```

### User Response (Custom Architecture Path)
```
User: "Custom architecture description"
```

### My Follow-up
```
Please describe your project architecture. I'll use your description instead of the detected patterns.

What I'd like to know:
- Architecture pattern (if different from "Layered")
- Key components and responsibilities
- Design principles you're following
- Quality standards and testing strategy
```

### User Description
```
User: "We use Hexagonal Architecture with Domain-Driven Design. The domain layer is completely isolated, application layer orchestrates use cases, and infrastructure layer handles persistence and external APIs. We follow CQRS for complex operations and aim for 85% test coverage with property-based testing."
```

### My Confirmation
```
Got it! I'll document your architecture as:

- **Pattern**: Hexagonal Architecture with Domain-Driven Design
- **Layers**: Domain (isolated), Application (orchestration), Infrastructure (adapters)
- **Patterns**: CQRS for complex operations
- **Testing**: 85% coverage with property-based testing

Does this accurately represent your architecture?
```

### User Confirmation
```
User: "Yes, perfect"
```

### My Response - Phase 4 (Completion)
```
✅ Initialization complete with your custom architecture!

**Generated Documentation:**
- .quaestor/AGENT.md
- .quaestor/ARCHITECTURE.md (with your Hexagonal/DDD architecture)
- CLAUDE.md

**Your Architecture:**
- Pattern: Hexagonal Architecture with Domain-Driven Design
- CQRS pattern documented
- 85% coverage target configured
- Property-based testing noted

**Next Steps:**
1. Review .quaestor/ARCHITECTURE.md Section 2 - your architecture is documented
2. Your custom testing strategy is in Section 5
3. Start implementing specifications with your architecture patterns
```

---

## Example 4: Minimal Setup for New Project

### User Request
```
User: "Initialize Quaestor in this project"
```

### Context
User has an empty/new project with minimal files.

### My Response - Phase 3 (Validation)
```
## Project Analysis Validation ✋

**Detected Configuration:**
- Framework: Unable to detect (minimal files found)
- Architecture: Unknown (new project)
- Complexity: 0.0/1.0 (new project)
- Phase: Startup (0-6 months)

**Quality Standards:**
- No existing quality tools detected
- No tests found
- No CI/CD configured

**Files Analyzed:**
- No significant project files found
- This appears to be a new project

**Recommendation:** Consider using minimal setup and configuring quality standards manually as your project develops.

## Your Options:
- ✅ Proceed with detected setup (basic defaults)
- 🔄 Modify detected patterns
- 📝 Custom architecture description
- 🚫 Start with minimal setup (recommended for new projects)

What would you prefer?
```

### User Response
```
User: "Start with minimal setup"
```

### My Response - Phase 4 (Completion)
```
✅ Minimal setup complete!

**Generated Documentation:**
- .quaestor/AGENT.md (standard workflow rules)
- .quaestor/ARCHITECTURE.md (template - customize as you develop)
- CLAUDE.md

**What to do next:**
1. Edit .quaestor/ARCHITECTURE.md as your project takes shape:
   - Fill in Section 1: Project Configuration
   - Define Section 2: Architecture Overview
   - Configure Section 3: Code Quality Standards (add commands as you adopt tools)

2. Install quality tools for your language/framework:
   - Python: `pip install ruff mypy pytest`
   - TypeScript: `npm install -D eslint prettier jest`
   - Rust: Already has clippy, rustfmt, cargo test

3. Return anytime to re-analyze:
   - "Analyze my project" to update configuration
   - All skills remain available via plugin/CLI

**Minimal Structure Created:**
- .quaestor/specs/draft/
- .quaestor/specs/active/
- .quaestor/specs/completed/
- .quaestor/specs/archived/
```

---

## Example 5: Error Handling - Agent Failure

### Scenario
One or more agents fail during analysis.

### My Response (Graceful Degradation)
```
🔍 Analyzing your project...

Spawning specialized agents:
- researcher: ✓ Complete (Python FastAPI detected)
- architect: ⚠ Timeout (10s limit reached)
- security: ✓ Complete (No major issues)

Note: Architecture analysis incomplete. Using basic pattern detection.

## Project Analysis Validation ✋

**Detected Configuration:**
- Framework: FastAPI with SQLAlchemy
- Architecture: Basic pattern detection (architect agent timed out)
  - Detected: Repository pattern in infrastructure/
  - Detected: Domain models in domain/
  - Recommendation: Review and customize architecture section
- Complexity: 0.50/1.0 (estimated from available metrics)
- Phase: Growth (6-18 months)

**Quality Standards:**
- Testing: pytest detected
- Linting: ruff detected
- Type checking: mypy in pyproject.toml
- Security: No major vulnerabilities

**Files Analyzed:**
- pyproject.toml: Dependencies analyzed
- src/: Basic structure reviewed
- tests/: Test suite found

⚠ **Note**: Architecture analysis was incomplete. The generated ARCHITECTURE.md will have a basic template in Section 2. Please review and customize it based on your actual architecture.

## Your Options:
- ✅ Proceed with detected setup (with basic architecture template)
- 🔄 Modify detected patterns
- 📝 Custom architecture description (recommended due to incomplete analysis)
- 🚫 Start with minimal setup

What would you prefer?
```

This shows graceful degradation when agents fail - I continue with available data and clearly communicate limitations.

---

## Common Workflows Summary

### Quick Accept (Most Common)
```
1. User: "Initialize Quaestor"
2. Me: [Analysis + Validation with all detected info]
3. User: "Proceed"
4. Me: [Complete setup]
```

### Modification Path
```
1. User: "Initialize Quaestor"
2. Me: [Analysis + Validation]
3. User: "Modify detected patterns"
4. Me: "What to adjust?"
5. User: [Specific changes]
6. Me: [Confirmation]
7. User: "Proceed"
8. Me: [Complete with modifications]
```

### Custom Architecture Path
```
1. User: "Initialize Quaestor"
2. Me: [Analysis + Validation]
3. User: "Custom architecture description"
4. Me: "Please describe your architecture"
5. User: [Detailed architecture explanation]
6. Me: [Confirmation of understanding]
7. User: "Yes"
8. Me: [Complete with custom architecture]
```

### Minimal Setup Path
```
1. User: "Initialize Quaestor" (in empty/new project)
2. Me: [Analysis shows minimal project]
3. User: "Minimal setup"
4. Me: [Create basic templates for user to customize]
```

---

*These examples demonstrate the complete initialization workflow across different project types and user interaction patterns.*
