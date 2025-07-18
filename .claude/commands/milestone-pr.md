---
allowed-tools: [Read, Bash, Grep, Glob, TodoWrite, Task]
description: "Intelligent PR creation with auto-detection and milestone completion validation"
performance-profile: "standard"
complexity-threshold: 0.4
auto-activation: ["milestone-validation", "commit-analysis", "pr-generation"]
intelligence-features: ["completion-detection", "conflict-checking", "quality-gates"]
---

# /milestone-pr - Intelligent PR Creation

## Purpose
Automatically create comprehensive PRs for completed milestones with intelligent validation, conflict detection, and quality gates.

## Usage
```
/milestone-pr
/milestone-pr --milestone "phase-1-auth"
/milestone-pr --draft --reviewers @alice,@bob
```

## Auto-Intelligence

### Completion Detection
```yaml
Auto-Validation:
  - Milestone: 100% task completion check
  - Commits: Auto-commit integration validation
  - Quality: All gates passing (tests, lint, types)
  - Branch: Feature branch detection
  - Conflicts: Base branch merge preview
```

### PR Generation
- **Title**: Auto-extract from milestone goal
- **Description**: Template with task list + metrics
- **Labels**: Based on commit types and milestone scope
- **Reviewers**: Auto-detect from CODEOWNERS + collaborators

## Execution: Validate → Analyze → Generate → Create

### Phase 1: Readiness Validation ✅
**Intelligent Prerequisites Check:**
```yaml
Validation Gates:
  - ✅ Milestone 100% complete (MEMORY.md scan)
  - ✅ Auto-commits exist for all tasks
  - ✅ Quality gates passed (/check validation)
  - ✅ Feature branch active (not main/master)
  - ✅ No merge conflicts with base
  - ✅ No existing PR for milestone
```

### Phase 2: Commit Analysis 📊
**Auto-Commit Discovery:**
```yaml
Commit Collection:
  - Source: MEMORY.md milestone tracking
  - Extract: commit_sha from completed tasks
  - Fallback: git log --grep="Part of: [milestone]"
  - Analyze: files changed, additions/deletions
  - Categorize: feat|fix|docs|perf|refactor
```

### Phase 3: PR Generation 🚀
**Intelligent PR Assembly:**
```yaml
PR Structure:
  title: "[Milestone]: [Auto-summary from tasks]"
  
  body_template: |
    ## 🎯 {{ milestone_name }}
    
    ### ✅ Completed ({{ task_count }})
    {% for task in tasks %}
    - [x] {{ task.description }} ({{ task.commit_sha[:7] }})
    {% endfor %}
    
    ### 📊 Metrics
    - Commits: {{ commit_count }} • Files: {{ files_changed }}
    - Added: +{{ insertions }} • Removed: -{{ deletions }}
    
    ### 🔄 Changes
    {% for type, commits in commits_by_type %}
    **{{ type|title }}** ({{ commits|length }}): {{ commit_list }}
    {% endfor %}
    
    ### ✅ Quality
    - [x] Tests passing • [x] Linting clean • [x] Types valid
    
    cc: @{{ reviewers|join(' @') }}
```

**Auto-Labels & Metadata:**
- **Labels**: milestone-[id], commit-type tags, size indicator
- **Reviewers**: CODEOWNERS + recent collaborators
- **Projects**: Auto-link to milestone board

### Phase 4: GitHub Integration ⚡
**Automated PR Creation:**
```yaml
GH CLI Command:
  gh pr create \
    --title "{{ title }}" \
    --body "{{ body }}" \
    --label "milestone-{{ id }},{{ type_labels }}" \
    --reviewer "{{ auto_reviewers }}" \
    --assignee "@me"
    
Branch Management:
  - Push: Ensure all commits on remote
  - Base: Auto-detect main/master/develop
  - Naming: feature/[milestone-id] convention
```

## Milestone Integration

**Post-Creation Updates:**
```yaml
Tracking Updates:
  - MEMORY.md: Add PR link + status
  - milestone/: Update with pr_number + pr_url
  - Status: Change to "in_review"
  - Next: Auto-detect next milestone to work on
```

## Error Handling

**Intelligent Recovery:**
```yaml
Common Issues:
  - Incomplete milestone → Show remaining tasks
  - No commits found → Check auto-commit status  
  - Existing PR → Link to existing + suggest update
  - Merge conflicts → List conflicts + resolution steps
  - Quality failures → Run /check + fix issues
```

## Success Criteria

**PR Creation:**
- ✅ Milestone completion validated
- ✅ All commits collected and analyzed
- ✅ PR created with comprehensive description
- ✅ Auto-labels and reviewers assigned
- ✅ Milestone tracking updated

**Integration:**
- ✅ Quality gates passed before creation
- ✅ No merge conflicts detected
- ✅ Auto-commit integration verified
- ✅ Next milestone workflow prepared

---
*Automated PR creation with intelligent milestone validation and quality gates*