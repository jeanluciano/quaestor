---
allowed-tools: [Read, Edit, MultiEdit, Write, Bash, Grep, Glob, LS, Task, TodoWrite]
description: "Strategic planning, milestone management, and progress tracking with multi-agent orchestration"
performance-profile: "complex"
complexity-threshold: 0.5
auto-activation: ["milestone-planning", "progress-visualization", "strategic-analysis"]
intelligence-features: ["velocity-tracking", "architecture-planning", "resource-estimation"]
agent-strategy:
  system_design: architect
  milestone_planning: architect
  task_breakdown: [architect, implementer]
  risk_assessment: security
  progress_analysis: researcher
---

# /plan - Strategic Planning & Progress Management

## Purpose
Plan work, manage milestones, track progress, and make strategic decisions. Combines milestone management with progress visualization and architectural planning.

## Usage
```
/plan                           # Show progress dashboard
/plan --create "MVP Complete"   # Create new milestone
/plan --complete               # Complete current milestone
/plan --analyze                # Deep strategic analysis
/plan --velocity              # Show velocity metrics
/plan --architecture          # Architectural planning mode
```

## Auto-Intelligence

### Multi-Mode Planning
```yaml
Mode Detection:
  - No args → Progress dashboard
  - --create → Milestone creation wizard
  - --complete → Completion validation
  - --analyze → Strategic analysis
  - --velocity → Performance metrics
  - --architecture → System design planning
```

### Agent Orchestration
```yaml
Progress Analysis:
  - researcher: Gather metrics and history
  - architect: Analyze system evolution
  
Milestone Planning:
  - architect: Design milestone structure
  - implementer: Estimate effort
  - security: Risk assessment
  
Strategic Analysis:
  - architect: Technical debt and opportunities
  - researcher: Pattern analysis
  - All agents: Domain-specific insights
```

## Execution: Analyze → Plan → Track → Archive

### Phase 0: Progress Dashboard 📊
**Default Mode - Comprehensive Status Overview:**
```yaml
Data Collection (Parallel):
  - Git metrics: commits, velocity, contributors
  - Task status: MEMORY.md parsing
  - Quality metrics: test/lint status
  - Architecture health: dependency analysis
  - Milestone progress: completion tracking

Visual Presentation:
  🎯 Project: [Name] • Phase: [Current Milestone]
  
  📈 Progress Overview:
  Overall: [████████░░] 80% • Velocity: ↑15% this week
  
  📊 Current Milestone: [Name]
  Tasks:    [███████░░░] 7/10 complete
  Quality:  [██████████] All checks passing ✅
  Docs:     [████████░░] 80% updated
  
  ⚡ Velocity Metrics:
  • This Week: 12 commits, 4 tasks completed
  • Average: 2.3 tasks/week, 87% on-time delivery
  • Trend: 📈 Accelerating
  
  🏗️ Architecture Health:
  • Technical Debt: Low (score: 82/100)
  • Test Coverage: 87% (↑3% this week)
  • Dependencies: All up to date ✅
  
  💡 Insights:
  • Strong momentum on authentication module
  • Consider addressing TODO backlog (12 items)
  • Ready for milestone completion review
  
  🎯 Recommended Next Action:
  → Complete remaining 3 tasks
  → Run: /plan --complete when ready
```

### Phase 1: Status Assessment 🔍
**Current Milestone Analysis:**
```yaml
Discovery:
  - Read: .quaestor/MEMORY.md → current milestone section
  - Parse: planned|in_progress|completed items
  - Check: .quaestor/milestones/*/tasks.yaml files
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
## 🎉 Milestone Complete: [Name] - [Date]

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
[Identified next logical milestone based on current progress]
```

### Phase 4: Next Phase Planning 🚀
**Intelligent Next Milestone Suggestion:**
```yaml
Planning Intelligence:
  - Analyze: current architecture + remaining TODOs
  - Identify: logical next development phase
  - Suggest: milestone scope + success criteria
  - Estimate: duration based on current velocity
```

## Milestone Creation Workflow

### Guided Creation Process
```yaml
Context Gathering:
  1. Goal: "What's the main objective?"
  2. Scope: "What are the key deliverables?"
  3. Criteria: "How will we measure success?"
  4. Duration: "Estimated timeframe?"

Template Generation:
  - Create: structured milestone section in MEMORY.md
  - Initialize: task tracking + progress indicators
  - Set: measurable success criteria
  - Link: to existing architecture + patterns
```

### Creation Output Template
```yaml
New Milestone Structure:
  - Header: "🚀 Milestone: [Name]"
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

### Velocity Tracking Mode (--velocity)
**Performance Metrics and Trends:**
```yaml
Metrics Collection:
  - Commit frequency and size
  - Task completion rates
  - Milestone duration trends
  - Quality gate success rates

Visualization:
  📈 Velocity Dashboard
  
  📊 This Week vs Average:
  Commits:     ████████ 12 (avg: 8)  ↑50%
  Tasks:       ██████ 4 (avg: 3)      ↑33%
  Code Churn:  ███ +847/-213 lines
  
  📉 Historical Trends (4 weeks):
  Week 1: ████ 4 tasks
  Week 2: ██████ 6 tasks
  Week 3: ███ 3 tasks
  Week 4: ████████ 8 tasks
  
  ⏱️ Milestone Velocity:
  • Current pace: 2.3 tasks/week
  • Estimated completion: ~2 weeks
  • Confidence level: High (87%)
  
  🎯 Efficiency Insights:
  • Peak productivity: Tue-Thu
  • Blockers: PR review delays
  • Recommendation: Batch similar tasks
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

**Milestone Completion:**
- ✅ All planned tasks demonstrably complete
- ✅ Quality gates passed (tests, linting, types)
- ✅ Documentation updated and current
- ✅ Success criteria measurably achieved
- ✅ Archive generated with evidence + insights

**Milestone Creation:**
- ✅ Clear, measurable objectives defined
- ✅ Concrete deliverables identified
- ✅ Success criteria established
- ✅ Progress tracking initialized
- ✅ Integration with existing project patterns

## Integration Points

**Quaestor Ecosystem:**
- **MEMORY.md** → Primary milestone tracking
- **ARCHITECTURE.md** → Update with architectural decisions
- **milestones/** → Detailed task tracking (if exists)
- **Git tags** → Optional milestone tagging
- **Quality system** → Integrated validation before completion

---
*Intelligent milestone management with evidence-based completion and automated progress tracking*