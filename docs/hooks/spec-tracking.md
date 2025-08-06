# Specification Progress Tracking

Quaestor automatically tracks specification progress through TODO completion. This streamlined approach eliminates manual status updates while providing real-time visibility into implementation progress.

## Overview

The TODO-based specification tracking system:
- **Automatic Progress Updates**: Specification progress updates when you complete related TODOs
- **Zero Manual Intervention**: No need to manually edit YAML files or update status
- **Natural Workflow Integration**: Works with your existing TODO workflow
- **Real-time Feedback**: See specification progress in your session context

## How It Works

### 1. TODO Monitoring
The `todo_spec_progress` hook monitors all TodoWrite operations:

```python
# When you update TODOs in your workflow
todos = [
    {"id": "1", "content": "Implement user authentication", "status": "completed"},
    {"id": "2", "content": "Add password hashing", "status": "completed"},
    {"id": "3", "content": "Create login endpoint", "status": "pending"}
]
```

### 2. Automatic Criterion Matching
The system intelligently matches completed TODOs to specification criteria:

- Analyzes TODO content for keywords
- Matches against acceptance criteria in active specifications
- Updates criteria when sufficient TODOs are completed

### 3. Progress Calculation
Progress is automatically calculated based on completed criteria:

```yaml
# Before TODO completion
acceptance_criteria:
  - [ ] Implement secure user authentication
  - [ ] Add password hashing with bcrypt
  - [ ] Create RESTful login endpoint

progress: 0.0

# After related TODOs are completed
acceptance_criteria:
  - ✓ Implement secure user authentication
  - ✓ Add password hashing with bcrypt
  - [ ] Create RESTful login endpoint

progress: 0.67
```

## Configuration

The TODO specification tracking is enabled by default in your `.claude/settings.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "TodoWrite",
        "hooks": [
          {
            "type": "command",
            "command": "python /path/to/hooks/todo_spec_progress.py",
            "description": "Update specification progress when TODOs are completed"
          }
        ]
      }
    ]
  }
}
```

## Usage Examples

### Example 1: Feature Implementation

1. Create a specification:
```bash
/plan "Add user profile management"
```

2. Work on implementation with TODOs:
```
- [ ] Create user profile model
- [ ] Add profile update endpoint
- [ ] Implement profile picture upload
- [ ] Add profile validation
```

3. As you complete TODOs, the specification automatically updates:
```yaml
# Specification updates automatically
acceptance_criteria:
  - ✓ User profile data model with required fields
  - ✓ Profile update functionality with validation
  - [ ] Profile picture upload with size limits
  
progress: 0.67
updated_at: 2024-01-15T10:30:00
implementation_notes: |
  - 2024-01-15: Updated progress via TODO completion
```

### Example 2: Bug Fix Tracking

1. Create a bug fix specification:
```bash
/plan "Fix authentication timeout issues"
```

2. Track fix progress with TODOs:
```
- [x] Investigate timeout root cause
- [x] Implement session refresh logic
- [ ] Add timeout configuration
- [ ] Update documentation
```

3. Specification updates automatically as work progresses

## Benefits

### 1. Natural Workflow
- No context switching to update specifications
- Progress tracking happens as you work
- Maintains focus on implementation

### 2. Accurate Progress
- Real-time progress based on actual work completed
- No forgotten manual updates
- Clear visibility into what's done and what remains

### 3. Automatic Documentation
- Implementation notes added automatically
- Progress history preserved
- Clear audit trail of changes

## Integration with Session Context

The session context loader automatically displays specification progress:

```markdown
## 📋 Active Specifications (1)

### 📋 Specification 1: User Authentication System
**ID**: spec-auth-001
**Progress**: [████████░░░░░░░░░░░░] 40%
├─ Criteria: 2/5 completed
├─ Status: ACTIVE
├─ Priority: HIGH
└─ Branch: feature/auth

💡 **Progress tracks automatically**: Complete TODOs to update acceptance criteria

**Acceptance Criteria:**
  1. [x] ~~Implement user registration~~
  2. [x] ~~Add password hashing~~
  3. [ ] Create login endpoint
  4. [ ] Add session management
  5. [ ] Implement logout functionality

**🎯 Next Steps:**
  → Create login endpoint
  → Add session management
  → Implement logout functionality
```

## Advanced Features

### Keyword Extraction
The system intelligently extracts keywords from criteria:

```python
# From criterion: "Implement secure user authentication with JWT"
# Extracted keywords: ["implement", "secure", "user", "authentication", "jwt"]

# TODOs that would match:
- "Implement JWT authentication"  # High match
- "Add secure auth system"       # Medium match
- "User login security"          # Lower match
```

### Coverage Threshold
A criterion is marked complete when >70% of its keywords are covered by completed TODOs:

```python
# Criterion: "Create RESTful API endpoints for user management"
# Keywords: ["create", "restful", "endpoints", "user", "management"]

# Completed TODOs:
- "Create user API endpoints" (covers: create, user, endpoints)
- "Add RESTful routes" (covers: restful)
# Coverage: 4/5 = 80% ✓ Marked as complete
```

## Best Practices

### 1. Descriptive TODO Content
Write TODOs that clearly describe what you're implementing:

```
# Good - specific and matches criteria
- [ ] Implement bcrypt password hashing for user registration

# Less effective - too vague
- [ ] Add security stuff
```

### 2. Reference Specifications
Include specification IDs in TODOs for direct matching:

```
- [ ] [spec-auth-001] Add two-factor authentication
- [ ] Complete login endpoint for spec-auth-001
```

### 3. Break Down Complex Tasks
Split large criteria into specific TODOs:

```yaml
# Criterion: "Implement complete authentication system"

# Break down into TODOs:
- [ ] Create user registration endpoint
- [ ] Add email verification
- [ ] Implement password reset flow
- [ ] Add remember me functionality
```

## Troubleshooting

### Progress Not Updating
1. Ensure TODOs are marked as "completed" status
2. Check that TODO content relates to specification criteria
3. Verify the specification is in "ACTIVE" status

### Manual Override
If needed, you can still manually edit specification YAML files:

```bash
# Edit specification directly
edit .quaestor/specs/active/spec-auth-001.yaml
```

## Next Steps

- Learn about [Session Context Loading](session-context-loader.md)
- Explore [Specification Workflow](../specs/workflow.md)
- Understand [Agent Integration](../agents/overview.md)