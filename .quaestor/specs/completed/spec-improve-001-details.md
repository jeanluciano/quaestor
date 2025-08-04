# Specification Details: Hook Reliability & Workflow Automation

## Analysis of Current Issues

### 1. Hook Reliability Problems

**Current Issues:**
- Hooks use basic error handling that may silently fail
- No retry logic for transient failures
- Inconsistent output format (some use stdout, some use JSON)
- Base hook class doesn't enforce proper JSON response format

**Specific Improvements Needed:**
```python
# In base.py - Add proper JSON output methods
def output_json_blocking(self, reason: str):
    """Block action with feedback to Claude."""
    output = {
        "decision": "block",
        "reason": reason
    }
    print(json.dumps(output))
    sys.exit(0)

def output_suggestion(self, message: str, suggest_agent: str = None):
    """Provide suggestion with optional agent recommendation."""
    if suggest_agent:
        message += f"\n\nPlease run: Use the {suggest_agent} agent to handle this task"
    output = {
        "decision": "block",
        "reason": message
    }
    print(json.dumps(output))
    sys.exit(0)
```

### 2. Subagent Selection Issues

**Current Problem:**
Commands define agent strategies in frontmatter but don't actively invoke them:
```yaml
# In /impl command
agent-strategy:
  complexity > 0.7: [architect, implementer]
  security_keywords: [security, qa]
```

**Solution:**
Commands should explicitly use the Task tool to invoke subagents:
```markdown
# In command implementation
Based on the complexity analysis (0.8), I'll use specialized agents:

Use the architect agent to design the system architecture
Use the implementer agent to execute the implementation
```

### 3. Workflow Pattern Enforcement

**New Approach:**
- Move Research → Plan → Implement pattern to CRITICAL_RULES.md
- Remove research_workflow_tracker.py hook entirely
- Let Claude enforce naturally through behavioral rules
- User maintains control when driving

**Benefits:**
- Simpler system (one less hook)
- Claude still follows the pattern
- No annoying blocks when user wants to override
- Clean separation of concerns

**CRITICAL_RULES.md Addition:**
```markdown
## 🔄 WORKFLOW PATTERN

### Research → Plan → Implement

**ALWAYS follow this pattern for non-trivial tasks:**

1. **RESEARCH FIRST**
   - Required Response: "Let me research the codebase first..."
   - Use grep/read to understand existing patterns
   - Check similar implementations
   - Understand dependencies

2. **PLAN BEFORE IMPLEMENTING**  
   - Required Response: "Based on my research, here's my plan..."
   - Present approach for approval
   - Identify files to modify
   - Consider edge cases

3. **IMPLEMENT WITH QUALITY**
   - Follow the approved plan
   - Use appropriate subagents
   - Test as you go
   - Validate changes

**EXCEPTIONS:**
- Trivial changes (typos, simple fixes)
- Explicit user override
- Emergency debugging
```

### 4. Spec Lifecycle Automation

**Current Process:**
- Specs must be manually moved between folders
- /review has --archive-spec flag but it's manual
- No automatic activation when work starts

**Enhancements:**

**A. Automatic Activation (draft → active):**
```markdown
# In /impl command
When starting implementation:
1. Detect relevant specification from task description
2. Check if spec exists in draft/ folder
3. Verify active/ folder has space (max 3 specs)
4. Move spec file from draft/ to active/
5. Update spec status to "active"
6. Link to current git branch if applicable
7. Confirm activation to user

Example flow:
User: /impl "implement user authentication"
Claude: Found matching spec 'spec-auth-001' in draft folder.
        📋 Activating specification: spec-auth-001
        ✅ Moved to active folder (2/3 slots used)
```

**B. Automatic Archiving (active → completed):**
```python
# In spec_tracker.py - Add completion detection
def check_spec_completion(self, spec_id: str) -> bool:
    """Check if all tasks in spec are completed."""
    # Read spec file
    # Check all acceptance criteria
    # Verify quality gates passed
    return all_complete

# In /review command - Auto-detect completed specs
When review completes successfully:
1. Check active specs for completion
2. If spec is complete, automatically archive
3. Update tracking and provide confirmation
```

## Simplification Opportunities

### 1. Remove Low-Value Hooks

**Consider Removing:**
- `compliance_validator.py` - Seems redundant with other validation
- `compliance_pre_edit.py` - Overlaps with spec_tracker
- `file_change_tracker.py` - Functionality covered by spec_tracker
- `research_workflow_tracker.py` - Move to CRITICAL_RULES.md instead

**Keep and Enhance:**
- `base.py` - Foundation for all hooks
- `spec_tracker.py` - Core workflow tracking
- `session_context_loader.py` - Context loading
- `user_prompt_submit.py` - Mode detection

### 2. Simplify Command Structure

**Current Complexity:**
- Commands have many configuration options
- Agent strategies defined but not used
- Complex frontmatter

**Simplification:**
```yaml
# Simplified frontmatter
---
allowed-tools: [Task, Read, Write, Edit, Bash]
description: "Implementation with automatic agent selection"
---

# In command body - explicit agent usage
I'll analyze the task complexity and use appropriate agents:

For this high-complexity feature:
- Use the architect agent to design the solution
- Use the implementer agent to write the code
- Use the qa agent to create tests
```

### 3. Streamline Workflow

**Remove:**
- Multiple validation steps that duplicate effort
- Complex progress tracking that adds little value
- Overly detailed status updates

**Focus on:**
- Clear phase transitions (Research → Plan → Implement)
- Automatic agent selection based on task
- Simple completion tracking

## Specific Implementation Steps

### Phase 1: Hook Reliability Improvements

1. **Update base.py:**
   - Add JSON output helper methods
   - Implement retry decorator usage
   - Add better error handling
   - Ensure consistent output format

2. **Update spec_tracker.py:**
   - Use JSON output for all responses
   - Add completion detection logic
   - Improve error handling
   - Simplify progress tracking

3. **Update CRITICAL_RULES.md:**
   - Add Research → Plan → Implement workflow pattern
   - Make it a behavioral rule, not hook-enforced
   - Allow user overrides for flexibility

### Phase 2: Command Improvements

1. **Update /impl command:**
   ```markdown
   # Add automatic spec activation
   When /impl detects a matching specification:
   1. Check if spec is in draft/ folder
   2. If yes, automatically move to active/ folder
   3. Update spec status to "active"
   4. Confirm: "📋 Activated specification: spec-auth-001"
   
   # Add explicit agent invocation
   Based on task analysis:
   - Complexity: 0.8 (high)
   - Files affected: 5
   - Security considerations: Yes
   
   I'll use specialized agents for this task:
   
   Use the architect agent to design the authentication system
   Use the security agent to review security implications
   Use the implementer agent to write the code
   ```

2. **Enhance /review command:**
   - Auto-detect completed specs
   - Automatically run --archive-spec when appropriate
   - Provide clear completion summary

### Phase 3: Configuration Updates

1. **Update .claude/settings.json:**
   ```json
   {
     "hooks": {
       "PostToolUse": [
         {
           "matcher": "Task",
           "hooks": [{
             "type": "command",
             "command": "python3 .claude/hooks/spec_tracker.py",
             "description": "Ensure agents follow specifications"
           }]
         }
       ]
     }
   }
   ```

2. **Add PreToolUse enforcement:**
   - Block direct implementation without research in framework mode
   - Ensure Task tool usage follows agent strategies

## Expected Outcomes

1. **Reliability:** Hooks fire consistently with proper error handling
2. **Automation:** Specs automatically complete when criteria met
3. **Simplicity:** Reduced complexity - fewer hooks, cleaner workflow
4. **Flexibility:** Workflow pattern in CRITICAL_RULES.md, not hook-enforced
5. **Integration:** Commands reliably use appropriate subagents

## Validation Plan

1. Test each hook individually for reliability
2. Verify framework mode blocks improper actions
3. Confirm commands invoke correct subagents
4. Validate automatic spec completion
5. Ensure backward compatibility

## Risk Mitigation

- Make changes incrementally
- Test thoroughly in development
- Maintain backward compatibility
- Document all changes clearly
- Provide migration guide if needed