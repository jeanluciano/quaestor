# A1 Rule Intelligence Integration Guide

## Overview

The A1 Rule Intelligence system enhances Quaestor's enforcement capabilities with:
- **Graduated Enforcement**: INFORM → WARN → JUSTIFY → BLOCK levels
- **Context-Aware Adaptation**: Rules adapt based on developer experience, workflow phase, and time pressure
- **Learning System**: Learns from override patterns to reduce false positives
- **Seamless Integration**: Works alongside existing Quaestor hooks

## Architecture

```
Quaestor Hooks                    A1 Intelligence Layer
     │                                    │
     ├─ BaseHook                         ├─ IntelligentHook (extends BaseHook)
     ├─ HookResult (binary)              ├─ EnforcementResult (4 levels)
     └─ Simple enforcement               └─ Adaptive enforcement
```

## Integration Approaches

### 1. New Hooks with Intelligence

Create new hooks that inherit from `IntelligentHook`:

```python
from a1.hooks import IntelligentHook
from a1.enforcement.rules import ResearchBeforeImplementationRule

class SmartResearchHook(IntelligentHook):
    def __init__(self):
        rule = ResearchBeforeImplementationRule()
        super().__init__("smart-research", rule_enforcer=rule)
    
    def execute_hook_logic(self):
        # Your hook logic here
        # This runs only if enforcement passes
        pass
```

### 2. Enhance Existing Hooks

Wrap existing Quaestor hooks with A1 intelligence:

```python
from a1.integration import wrap_quaestor_hook
from a1.enforcement import EnforcementLevel

# Original hook function
def check_something(context):
    if context.get("tool") == "Write":
        return HookResult(False, "Writing not allowed")
    return HookResult(True, "Check passed")

# Enhanced with A1
smart_check = wrap_quaestor_hook(
    check_something,
    rule_id="smart_check",
    rule_name="Smart Check",
    base_level=EnforcementLevel.WARN
)
```

### 3. Gradual Migration

Existing hooks continue to work unchanged. Migrate incrementally:

1. **Phase 1**: Add context tracking to existing hooks
2. **Phase 2**: Wrap critical hooks with A1 intelligence
3. **Phase 3**: Convert to IntelligentHook for full features

## Enforcement Levels

### INFORM (Least Restrictive)
- Logs information, no blocking
- Used for: new rules, suggestions, tips
- Example: "ℹ️ Consider adding tests for this function"

### WARN
- Shows warning but allows continuation
- Used for: best practices, code quality
- Example: "⚠️ Function exceeds 50 lines, consider refactoring"

### JUSTIFY
- Requires justification to proceed
- Used for: policy violations, risky changes
- Example: "🔒 Research required before implementation. Justification needed."

### BLOCK (Most Restrictive)
- Blocks action unless override provided
- Used for: critical violations, security issues
- Example: "❌ Insufficient test coverage. Override required."

## Context Factors

The system adapts enforcement based on:

1. **Developer Experience** (0.0 - 1.0)
   - Calculated from git history
   - More experienced = more flexibility

2. **Time Pressure** (0.0 - 1.0)
   - Detected from keywords, workflow velocity
   - Higher pressure = reduced enforcement

3. **Workflow Phase**
   - `research`: More lenient
   - `planning`: Balanced
   - `implementing`: Stricter

4. **Previous Violations**
   - Repeat violations increase enforcement
   - Clean history reduces strictness

## Override System

Users can override rules with justification:

```bash
# Justify override
--justify "Emergency hotfix for production issue"

# Strong override (for BLOCK level)
--override "CEO approved deadline-critical feature"
```

Overrides are:
- Tracked for learning
- Time-limited (default 4 hours)
- Analyzed for patterns

## Learning System

The A1 system learns from:
- Override patterns
- False positive reports
- Developer feedback

Example learning:
- If "test files" are repeatedly overridden for a rule
- System learns to reduce enforcement for test files
- Confidence increases with pattern frequency

## Configuration

Configure in `.quaestor/a1_config.yaml`:

```yaml
enforcement:
  base_levels:
    research_before_impl: JUSTIFY
    complexity_limit: WARN
    test_coverage: WARN
    documentation: INFORM
  
  adaptation:
    experience_weight: 0.3
    time_pressure_weight: 0.2
    phase_weight: 0.5
  
  learning:
    min_pattern_frequency: 3
    confidence_threshold: 0.7
    max_learned_exceptions: 100
```

## Migration Example

### Before (Quaestor Hook):
```python
def check_research_before_implementation(tool):
    state = WorkflowState()
    if tool in ["Write", "Edit"] and state.phase == "idle":
        return HookResult(False, "Research required first")
    return HookResult(True, "Check passed")
```

### After (A1 Enhanced):
```python
class IntelligentResearchCheck(IntelligentHook):
    def __init__(self):
        rule = ResearchBeforeImplementationRule()
        super().__init__("research-check", rule_enforcer=rule)
    
    def execute_hook_logic(self):
        # Enforcement already handled by parent class
        # Add any additional logic here
        self.output_success("Research check completed")
```

Benefits:
- Automatic context detection
- Graduated enforcement (not just block/allow)
- Learning from overrides
- Better developer experience

## Best Practices

1. **Start with INFORM/WARN** for new rules
2. **Monitor override patterns** to tune enforcement
3. **Use context factors** to reduce false positives
4. **Provide clear suggestions** in rules
5. **Allow overrides** with justification

## Troubleshooting

### High False Positive Rate
- Check context detection accuracy
- Review enforcement level settings
- Analyze override patterns

### Rules Too Lenient
- Increase base enforcement levels
- Adjust context weights
- Review learned exceptions

### Integration Issues
- Ensure proper imports
- Check hook inheritance
- Verify context builder setup