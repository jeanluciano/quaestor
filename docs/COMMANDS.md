# Quaestor Commands Overview

*Command system with Claude integration and orchestration*

## Command Architecture

### Intelligence Features
All Quaestor commands include these patterns:
- **Auto-activation**: Context-aware triggers and intelligent thresholds
- **Performance profiling**: Standard, optimization, and complex execution modes
- **Quality gates**: Integrated validation cycles with zero-tolerance fixing
- **Milestone integration**: Automatic progress tracking and completion detection
- **Token efficiency**: Symbol system for 30-50% token reduction

### YAML Frontmatter Standard
```yaml
---
allowed-tools: [tool1, tool2, ...]
description: "Brief command description with intelligence focus"
performance-profile: "standard|optimization|complex"
complexity-threshold: 0.2-0.8  # Based on command sophistication
auto-activation: ["feature1", "feature2", ...]
intelligence-features: ["capability1", "capability2", ...]
---
```

## Available Commands

### 🔧 Core Development Commands

#### `/task` - Intelligent Implementation
**Purpose**: Execute production-quality features with auto-detected language standards and intelligent orchestration.

**Intelligence**: Auto-persona activation, parallel execution, milestone integration
**Profile**: Complex (0.7 threshold)
**Key Features**:
- Project detection → Python|Rust|JS|Generic standards
- Complexity assessment → Single|Multi-file|System-wide strategy
- Quality cycle every 3 edits with language-specific validation

```bash
/task "implement user authentication system"
/task [description] --strategy systematic|agile|focused
```

#### `/check` - Zero-Tolerance Quality Validation  
**Purpose**: Verify code quality, run tests, fix ALL issues with intelligent error fixing.

**Intelligence**: Parallel-fixing, error-categorization, quality-gates
**Profile**: Optimization (0.4 threshold)
**Key Features**:
- Auto-detect project type → apply language standards
- Parallel agent strategy for complex issue resolution
- Mandatory: ALL linters pass, ALL tests pass, ALL types clean

```bash
/check
/check --parallel --fix-all
```

### 📊 Analysis & Planning Commands

#### `/analyze` - Multi-Dimensional Code Analysis
**Purpose**: Execute comprehensive analysis across quality, security, performance, and architecture domains.

**Intelligence**: Systematic-analysis, evidence-gathering, tool-orchestration
**Profile**: Complex (0.8 threshold)
**Key Features**:
- Domain detection & tool selection (quality|security|performance|architecture)
- Parallel agent specialization for large codebases
- Priority scoring matrix with evidence-based insights

```bash
/analyze [target] --focus quality|security|performance|architecture
/analyze --depth quick|deep|comprehensive
```

#### `/status` - Intelligent Progress Overview
**Purpose**: Analyze project progress with visual indicators, velocity tracking, and actionable insights.

**Intelligence**: Progress-visualization, insight-generation, next-action-detection
**Profile**: Standard (0.2 threshold)
**Key Features**:
- Multi-source analysis (MEMORY.md, git history, quality metrics)
- Visual progress bars with velocity trends
- Bottleneck detection with specific action suggestions

```bash
/status
/status --verbose --milestone current
```

### 🎯 Milestone Management Commands

#### `/milestone` - Intelligent Milestone Management
**Purpose**: Create or complete milestones with evidence-based validation and automated progress tracking.

**Intelligence**: Completion-detection, evidence-validation, progress-tracking
**Profile**: Standard (0.3 threshold)
**Key Features**:
- Readiness assessment with quality gates
- Smart archiving with auto-categorization
- Next phase planning based on velocity analysis

```bash
/milestone --create "MVP Complete"
/milestone --complete
```

#### `/milestone-pr` - Automated PR Creation
**Purpose**: Create comprehensive PRs for completed milestones with auto-detection and validation.

**Intelligence**: Milestone-validation, commit-analysis, pr-generation
**Profile**: Standard (0.4 threshold)
**Key Features**:
- Completion detection with conflict checking
- Commit discovery and categorization
- Intelligent PR generation with reviewer detection

```bash
/milestone-pr
/milestone-pr --milestone "phase-1-auth" --draft
```

### 🚀 Automation Commands

#### `/commit` - Intelligent Commit Generation
**Purpose**: Automatically create conventional commits when TODOs are completed.

**Intelligence**: Todo-completion-detection, commit-generation, milestone-tracking
**Profile**: Optimization (0.3 threshold)
**Key Features**:
- Conventional commit spec with intelligent type/scope detection
- Smart file staging with quality gates
- Hook integration for automatic TODO completion triggers

```bash
/commit
/commit --dry-run --todo-id 42
```

#### `/project-init` - Framework-Aware Project Setup
**Purpose**: Analyze project architecture, detect frameworks, and generate intelligent Quaestor setup.

**Intelligence**: Framework-detection, pattern-analysis, adaptive-setup
**Profile**: Complex (0.6 threshold)
**Key Features**:
- Stack analysis (React|Django|Express|FastAPI|Axum)
- Architecture pattern detection (MVC|DDD|VSA|Microservices)
- Adaptive milestone generation based on project maturity

```bash
/project-init
/project-init --type web-api --existing
```

## Intelligence Patterns

### Performance Profiles
- **Standard (0.2-0.4)**: Simple tasks, direct execution, basic validation
- **Optimization (0.4-0.6)**: Quality-focused, fast validation, parallel fixing
- **Complex (0.6-0.8)**: Multi-agent coordination, systematic approach, evidence-based

### Auto-Activation Triggers
- **Context detection**: Project type, framework, architecture patterns
- **Quality gates**: Test status, linting compliance, build health
- **Milestone integration**: Progress tracking, completion detection
- **Orchestration**: Tool selection, agent spawning, parallel execution

### Validation Cycles
```
Execute → Validate → Fix (if ❌) → Re-validate → ✅ Complete
```

## Symbol System

### Core Flow
- `→` leads to, implies
- `⇒` transforms to  
- `✅` completed, passed
- `❌` failed, error
- `⚠️` warning
- `⚡` performance, optimization
- `🔍` analysis, investigation
- `📊` metrics, data
- `🎯` target, goal

### Workflow Patterns
```
🔍 Analysis → 📋 Planning → ⚡ Implementation → ✅ Validation
```

## Integration Points

### Quaestor Ecosystem
- **MEMORY.md**: Milestone tracking and progress updates
- **ARCHITECTURE.md**: System design and pattern documentation  
- **Quality system**: Integrated validation before operations
- **Git workflow**: Conventional commits and PR automation

### Command Features
- **Token efficiency**: Reduction through symbol system
- **Orchestration**: Context-aware tool selection
- **Auto-activation**: Reduced manual intervention
- **Quality gates**: Error fixing and validation

---
*Command system with orchestration and automatic quality gates*