# Agent-Rule Interaction Improvements for Quaestor

*A comprehensive plan to transform rules from constraints into intelligent guidance*

## Executive Summary

This document outlines improvements to make Quaestor's rule system more effective for AI coding agents. The core philosophy shifts from "enforcement and restriction" to "guidance and partnership," creating a system where rules adapt to context, explain their purpose, and learn from usage.

## Current Challenges from an Agent's Perspective

As an AI coding agent using Quaestor, I face several challenges that reduce both productivity and rule compliance:

### 1. Context Blindness
Rules apply uniformly regardless of what I'm doing:
- **During exploration**: Strict enforcement slows down code understanding
- **During implementation**: Need all quality gates active
- **During debugging**: Need flexibility to test hypotheses
- **During refactoring**: Different rules apply than new development

### 2. Binary Enforcement
Rules either completely block or fully allow actions:
- Cannot proceed with acknowledged technical debt
- No mechanism for "I know this is suboptimal but necessary"
- Legitimate exceptions (e.g., long database migration functions) are blocked
- Forces workarounds rather than documented exceptions

### 3. Silent Rules
Rules enforce behavior without explaining rationale:
- Don't understand why certain patterns are forbidden
- Cannot make informed decisions about exceptions
- Feel constrained rather than guided
- Miss learning opportunities from violations

### 4. No Feedback Channel
Cannot communicate rule effectiveness:
- No way to report false positives
- Cannot suggest improvements based on experience
- System doesn't learn which rules actually prevent problems
- Repeated encounters with the same unhelpful restrictions

### 5. Static Learning
Each session starts fresh:
- Previous resolutions to rule conflicts are forgotten
- Project-specific patterns must be rediscovered
- No accumulated wisdom from past work
- Same mistakes repeated across sessions

## Proposed Improvements

### 1. Context-Aware Rule System

**Goal**: Rules adapt their strictness based on current development phase

**Implementation**:
```python
# src/quaestor/context/intent_detector.py
class IntentDetector:
    """Detect agent's current intent from behavior patterns"""
    
    PATTERNS = {
        "exploring": {
            "indicators": ["multiple Read ops", "Grep searches", "no writes"],
            "rule_modifier": 0.5,  # Relax non-critical rules
            "preserve": ["security", "data_safety"]  # Never relax these
        },
        "implementing": {
            "indicators": ["Edit after Read", "test creation", "systematic changes"],
            "rule_modifier": 1.0,  # Full rule enforcement
        },
        "debugging": {
            "indicators": ["focused Read/Edit cycles", "error searches", "log analysis"],
            "rule_modifier": 0.7,  # Some flexibility for experimentation
        },
        "refactoring": {
            "indicators": ["multi-file edits", "pattern replacement", "no feature changes"],
            "rule_modifier": 1.2,  # Extra strict - maintaining behavior is critical
        }
    }
```

**Integration with existing MEMORY.md**:
```markdown
### 2024-01-16
- **Context**: Debugging authentication issues
- **Rule Relaxed**: function_length (investigating complex auth flow)
- **Justification**: Need to trace full authentication path in single view
- **Resolution**: Split into 3 functions after understanding issue
```

### 2. Graduated Enforcement Levels

**Goal**: Replace binary block/allow with nuanced responses

**Levels**:
1. **Inform** - Log violation, continue work, track for later review
2. **Warn** - Show warning, highlight consequences, allow continuation  
3. **Justify** - Require explanation before proceeding, record justification
4. **Block** - Hard stop for critical safety/security rules only

**Rule Definition Enhancement**:
```yaml
# In command YAML frontmatter
rules:
  function_length:
    max_lines: 50
    enforcement:
      min: "inform"      # During exploration
      default: "warn"    # Normal development
      max: "justify"     # Can never fully block
    context_modifiers:
      debugging: "inform"
      refactoring: "justify"
    
  no_raw_sql:
    enforcement:
      min: "block"       # Always block - security critical
      default: "block"
      max: "block"
```

### 3. Rule Explanation System

**Goal**: Every rule includes rationale, examples, and alternatives

**Format Enhancement for CRITICAL_RULES.md**:
```markdown
## Rule: Limit Function Length
<!-- RULE:function-length:max-50-lines -->

### Why This Rule Exists
- **Readability**: Long functions are hard to understand and test
- **Maintainability**: Smaller functions are easier to modify safely
- **Testing**: Each function should have a single, testable purpose

### Good Example
```python
def process_user_data(user_data: dict) -> User:
    validated_data = validate_user_data(user_data)
    normalized_data = normalize_user_fields(validated_data)
    return create_user_object(normalized_data)
```

### When to Override
- Database migrations (atomic operations)
- Complex mathematical algorithms (readability would suffer from splitting)
- Template rendering functions (logical unit)

### How to Override
```python
def long_migration_function():  # noqa: function-length
    """
    Justification: Database migration must be atomic.
    Splitting would require distributed transaction.
    """
    # ... migration code ...
```
```

### 4. Enhanced Memory Integration

**Goal**: Use existing MEMORY.md more effectively for rule learning

**Proposed MEMORY.md Sections**:
```markdown
## Rule Violation Patterns
<!-- Track patterns to identify systemic issues -->

### Recurring Violations
- **function_length**: 5 occurrences in auth module
  - Pattern: Authentication flows are inherently complex
  - Suggestion: Create auth-specific rule relaxation

### Successful Resolutions
- **deep_nesting**: Refactored using strategy pattern
  - Files: src/payment/processor.py
  - Reusable pattern for similar cases

## Project-Specific Patterns
<!-- Accumulated wisdom for this codebase -->

### Accepted Exceptions
1. Migration files can exceed function length limits
2. Test fixtures may use raw SQL for setup
3. Legacy module X uses different naming convention (migration in progress)
```

### 5. Agent Feedback System

**Goal**: Create bidirectional communication about rule effectiveness

**Implementation in hooks**:
```python
# src/quaestor/hooks/rule_feedback.py
class RuleFeedback:
    def report_false_positive(self, rule: str, context: dict):
        """Agent reports when rule blocks legitimate work"""
        self._append_to_memory(f"False positive: {rule} in {context}")
        
    def report_prevented_issue(self, rule: str, issue: str):
        """Agent reports when rule prevented a real problem"""
        self._append_to_memory(f"Rule {rule} prevented: {issue}")
        
    def suggest_modification(self, rule: str, suggestion: str):
        """Agent suggests rule improvement"""
        self._append_to_memory(f"Rule suggestion: {rule} - {suggestion}")
```

**Integration with milestone tracking**:
```yaml
# .quaestor/milestones/phase-1/tasks.yaml
- task_id: "implement-auth"
  rule_feedback:
    - rule: "function_length"
      violations: 3
      justified: 3
      comment: "Auth flows inherently complex"
    - rule: "test_coverage"  
      violations: 0
      comment: "Rule helped ensure comprehensive auth testing"
```

### 6. Progressive Rule Introduction

**Goal**: Don't overwhelm with all rules immediately

**Implementation**:
```python
# src/quaestor/rules/progressive.py
class ProgressiveRules:
    PHASES = {
        "initial": ["security", "data_safety", "basic_errors"],
        "development": ["testing", "documentation", "style"],
        "mature": ["performance", "accessibility", "advanced_patterns"],
        "production": ["all_rules"]
    }
    
    def get_active_rules(self, project_maturity: str, context: str) -> list:
        """Return only relevant rules for current project phase"""
        base_rules = self.PHASES.get(project_maturity, [])
        return self._filter_by_context(base_rules, context)
```

### 7. Interactive Rule Negotiation

**Goal**: Allow justified exceptions through dialogue

**Example Flow**:
```python
# Agent attempts to write 75-line function
System: "Function exceeds 50-line limit. This impacts readability."
Agent: "This is a database migration that must be atomic."
System: "Understood. Accepting exception for migration. Add comment: # noqa: function-length"
Agent: "Added comment with justification."
System: "Exception recorded in MEMORY.md for future reference."
```

**Recording in MEMORY.md**:
```markdown
### Negotiated Exceptions
- **Date**: 2024-01-16
- **Rule**: function_length
- **File**: migrations/2024_01_16_user_refactor.py
- **Justification**: Atomic database migration
- **Pattern**: Accept function_length violations in migrations/
```

## Implementation Roadmap

### Phase 1: Quick Wins (1 week)
1. Add enforcement levels to existing rules
2. Enhance CRITICAL_RULES.md with explanations
3. Create basic context detection from recent operations
4. Update MEMORY.md template for rule tracking

### Phase 2: Core Features (2-3 weeks)
1. Implement graduated enforcement in hooks
2. Build feedback system integrated with MEMORY.md
3. Add negotiation protocol for justified exceptions
4. Create context-aware rule modification

### Phase 3: Advanced Features (1 month)
1. Implement progressive rule introduction
2. Build pattern recognition from MEMORY.md
3. Create rule effectiveness metrics
4. Generate rule tuning recommendations

## Expected Benefits

### For Agents
- Less frustration from false positives
- Better understanding of quality requirements
- Ability to work efficiently while maintaining standards
- Learning that persists across sessions

### For Code Quality
- Higher compliance due to understanding
- Fewer workarounds due to flexibility
- Better rules through continuous improvement
- Documented exceptions with justifications

### For Teams
- Shared learning through MEMORY.md
- Consistent handling of exceptions
- Data-driven rule improvements
- Reduced onboarding time for new patterns

## Integration with Existing Systems

### MEMORY.md Enhancement
- Add structured sections for rule violations and resolutions
- Track patterns and project-specific exceptions
- Record negotiated exceptions with justifications

### Milestone Integration  
- Add rule_feedback field to tasks.yaml
- Track which rules helped or hindered each task
- Use for retrospective rule tuning

### Command Enhancement
- Add context awareness to command execution
- Allow commands to specify their intent
- Adjust rule enforcement accordingly

## Success Metrics

1. **Reduction in false positives** - Track unjustified blocks
2. **Increase in compliance** - Measure voluntary rule following
3. **Decrease in workarounds** - Monitor code quality metrics
4. **Improved velocity** - Track time saved by context awareness
5. **Learning effectiveness** - Measure pattern reuse from MEMORY.md

## Conclusion

These improvements transform Quaestor's rules from static constraints into an intelligent guidance system that:
- Adapts to development context
- Explains rather than merely enforces
- Learns from agent interactions
- Allows justified exceptions
- Improves through usage

The result is a partnership between agents and rules that enhances both productivity and code quality.