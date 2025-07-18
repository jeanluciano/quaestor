---
allowed-tools: [Read, Edit, MultiEdit, Write, Bash, Grep]
description: "Intelligent milestone management with completion detection"
performance-profile: "standard"
complexity-threshold: 0.3
auto-activation: ["completion-detection", "evidence-validation", "progress-tracking"]
intelligence-features: ["readiness-assessment", "auto-archiving", "next-phase-planning"]
---

# /milestone - Intelligent Milestone Management

## Purpose
Create new milestones or intelligently complete current milestones with evidence-based validation and automated progress tracking.

## Usage
```
/milestone --create "MVP Complete"
/milestone --complete
/milestone --status
/milestone [interactive mode]
```

## Auto-Intelligence

### Completion Detection
```yaml
Readiness Assessment:
  - Tasks: scan for incomplete items
  - Quality: verify tests + linting status
  - Documentation: check for pending updates
  - Evidence: validate measurable criteria
```

### Smart Archiving
- **Auto-categorize**: achievements, decisions, patterns, metrics
- **Cross-reference**: link related commits, PRs, issues
- **Extract insights**: document lessons learned + patterns established

## Execution: Assess → Validate → Archive → Plan

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

## Interactive Mode Features

**Intelligent Status Overview:**
```yaml
When No Flags Provided:
  1. Display: current milestone progress visualization
  2. Analyze: completion readiness
  3. Recommend: complete|continue|create action
  4. Guide: through selected workflow
```

**Progress Visualization:**
```
📊 Current Milestone: [Name]
Progress: [████████░░] 80%

✅ Completed (X): [List recent completions]
🔄 In Progress (Y): [List active tasks]  
📋 Planned (Z): [List remaining tasks]

🎯 Readiness Check:
✅ Tasks: 8/10 complete
⚠️ Tests: 2 failing (run /check)
✅ Documentation: Current
❌ Success Criteria: 2/3 met

💡 Recommendation: Fix failing tests before completion
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