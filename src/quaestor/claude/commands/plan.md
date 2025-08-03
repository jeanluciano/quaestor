---
allowed-tools: [Read, Edit, MultiEdit, Write, Bash, Grep, Glob, LS, Task, TodoWrite]
description: "Specification-driven planning, project management, and progress tracking with multi-agent orchestration"
performance-profile: "complex"
complexity-threshold: 0.5
auto-activation: ["specification-planning", "project-planning", "progress-visualization", "strategic-analysis"]
intelligence-features: ["spec-tracking", "velocity-tracking", "architecture-planning", "contract-validation"]
agent-strategy:
  specification_design: planner
  system_design: architect
  project_planning: architect
  spec_breakdown: [planner, architect, implementer]
  risk_assessment: security
  progress_analysis: researcher
---

# /plan - Specification-Driven Planning & Progress Management

## Purpose
Design specifications, plan work through spec-driven development, manage projects, track progress, and make strategic decisions. Combines specification management with progress visualization and architectural planning.

## Usage
```
/plan                           # Show progress dashboard with specs
/plan --spec "User Auth"        # Create new specification
/plan --create "MVP Complete"   # Create new project phase
/plan --complete               # Complete current project phase
/plan --analyze                # Deep strategic analysis
/plan --architecture          # Architectural planning mode
/plan --link                   # Link current branch to spec
/plan --activate <spec-id>     # Move spec from draft to active
/plan --archive <spec-id>      # Move spec from active to completed
/plan --migrate                # Migrate flat specs to folders
```

## Auto-Intelligence

### Multi-Mode Planning
```yaml
Mode Detection:
  - No args → Progress dashboard with folder stats
  - --spec → Specification creation wizard (creates in draft/)
  - --create → Project phase creation wizard
  - --complete → Completion validation
  - --analyze → Strategic analysis
  - --architecture → System design planning
  - --link → Branch-to-spec linkage
  - --activate → Move spec to active/ folder
  - --archive → Move spec to completed/ folder
  - --migrate → Migrate flat specs to folders
```

### Agent Orchestration
```yaml
Specification Design:
  - planner: Create specs with contracts
  - architect: Validate technical approach
  - implementer: Estimate complexity
  
Progress Analysis:
  - researcher: Gather spec status and metrics
  - architect: Analyze system evolution
  
Project Planning:
  - architect: Design project structure
  - planner: Break down into specifications
  - security: Risk assessment
  
Strategic Analysis:
  - architect: Technical debt and opportunities
  - researcher: Pattern analysis
  - All agents: Domain-specific insights
```

## Execution: Analyze → Plan → Track → Archive

### Folder Management Integration
**Automatic folder-based specification lifecycle:**
```yaml
On First Run:
  - Initialize FolderManager with .quaestor/specifications/
  - Create folder structure: draft/, active/, completed/
  - Migrate existing flat specifications to appropriate folders
  - Update manifest with folder locations

Folder Operations:
  - New spec → Create in draft/
  - Start work → Move to active/ (max 3)
  - Complete → Move to completed/
  - All moves atomic with git tracking

Specification Context:
  - Use active/ folder specs as source of truth
  - No separate MEMORY.md file needed
  - Context loaded directly from active specifications
  - Completed specs archived in completed/ folder
```

### Phase 0: Progress Dashboard 📊
**Default Mode - Comprehensive Status Overview:**
```yaml
Data Collection (Parallel):
  - Folder statistics: draft/active/completed counts via FolderManager
  - Active specifications: Read from active/ folder (max 3)
  - Active work: Read directly from active specifications
  - Git metrics: commits, velocity, contributors
  - Quality metrics: test/lint status per spec
  - Architecture health: dependency analysis
  - Project progress: folder-based completion tracking

Visual Presentation:
  🎯 Project: [Name] • Phase: [Current Phase]
  
  📈 Progress Overview:
  Overall: [████████░░] 80% • Velocity: ↑15% this week
  
  📁 Specification Folders:
  • draft/: 5 specs ready to start
  • active/: 2/3 slots used (can add 1 more)
  • completed/: 12 specs archived
  
  📋 Active Specifications (active/):
  • [feat-auth-001] User Authentication
    Folder: active/ • Branch: feat/spec-auth-001-user-auth
    Contract: ✅ Defined • Tests: [████░░░░░░] 4/10
    
  • [feat-api-002] REST API Design  
    Folder: active/ • Branch: feat/spec-api-002-rest-design
    Contract: ✅ Defined • Tests: [██████████] 10/10
  
  📊 Current Phase: [Name]
  Specs:    [███████░░░] 7/10 complete
  Quality:  [██████████] All checks passing ✅
  Docs:     [████████░░] 80% updated
  
  ⚡ Velocity Metrics:
  • This Week: 12 commits, 4 specs completed
  • Average: 2.3 specs/week, 87% on-time delivery
  • Trend: 📈 Accelerating
  
  🏗️ Architecture Health:
  • Technical Debt: Low (score: 82/100)
  • Test Coverage: 87% (↑3% this week)
  • Dependencies: All up to date ✅
  
  💡 Insights:
  • Strong momentum on authentication specs
  • 3 specs awaiting implementation
  • Ready for phase completion review
  
  🎯 Recommended Next Action:
  → Complete remaining 3 specifications
  → Run: /plan --spec to create next spec
  → Run: /plan --complete when ready
```

### Phase 1: Status Assessment 🔍
**Current Phase Analysis:**
```yaml
Discovery:
  - Read: .quaestor/MEMORY.md → current phase section
  - Parse: planned|active|completed items
  - Check: .quaestor/specifications/*.yaml files
  - Assess: overall completion percentage
```

### Phase 2: Completion Validation ✅
**Evidence-Based Readiness Check:**
```yaml
Quality Gates:
  - ✅ All planned tasks marked complete
  - ✅ Tests passing (run quality check)
  - ✅ Documentation current
  - ✅ No critical TODOs remaining
  - ✅ Success criteria met

Intelligent Verification:
  - Parse: task completion evidence
  - Validate: measurable outcomes achieved
  - Confirm: no blocking issues remain
```

### Phase 3: Intelligent Archiving 📦
**Automated Archive Process:**
```yaml
Archive Generation:
  1. Extract: key achievements + technical highlights
  2. Categorize: features|fixes|improvements|patterns
  3. Document: architectural decisions + trade-offs
  4. Quantify: metrics (tests, coverage, files, commits)
  5. Preserve: lessons learned + future considerations
```

**Archive Structure:**
```
## 🎉 Phase Complete: [Name] - [Date]

### Summary
[X] tasks completed over [duration] • [Y] commits • [Z] files modified

### Key Achievements
• [Feature 1] - [Impact/value]
• [Feature 2] - [Impact/value]
• [Pattern/Decision] - [Rationale]

### Quality Metrics
- Tests: [count] passing ([coverage]%)
- Linting: ✅ Clean
- Type Coverage: [percentage]
- Performance: [metrics if applicable]

### Technical Evolution  
• [Architectural pattern established]
• [Framework/library decisions]
• [Infrastructure improvements]

### Next Phase Focus
[Identified next logical phase based on current progress]
```

### Phase 4: Next Phase Planning 🚀
**Intelligent Next Phase Suggestion:**
```yaml
Planning Intelligence:
  - Analyze: current architecture + remaining TODOs
  - Identify: logical next development phase
  - Suggest: phase scope + success criteria
  - Estimate: duration based on current velocity
```

## Specification Creation Workflow (--spec)

### Initial Setup
```yaml
Directory Structure:
  - Use FolderManager to create folder structure:
    - draft/     # New specifications start here
    - active/    # In-progress (max 3 specifications)
    - completed/ # Finished specifications
  - Automatic migration of existing flat specifications
  - Git integration for history preservation
```

### Guided Specification Process
```yaml
Context Gathering:
  1. Title: "What feature/fix are you planning?"
  2. Type: "Is this a feature, bugfix, refactor, etc?"
  3. Description: "What exactly needs to be built?"
  4. Rationale: "Why is this needed?"

Contract Definition:
  1. Inputs: "What data/parameters are required?"
  2. Outputs: "What will be produced/returned?"
  3. Behavior: "What are the key rules/logic?"
  4. Constraints: "Any performance/security requirements?"

Acceptance Criteria:
  - Define: measurable success conditions
  - Create: test scenarios with Given/When/Then
  - Link: to existing specifications if dependent

Branch Creation:
  - Generate: spec-compliant branch name
  - Link: specification to branch
  - Update: spec status to ACTIVE
```

### Specification Output Template
```yaml
Specification Created:
  ID: feat-auth-001
  Title: User Authentication System
  Type: feature
  Priority: high
  Status: DRAFT → ACTIVE
  
  Contract:
    Inputs:
      - username: string (required)
      - password: string (required, min 8 chars)
    Outputs:
      - token: JWT string
      - user: User object
    Behavior:
      - Validate credentials against database
      - Generate JWT with 24h expiration
      - Log authentication attempts
      
  Branch: feat/spec-auth-001-user-authentication
  Folder: draft/ → Will move to active/ when work begins
  
  Next Steps:
  1. Review specification contract
  2. Run /plan --activate spec-auth-001 to move to active/
  3. Implement according to acceptance criteria
  4. Run /plan --complete spec-auth-001 to archive
```

## Project Phase Creation Workflow

### Guided Creation Process
```yaml
Context Gathering:
  1. Goal: "What's the main objective?"
  2. Scope: "What are the key deliverables?"
  3. Criteria: "How will we measure success?"
  4. Duration: "Estimated timeframe?"

Specification Planning:
  - Identify: specifications needed for phase
  - Prioritize: critical vs nice-to-have specs
  - Estimate: complexity and dependencies
  
Template Generation:
  - Create: structured phase section in MEMORY.md
  - Initialize: specification tracking
  - Set: measurable success criteria
  - Link: to specification manifest
```

### Creation Output Template
```yaml
New Phase Structure:
  - Header: "🚀 Phase: [Name]"
  - Goals: [Numbered objectives]
  - Planned_Tasks: [Checkbox list]
  - Success_Criteria: [Measurable outcomes]
  - In_Progress: []
  - Completed: []
  - Estimated_Duration: [Based on scope analysis]
```

## Advanced Planning Modes

### Strategic Analysis Mode (--analyze)
**Deep Technical and Architectural Analysis:**
```yaml
Multi-Agent Analysis:
  - architect: System design evaluation
  - researcher: Pattern and debt analysis
  - security: Risk assessment
  - implementer: Performance review

Output Structure:
  📊 Strategic Analysis Report
  
  🏗️ Architecture Assessment:
  • Current patterns: [MVC, Repository, etc.]
  • Technical debt: [Quantified with locations]
  • Scalability concerns: [Bottlenecks identified]
  • Recommended refactorings: [Prioritized list]
  
  🔍 Code Quality Insights:
  • Complexity hotspots: [Files exceeding thresholds]
  • Test coverage gaps: [Modules needing tests]
  • Documentation needs: [APIs lacking docs]
  
  🚀 Opportunities:
  • Performance optimizations: [Quick wins]
  • Architecture improvements: [Long-term]
  • Security enhancements: [Priority fixes]
  
  📋 Strategic Recommendations:
  1. [High-impact, low-effort items]
  2. [Technical debt to address]
  3. [Architecture evolution path]
```


### Architecture Planning Mode (--architecture)
**System Design and Evolution Planning:**
```yaml
Agent Collaboration:
  - architect: Lead design decisions
  - security: Security architecture
  - implementer: Feasibility assessment
  - researcher: Pattern research

Planning Output:
  🏗️ Architecture Planning Session
  
  📐 Current State:
  • Pattern: [Layered Architecture]
  • Components: [List with relationships]
  • Dependencies: [Internal/External]
  
  🎯 Proposed Evolution:
  • Short-term: [Immediate improvements]
  • Medium-term: [Structural changes]
  • Long-term: [Architecture vision]
  
  ⚡ Implementation Plan:
  1. [Refactor X to pattern Y]
  2. [Extract service Z]
  3. [Implement caching layer]
  
  📊 Impact Analysis:
  • Performance: +30% expected
  • Maintainability: Improved
  • Complexity: Managed increase
  • Risk: Low-Medium
```

## Quality Integration

**Automatic Quality Validation:**
- **Before completion** → Run `/check` to validate readiness
- **Evidence requirement** → All quality gates must pass
- **Metrics capture** → Document test coverage, performance benchmarks
- **Standards compliance** → Verify against project quality standards

## Success Criteria

**Specification Creation:**
- ✅ Clear contract with inputs/outputs defined
- ✅ Acceptance criteria measurable and testable
- ✅ Test scenarios documented
- ✅ Branch created and linked to spec
- ✅ Specification tracked in manifest

**Phase Completion:**
- ✅ All planned specifications completed
- ✅ Spec contracts validated and complete
- ✅ Quality gates passed (tests, linting, types)
- ✅ Documentation updated and current
- ✅ Success criteria measurably achieved
- ✅ Archive generated with evidence + insights

**Phase Creation:**
- ✅ Clear, measurable objectives defined
- ✅ Specifications identified and prioritized
- ✅ Success criteria established
- ✅ Progress tracking initialized
- ✅ Integration with specification system

## Integration Points

**Quaestor Ecosystem:**
- **specifications/** → Specification manifest and tracking
- **MEMORY.md** → Primary phase and spec progress
- **ARCHITECTURE.md** → Update with architectural decisions
- **specifications/** → Specification-level tracking
- **Git branches** → Automatic spec-to-branch linkage
- **Quality system** → Integrated validation per specification
- **Hooks** → specification tracking and validation

## Implementation Guide

**Using FolderManager:**
```python
from quaestor.core.folder_manager import FolderManager

# Initialize manager
folder_mgr = FolderManager(Path(".quaestor/specifications"))

# First run - setup folders
result = folder_mgr.create_folder_structure()
if result.success:
    # Migrate existing specs
    folder_mgr.migrate_flat_specifications()

# Move spec to active
result = folder_mgr.move_specification(
    Path("draft/spec-auth-001.yaml"), 
    "active"
)
```

**Folder Operations:**
- Create spec → Save to draft/
- Activate → Check limit, move to active/
- Complete → Move to completed/, update memory
- All operations atomic with rollback

---
*Intelligent specification-driven planning with folder-based lifecycle management*