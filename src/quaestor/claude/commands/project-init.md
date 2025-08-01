---
allowed-tools: [Read, Bash, Glob, Grep, Edit, MultiEdit, Write, TodoWrite, Task]
description: "Intelligent project analysis with auto-framework detection and adaptive setup"
performance-profile: "complex"
complexity-threshold: 0.6
auto-activation: ["framework-detection", "pattern-analysis", "adaptive-setup"]
intelligence-features: ["architecture-detection", "stack-analysis", "specification-generation"]
agent-strategy:
  project_analysis: [researcher, architect]
  security_audit: security
  spec_generation: planner
  documentation: [architect, implementer]
  quality_definition: qa
---

# /project-init - Intelligent Project Initialization

## Purpose
Analyze project architecture, detect frameworks and patterns, then generate intelligent Quaestor setup with auto-populated documentation and milestones.

## Usage
```
/project-init
/project-init --type web-api
/project-init --existing --migrate
```

## Auto-Intelligence

### Framework Detection
```yaml
Stack Analysis:
  - Language: Auto-detect → Python|Rust|JS|TS|Go standards
  - Framework: React|Django|Express|FastAPI|Axum patterns
  - Architecture: MVC|DDD|VSA|Microservices detection
  - Patterns: Repository|Service|CQRS|Event-driven
```

### Adaptive Setup
- **New projects**: Generate starter architecture + milestones
- **Existing projects**: Analyze current state + fill gaps
- **Migration**: Import existing docs + enhance with Quaestor

## Execution: Analyze → Generate → Validate → Setup

### Phase 1: Project Analysis 🔍

**Intelligent Discovery:**
```yaml
Framework Detection:
  - package.json → React|Vue|Angular|Express
  - requirements.txt → Django|FastAPI|Flask
  - Cargo.toml → Axum|Actix|Rocket
  - go.mod → Gin|Echo|Fiber
  
Architecture Patterns:
  - Features/ → Vertical Slice Architecture
  - Domain/ → Domain-Driven Design
  - controllers/models/views → MVC
  - services/ → Service Layer
```

**Code Quality Analysis:**
```yaml
Pattern Detection:
  - VSA: Features/ folders → Jimmy Bogard's pattern
  - DDD: Domain/Application/Infrastructure layers
  - Clean Architecture: Entities/UseCases/Adapters
  - Enterprise Patterns: Repository|Service|UnitOfWork
  
Code Smell Detection:
  - Bloaters: Long methods, large classes
  - OOP Abusers: Switch statements, refused bequest
  - Change Preventers: Divergent change, shotgun surgery
  - Dispensables: Dead code, lazy classes
  - Couplers: Feature envy, message chains
```

### Phase 2: Intelligent Generation ⚡
**Auto-Document Creation:**
```yaml
Generated Documents:
  - ARCHITECTURE.md: Detected patterns + structure
  - MEMORY.md: Current state + auto-milestones  
  - manifest.json: Project metadata + tracking
  - CRITICAL_RULES.md: Framework-specific guidelines
```

### Phase 3: User Validation ✅ **[MANDATORY - DO NOT SKIP]**

⚠️ **CRITICAL ENFORCEMENT RULE:**
```yaml
before_phase_4:
  MUST_PRESENT_ANALYSIS:
    - framework_detection_results
    - architecture_pattern_analysis  
    - proposed_milestones
    - quality_standards_detected
  
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

**MANDATORY Interactive Confirmation Template:**
```
## Project Analysis Validation ✋

**Detected Configuration:**
- Framework: [detected_framework]
- Architecture: [detected_pattern]
- Complexity: [score]/1.0
- Phase: [project_phase]

**Proposed Milestones:**
[list_proposed_milestones]

**Quality Standards:**
[detected_tools_and_standards]

## Your Options:
- ✅ Proceed with detected setup
- 🔄 Modify detected patterns
- 📝 Custom architecture description  
- 🚫 Start with minimal setup

## Milestone Creation:
- ⭐ Create milestone files (.quaestor/milestones/*/README.md + tasks.yaml)
- 📝 Documentation only (just populate MEMORY.md templates)

What would you prefer for setup and milestones?
```

### Phase 4: Setup Completion 🚀 **[ONLY AFTER USER APPROVAL]**

**Document Generation:**
```yaml
Template Selection:
  - Framework-specific: React|Django|Express templates
  - Pattern-specific: MVC|DDD|VSA structures
  - Size-appropriate: Startup|Enterprise|Legacy setups
  
Auto-Population:
  - Real paths from project structure
  - Detected components and responsibilities
  - Inferred milestones from git history
  - Framework-specific quality standards
```

**Conditional Milestone Creation:**
```yaml
if_user_chose_milestone_files:
  actions:
    - create_directories: ".quaestor/milestones/[milestone_id]/"
    - generate_readme: "Goals, success criteria, timeline"
    - create_tasks_yaml: "Structured subtask tracking with status"
    - initialize_notes: "Implementation notes and decisions"
  
if_user_chose_documentation_only:
  actions:
    - populate_memory_templates: "Update MEMORY.md with milestone information"
    - skip_milestone_directories: "No .quaestor/milestones/ creation"

mandatory_for_both:
  - populate_architecture_md: "Real project analysis"
  - update_critical_rules: "Framework-specific guidelines"
  - configure_quality_standards: "Testing and linting setup"
```

## Framework-Specific Intelligence

### React/Frontend Projects
```yaml
React Analysis:
  State Management: Redux|Context|Zustand detection
  Component Patterns: HOC|Hooks|Render Props
  Architecture: SPA|SSR|Static Site patterns
  Quality Gates: ESLint + Prettier + TypeScript
  
Generated Milestones:
  - Component Library Setup
  - State Management Implementation
  - Testing Infrastructure
  - Performance Optimization
```

### Python/Backend Projects
```yaml
Python Analysis:
  Framework: Django|FastAPI|Flask detection
  Patterns: MVC|Repository|Service Layer
  Testing: pytest|unittest setup
  Quality Gates: ruff + mypy + pytest
  
Generated Milestones:
  - API Design & Models
  - Authentication System
  - Database Integration
  - Production Deployment
```

## Adaptive Milestone Generation
**Smart Phase Detection:**
```yaml
Project Analysis → Milestone Generation:
  - New projects: Foundation → Core → Polish phases
  - In-progress: Analyze git history → identify next logical phase
  - Legacy: Assessment → Modernization → Enhancement
  
Example Milestone Sets:
  Startup (0-6 months):
    - "MVP Foundation"
    - "Core Features"
    - "User Feedback Integration"
  
  Growth (6-18 months):
    - "Performance Optimization"
    - "Feature Expansion"
    - "Production Hardening"
  
  Enterprise (18+ months):
    - "Architecture Evolution"
    - "Scalability Improvements"
    - "Platform Maturation"
```

## Success Criteria
**Initialization Complete:**
- ✅ Framework and architecture accurately detected
- ✅ **USER VALIDATION COMPLETED** ← **MANDATORY**
- ✅ Documents generated with real project data
- ✅ Milestones aligned with project phase and goals
- ✅ Quality standards configured for tech stack
- ✅ First milestone ready for /task execution

**Framework Integration:**
- ✅ Language-specific quality gates configured
- ✅ Testing patterns and tools detected
- ✅ Build and deployment awareness established
- ✅ Performance benchmarks appropriate for stack

---
*Intelligent framework detection with adaptive project setup and auto-generated documentation*

