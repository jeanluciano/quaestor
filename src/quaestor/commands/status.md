---
allowed-tools: [Read, LS, Grep]
description: Show current project status and progress
---

# STATUS - Project Progress Overview
<!-- META:command:status -->
<!-- META:version:1.0 -->

## 📊 Project Status Report

I'll analyze your project's current state and progress.

### 1. Check Quaestor Documentation
First, let me read your project's current status from the Quaestor files:

```yaml
files_to_check:
  - path: ".quaestor/MEMORY.md"
    purpose: "Current progress and milestones"
  - path: ".quaestor/ARCHITECTURE.md"
    purpose: "Project structure and design"
  - path: ".quaestor/manifest.json"
    purpose: "File tracking and versions"
```

### 2. Analyze Current State

<!-- DATA:status-analysis:START -->
```yaml
progress_indicators:
  milestones:
    - check: "current_milestone"
      source: "MEMORY.md → Current Milestone section"
    - check: "completed_items"
      source: "MEMORY.md → Completed section"
    - check: "in_progress_items"
      source: "MEMORY.md → In Progress section"
    - check: "upcoming_items"
      source: "MEMORY.md → Planned section"
  
  code_quality:
    - check: "test_status"
      command: "Check if tests exist and recent results"
    - check: "linting_status"
      command: "Look for recent linting results"
    - check: "type_checking"
      command: "Check for type checking configuration"
  
  project_health:
    - check: "recent_commits"
      source: "git log if available"
    - check: "documentation_status"
      source: "README.md and docs/"
    - check: "dependencies_status"
      source: "package files"
```
<!-- DATA:status-analysis:END -->

### 3. Generate Status Report

After analyzing, I'll provide a formatted status report:

```
📊 Project Status: [Project Name]

Current Phase: [Milestone Name]
Progress: [##########----] 75%

✅ Recently Completed ([count]):
  • [Completed item 1]
  • [Completed item 2]
  • ...

🚧 In Progress ([count]):
  • [Current task 1] - [status]
  • [Current task 2] - [status]
  • ...

📋 Upcoming ([count]):
  • [Planned item 1]
  • [Planned item 2]
  • ...

Code Quality:
  Tests: [✅ Passing | ⚠️ Issues | ❌ Failing]
  Linting: [✅ Clean | ⚠️ Warnings | ❌ Errors]
  Type Check: [✅ Clean | ⚠️ Issues | ❌ Errors]

Last Activity: [time since last commit/update]
Documentation: [✅ Current | ⚠️ Needs Update | ❌ Missing]

💡 Recommendations:
  • [Suggestion based on current state]
  • [Next logical step]
```

### 4. Verbose Mode (if requested)

If you add `--verbose` to the command, I'll also show:
- Detailed progress on each task
- Full list of completed items
- Technical debt tracking
- Performance metrics
- Test coverage details

### 5. Quick Actions

Based on the status, I'll suggest quick actions:
- If tests failing: "Run `/check` to see details"
- If tasks stalled: "Use `/task` to continue implementation"
- If milestone complete: "Use `/milestone-commit` to finalize"

---

**Usage:**
- `/status` - Show concise project status
- `/status --verbose` - Show detailed status with all items
- `/status --json` - Output in JSON format (coming soon)