---
allowed-tools: all
description: Create a pull request for a completed milestone with all atomic commits
---

# MILESTONE PR - Create Pull Request for Completed Milestones
<!-- META:command:milestone:pr -->
<!-- META:version:1.0 -->
<!-- META:ai-optimized:true -->

## 🎯 PURPOSE: One PR Per Milestone

**Create comprehensive pull requests when milestones are complete, containing all atomic commits.**

<!-- SECTION:milestone-pr:overview:START -->
## Overview

<!-- DATA:workflow-summary:START -->
```yaml
workflow:
  trigger: "All tasks in milestone completed"
  prerequisites:
    - all_tasks_done: "100% completion"
    - commits_created: "Via auto-commit"
    - quality_passing: "All checks green"
    - on_feature_branch: "Not main/master"
  
  actions:
    - validate_milestone: "Ensure ready for PR"
    - gather_commits: "Collect all related commits"
    - generate_description: "Create comprehensive PR body"
    - create_pr: "Using GitHub CLI"
    - update_tracking: "Mark milestone as PR created"
  
  benefits:
    - "Logical PR boundaries"
    - "Complete feature delivery"
    - "Traceable progress"
    - "Clean review process"
```
<!-- DATA:workflow-summary:END -->
<!-- SECTION:milestone-pr:overview:END -->

<!-- SECTION:milestone-pr:validation:START -->
## Pre-PR Validation

<!-- DATA:validation-checks:START -->
```yaml
validation:
  1_milestone_completion:
    check: "All tasks in milestone completed"
    source: ".quaestor/milestones/{{ milestone }}/tasks.yaml"
    require: "100% completion"
    
  2_commits_exist:
    check: "Commits created for completed tasks"
    validate: "Each task has commit_sha"
    minimum: 1
    
  3_branch_status:
    check: "On feature branch"
    command: "git branch --show-current"
    not_allowed: ["main", "master", "develop"]
    
  4_quality_status:
    check: "All quality checks passing"
    run: "/quaestor:check"
    require: "All green"
    
  5_conflicts_check:
    check: "No merge conflicts with base"
    command: "git merge-tree $(git merge-base HEAD main) HEAD main"
    abort_if: "Conflicts detected"
    
  6_pr_uniqueness:
    check: "No existing PR for this milestone"
    command: "gh pr list --search 'milestone:{{ milestone_name }}'"
    abort_if: "PR already exists"
```
<!-- DATA:validation-checks:END -->
<!-- SECTION:milestone-pr:validation:END -->

<!-- SECTION:milestone-pr:commit-gathering:START -->
## Commit Collection

<!-- DATA:commit-collection:START -->
```yaml
commit_gathering:
  strategies:
    1_from_milestone_tasks:
      read: ".quaestor/milestones/{{ milestone }}/tasks.yaml"
      extract: "commit_sha from each completed task"
      validate: "Commits exist in git log"
      
    2_from_commit_messages:
      search: "git log --grep='Part of: {{ milestone }}'"
      fallback: "If tasks.yaml missing commit info"
      
    3_from_time_range:
      start: "Milestone start date"
      end: "Current date"
      filter: "Commits by current author"
      validate: "Related to milestone work"
  
  commit_ordering:
    strategy: "chronological"
    oldest_first: true
    
  commit_details:
    for_each_commit:
      - sha: "Full commit hash"
      - short_sha: "7-character hash"
      - message: "Full commit message"
      - files_changed: "List of modified files"
      - insertions: "Lines added"
      - deletions: "Lines removed"
      - author: "Commit author"
      - date: "Commit timestamp"
```
<!-- DATA:commit-collection:END -->
<!-- SECTION:milestone-pr:commit-gathering:END -->

<!-- SECTION:milestone-pr:pr-generation:START -->
## Pull Request Generation

<!-- DATA:pr-structure:START -->
```yaml
pr_structure:
  title_generation:
    format: "{{ milestone_name }}: {{ summary }}"
    
    summary_extraction:
      from_milestone_readme: "First line of README.md"
      from_completed_tasks: "Common theme analysis"
      max_length: 50
      
    examples:
      - "Phase 1 Authentication: Add OAuth2 and session management"
      - "Performance Optimization: Reduce API response time by 50%"
      - "Documentation Update: Add API reference and tutorials"
  
  body_template: |
    ## 🎯 {{ milestone_name }}
    
    {{ milestone_description }}
    
    ### ✅ Completed Tasks ({{ task_count }})
    
    {% for task in completed_tasks %}
    - [x] {{ task.description }} ({{ task.commit_link }})
    {% endfor %}
    
    ### 📊 Summary
    
    - **Commits**: {{ commit_count }}
    - **Files Changed**: {{ total_files_changed }}
    - **Lines Added**: +{{ total_insertions }}
    - **Lines Removed**: -{{ total_deletions }}
    - **Duration**: {{ milestone_duration }} days
    
    ### 🔄 Changes by Type
    
    {% for type, commits in commits_by_type %}
    #### {{ type|capitalize }} ({{ commits|length }})
    {% for commit in commits %}
    - {{ commit.message }} ({{ commit.short_sha }})
    {% endfor %}
    {% endfor %}
    
    ### 📝 Detailed Changes
    
    <details>
    <summary>Click to expand commit details</summary>
    
    {% for commit in all_commits %}
    #### {{ commit.short_sha }} - {{ commit.message }}
    - **Files**: {{ commit.files_changed|join(', ') }}
    - **Changes**: +{{ commit.insertions }} -{{ commit.deletions }}
    
    {% endfor %}
    </details>
    
    ### ✅ Quality Checks
    
    - [x] All tests passing
    - [x] Linting clean
    - [x] Type checking passed
    - [x] Documentation updated
    
    ### 🚀 Next Steps
    
    {% if next_milestone %}
    After merging, the next milestone is: **{{ next_milestone }}**
    {% else %}
    This completes the current phase of work.
    {% endif %}
    
    ---
    
    cc: @{{ reviewers|join(' @') }}
    
    Milestone tracked in: `.quaestor/milestones/{{ milestone_id }}/`
```
<!-- DATA:pr-structure:END -->

<!-- DATA:pr-metadata:START -->
```yaml
pr_metadata:
  labels:
    automatic:
      - "milestone-{{ milestone_id }}"
      - "{{ milestone_type }}"  # feature, bugfix, etc.
    
    from_commits:
      feat: "enhancement"
      fix: "bug"
      docs: "documentation"
      perf: "performance"
      refactor: "refactoring"
      test: "testing"
    
    size_based:
      small: "< 100 lines"
      medium: "100-500 lines"
      large: "> 500 lines"
  
  assignees:
    - "@me"  # Current user
    
  reviewers:
    detection:
      - "CODEOWNERS file"
      - "Recent collaborators"
      - "Milestone participants"
    
  projects:
    link_to: "GitHub project board"
    column: "In Review"
```
<!-- DATA:pr-metadata:END -->
<!-- SECTION:milestone-pr:pr-generation:END -->

<!-- SECTION:milestone-pr:branch-management:START -->
## Branch Management

<!-- DATA:branch-strategy:START -->
```yaml
branch_management:
  naming:
    format: "{{ type }}/{{ milestone_id }}"
    examples:
      - "feature/phase-1-auth"
      - "fix/payment-processing"
      - "docs/api-reference"
    
    type_mapping:
      feature_milestone: "feature"
      bugfix_milestone: "fix"
      docs_milestone: "docs"
      refactor_milestone: "refactor"
  
  push_strategy:
    ensure_pushed: "All commits on remote"
    command: "git push -u origin {{ branch_name }}"
    
  base_branch:
    default: "main"
    from_config: ".github/CONTRIBUTING.md"
    detection:
      - "git config --get init.defaultBranch"
      - "Most active branch"
```
<!-- DATA:branch-strategy:END -->
<!-- SECTION:milestone-pr:branch-management:END -->

<!-- SECTION:milestone-pr:gh-integration:START -->
## GitHub CLI Integration

<!-- DATA:gh-commands:START -->
```yaml
github_cli:
  pr_creation:
    command: |
      gh pr create \
        --title "{{ title }}" \
        --body "{{ body }}" \
        --base "{{ base_branch }}" \
        --head "{{ feature_branch }}" \
        {% for label in labels %}
        --label "{{ label }}" \
        {% endfor %}
        {% for reviewer in reviewers %}
        --reviewer "{{ reviewer }}" \
        {% endfor %}
        --assignee "@me"
    
    options:
      --draft: "If milestone has warnings"
      --no-maintainer-edit: false
      --web: "Open in browser after creation"
  
  pr_enhancements:
    link_issues:
      command: "gh pr edit {{ pr_number }} --add-link {{ issue }}"
      
    add_to_project:
      command: "gh pr edit {{ pr_number }} --add-project {{ project }}"
      
    enable_auto_merge:
      command: "gh pr merge {{ pr_number }} --auto --squash"
      condition: "If all checks pass"
```
<!-- DATA:gh-commands:END -->
<!-- SECTION:milestone-pr:gh-integration:END -->

<!-- SECTION:milestone-pr:post-pr:START -->
## Post-PR Actions

<!-- DATA:post-creation:START -->
```yaml
post_pr_actions:
  1_update_milestone:
    file: ".quaestor/milestones/{{ milestone }}/tasks.yaml"
    add:
      pr_number: "{{ pr_number }}"
      pr_url: "{{ pr_url }}"
      pr_created_at: "{{ timestamp }}"
      status: "in_review"
  
  2_update_memory:
    add_entry: |
      ## Milestone PR Created: {{ milestone_name }}
      - PR #{{ pr_number }}: {{ pr_url }}
      - Commits: {{ commit_count }}
      - Ready for review
  
  3_notifications:
    slack: "New PR ready for review: {{ pr_url }}"
    email: "If configured"
    
  4_next_milestone:
    check: "Find next incomplete milestone"
    suggest: "Start working on {{ next_milestone }}"
    create_branch: "For next milestone work"
```
<!-- DATA:post-creation:END -->
<!-- SECTION:milestone-pr:post-pr:END -->

<!-- SECTION:milestone-pr:usage:START -->
## Usage

<!-- EXAMPLE:basic:START -->
```bash
# Create PR for current milestone
/quaestor:milestone-pr

# Create PR for specific milestone
/quaestor:milestone-pr --milestone "phase-1-auth"

# Create draft PR (for early review)
/quaestor:milestone-pr --draft

# Dry run (see what would be created)
/quaestor:milestone-pr --dry-run
```
<!-- EXAMPLE:basic:END -->

<!-- EXAMPLE:advanced:START -->
```bash
# With custom base branch
/quaestor:milestone-pr --base develop

# With specific reviewers
/quaestor:milestone-pr --reviewers @alice,@bob

# Auto-merge when ready
/quaestor:milestone-pr --auto-merge

# Open in browser after creation
/quaestor:milestone-pr --web
```
<!-- EXAMPLE:advanced:END -->
<!-- SECTION:milestone-pr:usage:END -->

<!-- SECTION:milestone-pr:error-handling:START -->
## Error Handling

<!-- DATA:error-scenarios:START -->
```yaml
error_handling:
  incomplete_milestone:
    error: "Not all tasks completed"
    action: "Show incomplete tasks"
    suggestion: "Complete remaining tasks first"
    
  no_commits:
    error: "No commits found for milestone"
    action: "Check if auto-commit ran"
    suggestion: "Manually commit completed work"
    
  existing_pr:
    error: "PR already exists for milestone"
    action: "Show existing PR"
    suggestion: "Update existing PR or close it"
    
  merge_conflicts:
    error: "Conflicts with base branch"
    action: "List conflicting files"
    suggestion: "Resolve conflicts before PR"
    
  quality_failures:
    error: "Quality checks failing"
    action: "Run /quaestor:check"
    suggestion: "Fix issues before creating PR"
```
<!-- DATA:error-scenarios:END -->
<!-- SECTION:milestone-pr:error-handling:END -->

<!-- SECTION:milestone-pr:best-practices:START -->
## Best Practices

<!-- DATA:pr-practices:START -->
```yaml
best_practices:
  milestone_size:
    ideal: "5-10 completed tasks"
    max_commits: 20
    review_time: "< 1 hour"
    
  pr_description:
    - "Clear summary of changes"
    - "Link to related issues"
    - "Include test results"
    - "Document breaking changes"
    
  review_process:
    - "Self-review first"
    - "Check CI passes"
    - "Respond to feedback promptly"
    - "Squash merge for clean history"
    
  milestone_flow:
    - "Plan → Implement → Commit → PR → Merge"
    - "One milestone = One feature"
    - "Regular, predictable delivery"
```
<!-- DATA:pr-practices:END -->
<!-- SECTION:milestone-pr:best-practices:END -->

**Turn completed milestones into reviewable PRs with one command!**