---
allowed-tools: [Read, Bash, Glob, Grep, Edit, MultiEdit, Write, TodoWrite, Task]
description: "Intelligent project analysis with auto-framework detection and adaptive setup"
agent-strategy:
  project_analysis: [researcher, architect]
  security_audit: security
  documentation: [architect, implementer]
  quality_definition: qa
---

# /project-init - Intelligent Project Initialization

## Purpose
Analyze project architecture, detect frameworks and patterns, then generate intelligent Quaestor setup with auto-populated documentation.

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
- **New projects**: Generate starter architecture + documentation
- **Existing projects**: Analyze current state + fill gaps
- **Migration**: Import existing docs + enhance with Quaestor

## Execution: Analyze → Generate → Validate → Setup

### Phase 1: Project Analysis 🔍

**Agent-Orchestrated Discovery:**

Use the Task tool to spawn specialized agents for parallel analysis:

```yaml
Parallel Agent Execution:
  1. Framework & Dependency Analysis:
     Agent: researcher
     Mission: "Analyze the project structure and identify:
       - Primary programming language and framework
       - Project dependencies from package.json/requirements.txt/Cargo.toml/go.mod
       - Test framework and current coverage
       - Build tools and scripts
       Output as structured YAML with framework, dependencies, and tools"
  
  2. Architecture Pattern Analysis:
     Agent: architect
     Mission: "Evaluate the codebase architecture:
       - Identify architecture patterns (MVC, DDD, VSA, Clean Architecture)
       - Map component relationships and boundaries
       - Assess API design patterns
       - Analyze database architecture
       - Identify technical debt and complexity hotspots
       Output as structured analysis with patterns, strengths, and concerns"
  
  3. Security Assessment:
     Agent: security
     Mission: "Perform security analysis on the project:
       - Identify security patterns and anti-patterns
       - Check for common vulnerabilities
       - Assess authentication/authorization approach
       - Review data handling and encryption
       - Evaluate dependency security
       Output as security assessment with risks and recommendations"
```

**Result Consolidation:**
After all agents complete, consolidate findings into a unified analysis:
```yaml
Consolidated Analysis:
  Framework: [from researcher]
  Architecture: [from architect]
  Security: [from security]
  Complexity: [calculated score]
  Phase: [new|growth|legacy based on analysis]
```

### Phase 2: Document Generation ⚡
**Based on agent analysis, generate:**
```yaml
Generated Documents:
  - ARCHITECTURE.md: From architect agent analysis
  - RULES.md: Framework-specific from analysis
  - QUAESTOR_CLAUDE.md: AI collaboration guidelines
```

**Note:** Use `/plan --spec` command to create project specifications after initialization.

### Phase 3: User Validation ✅ **[MANDATORY - DO NOT SKIP]**

⚠️ **CRITICAL ENFORCEMENT RULE:**
```yaml
before_phase_4:
  MUST_PRESENT_ANALYSIS:
    - framework_detection_results
    - architecture_pattern_analysis  
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

**Quality Standards:**
[detected_tools_and_standards]

## Your Options:
- ✅ Proceed with detected setup
- 🔄 Modify detected patterns
- 📝 Custom architecture description
- 🚫 Start with minimal setup

What would you prefer for the initial setup?
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
  - Inferred patterns from git history
  - Framework-specific quality standards
```

**Document Population:**
```yaml
mandatory_actions:
  - populate_architecture_md: "Real project analysis"
  - update_critical_rules: "Framework-specific guidelines"
  - configure_quality_standards: "Testing and linting setup"
  - create_initial_specifications: "Draft/ folder for new specs"
```

## Framework-Specific Intelligence

### React/Frontend Projects
```yaml
React Analysis:
  State Management: Redux|Context|Zustand detection
  Component Patterns: HOC|Hooks|Render Props
  Architecture: SPA|SSR|Static Site patterns
  Quality Gates: ESLint + Prettier + TypeScript
  
Detected Patterns:
  - Component-based architecture
  - State management approach
  - Testing infrastructure
  - Build and deployment setup
```

### Python/Backend Projects
```yaml
Python Analysis:
  Framework: Django|FastAPI|Flask detection
  Patterns: MVC|Repository|Service Layer
  Testing: pytest|unittest setup
  Quality Gates: ruff + mypy + pytest
  
Detected Patterns:
  - API architecture style
  - Authentication approach
  - Database patterns
  - Deployment configuration
```

## Agent Error Handling

**Graceful Degradation for Agent Failures:**
```yaml
Error Handling Strategy:
  If researcher agent fails:
    - Fall back to basic file detection (package.json, requirements.txt)
    - Log: "Framework detection limited - manual review recommended"
    - Continue with available data
  
  If architect agent fails:
    - Use simplified pattern detection based on folder structure
    - Log: "Architecture analysis incomplete - patterns may be missed"
    - Continue with basic analysis
  
  If security agent fails:
    - Flag for manual security review
    - Log: "Security assessment skipped - manual review required"
    - Continue without security recommendations
  
  If any agent fails:
    - Continue with available analysis
    - Log failure for user awareness
    - Provide manual guidance

Performance Monitoring:
  - Total time limit: 30 seconds
  - Individual agent timeout: 10 seconds
  - Parallel execution to maximize efficiency
```

## Getting Started After Initialization

### Next Steps
1. Review generated documentation:
   - `.quaestor/ARCHITECTURE.md` - Project structure analysis
   - `.quaestor/RULES.md` - Framework-specific guidelines
   - `.quaestor/specs/` - Folder structure for specs

2. Create project specifications:
   - Use `/plan --spec` to create new specifications
   - Use `/plan` to view project progress
   - Use `/impl` to implement specifications

3. Start development:
   - Follow the Research → Plan → Implement workflow
   - Use appropriate agents for complex tasks
   - Maintain documentation as you progress

### Agent Invocation Examples
**How Agents Work Together:**
```yaml
Phase 1 - Parallel Analysis:
  researcher agent:
    Input: Project directory
    Output: Framework, dependencies, tools
    Example: "Detected: React 18.2, TypeScript 5.0, Jest, ESLint"
  
  architect agent:
    Input: Codebase structure
    Output: Patterns, architecture, complexity
    Example: "Found: Component-based, Redux state, 0.7 complexity"
  
  security agent:
    Input: Code and dependencies
    Output: Vulnerabilities, recommendations
    Example: "2 outdated deps, auth pattern needed"
```

## Project Phase Detection
**Smart Phase Analysis:**
```yaml
Project Analysis → Phase Detection:
  - New projects: Foundation phase
  - In-progress: Analyze git history → identify current phase
  - Legacy: Assessment and modernization needs
  
Project Phases:
  Startup (0-6 months):
    - MVP Foundation
    - Core Features
    - User Feedback Integration
  
  Growth (6-18 months):
    - Performance Optimization
    - Feature Expansion
    - Production Hardening
  
  Enterprise (18+ months):
    - Architecture Evolution
    - Scalability Improvements
    - Platform Maturation
```

## Success Criteria
**Initialization Complete:**
- ✅ Framework and architecture accurately detected
- ✅ **USER VALIDATION COMPLETED** ← **MANDATORY**
- ✅ Documents generated with real project data
- ✅ Quality standards configured for tech stack
- ✅ Project ready for development

**Framework Integration:**
- ✅ Language-specific quality gates configured
- ✅ Testing patterns and tools detected
- ✅ Build and deployment awareness established
- ✅ Performance benchmarks appropriate for stack

### Real-World Validation Example
**What Users Actually See:**
```
## Project Analysis Validation ✋

**Detected Configuration:**
- Framework: React with TypeScript
- Architecture: Component-based with Redux
- Complexity: 0.7/1.0
- Phase: Growth (6-18 months)

**Quality Standards:**
- Testing: Jest + React Testing Library
- Linting: ESLint with Airbnb config
- Type checking: TypeScript strict mode
- CI/CD: GitHub Actions detected

## Your Options:
- ✅ Proceed with detected setup
- 🔄 Modify detected patterns
- 📝 Custom architecture description
- 🚫 Start with minimal setup

What would you prefer for the initial setup?

**Note:** After initialization, use `/plan --spec` to create project specifications.
```

---
*Intelligent framework detection with adaptive project setup and auto-generated documentation*

