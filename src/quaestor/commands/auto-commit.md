---
allowed-tools: [Read, Bash, Grep, Edit, TodoWrite]
description: "Intelligent commit generation with conventional commit spec and milestone integration"
performance-profile: "optimization"
complexity-threshold: 0.3
auto-activation: ["todo-completion-detection", "commit-generation", "milestone-tracking"]
intelligence-features: ["conventional-commits", "scope-detection", "quality-gates"]
---

# /auto-commit - Intelligent Commit Generation

## Purpose
Automatically create conventional commits when TODOs are completed, with intelligent scope detection, quality gates, and milestone integration.

## Usage
```
/auto-commit
/auto-commit --dry-run
/auto-commit --todo-id 42
```

## Auto-Intelligence

### Commit Generation
```yaml
Conventional Commits:
  - Type: Auto-detect feat|fix|docs|refactor|test|perf|chore
  - Scope: Extract from milestone|directory|module patterns
  - Description: Transform TODO → imperative mood
  - Body: Generate from file changes + context
```

### Quality Integration
- **Pre-commit checks**: Syntax, linting, tests
- **Smart staging**: Only related files
- **Milestone tracking**: Auto-update progress

## Execution: Detect → Analyze → Generate → Commit

### Phase 1: Completion Detection 🔍
**TODO Status Monitoring:**
```yaml
Trigger Source:
  - TodoWrite: Status change to 'completed'
  - Context: Link to milestone tasks
  - Files: Modified since TODO in_progress
  - Scope: Directory/module analysis
```

### Phase 2: Intelligent Analysis ⚡
**Conventional Commit Spec:**
```yaml
Type Detection:
  - implement|add|create → feat
  - fix|resolve|repair → fix
  - update docs|document → docs
  - refactor|restructure → refactor
  - test|testing → test
  - optimize|performance → perf
  
Scope Extraction:
  - Milestone: "Phase 1: Auth" → auth
  - Directory: "src/components/" → components
  - Module: "quaestor.hooks" → hooks
  - Explicit: "[scope:api]" → api
```

### Phase 3: Message Generation 📝
**Template Structure:**
```
type(scope): description

- Change summary bullet points
- Key implementation details

Part of: [Milestone Name]
Completes: TODO #[id]
```

**Example Output:**
```
feat(auth): implement OAuth2 login flow

- Added OAuth2 provider configuration
- Implemented callback handling
- Added token refresh logic

Part of: Phase 1 - User Authentication
Completes: TODO #42
```

### Phase 4: Quality Gates ✅
**Pre-Commit Validation:**
```yaml
Mandatory Checks:
  - Syntax: python -m py_compile, tsc --noEmit
  - Linting: ruff check, eslint, cargo clippy
  - Tests: Run affected modules only (fast mode)
  
Auto-Fix:
  - Formatting: ruff format, prettier --write
  - Import sorting: isort, organize imports
  
Failure Response:
  - Abort commit → show errors
  - Suggest: Run /check to fix issues
```

## Smart File Staging

**Auto-Detection Rules:**
```yaml
Include:
  - Direct changes: git diff --name-only
  - Test files: test_*.py, *.test.js, *.spec.ts
  - Related docs: README.md, *.md in same dir
  - Config: package.json, requirements.txt (if deps added)
  
Exclude:
  - Temp files: *.log, *.tmp, __pycache__
  - Secrets: .env*, *.secret
  - Generated: *.generated.*, lock files
  
Validation:
  - Only stage TODO-related files
  - Prevent mixing unrelated changes
```

## Milestone Integration

**Auto-Tracking Updates:**
```yaml
On Commit:
  - Find milestone: Match TODO in tasks.yaml
  - Update task: Add completed_at + commit_sha
  - Recalculate progress: completed/total * 100
  - Check completion: Notify if milestone done
  
Memory Updates:
  - Format: "✅ task_description (commit_sha)"
  - Location: Current Milestone section
  - Trigger: Suggest /milestone-pr if complete
```

## Hook Configuration

**Automatic Triggers:**
```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "TodoWrite",
      "hooks": [{
        "type": "command",
        "command": "quaestor auto-commit --check"
      }]
    }]
  }
}
```

**Logic Flow:**
- Parse TodoWrite output → Find 'completed' status
- Trigger auto-commit for each completion
- Update milestone progress automatically

## Success Criteria

**Commit Creation:**
- ✅ Conventional commit format generated
- ✅ Only related files staged
- ✅ Quality gates passed
- ✅ Milestone tracking updated

**Integration:**
- ✅ TODO completion detection working
- ✅ Automatic hook triggers functional
- ✅ Progress calculation accurate
- ✅ Clean git history maintained

---
*Intelligent commit generation with conventional spec and milestone integration*