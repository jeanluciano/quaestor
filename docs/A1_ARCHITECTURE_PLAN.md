# Quaestor + A1 Architecture Plan

## Overview

A1 is an **automatic intelligence layer** for Quaestor that observes Claude Code's behavior through hooks and provides real-time insights, adaptive rule management, and predictive assistance through a TUI dashboard.

## Core Design Principles

1. **A1 depends on Quaestor** - Not a standalone tool
2. **Fully automatic** - No manual A1 commands required
3. **Hook-driven** - All intelligence triggered by Claude Code hooks
4. **Always visible** - TUI dashboard shows real-time insights
5. **Non-intrusive** - Works in background without interrupting workflow

## Architecture

### Event Flow

```
Claude Code Tool Use
        ↓
Claude Code Hooks (PreToolUse, PostToolUse, Stop, etc.)
        ↓
Quaestor Hook Handlers (Python)
        ↓
A1 Event Processing
        ↓
    ┌───┴───┐
    ↓       ↓
TUI Update  Rule Adaptations
            ↓
        Back to Quaestor
```

### System Components

```
┌─────────────────────────────────────────────────────┐
│                   Claude Code                        │
│              (AI Coding Assistant)                   │
└────────────────────┬────────────────────────────────┘
                     │ Hooks
                     ▼
┌─────────────────────────────────────────────────────┐
│                 Quaestor Core                        │
│  - Hook handlers                                     │
│  - Rule engine                                       │
│  - Context management                                │
│  - Event emission                                    │
└────────────────────┬────────────────────────────────┘
                     │ Events
                     ▼
┌─────────────────────────────────────────────────────┐
│                    A1 Service                        │
│  ┌─────────────────────────────────────────────┐    │
│  │          Event Processing Engine             │    │
│  │  - Intent detection                          │    │
│  │  - Pattern learning                          │    │
│  │  - Context building                          │    │
│  │  - Rule adaptation                           │    │
│  └─────────────────┬───────────────────────────┘    │
│                    │                                 │
│  ┌─────────────────┴───────────────────────────┐    │
│  │              TUI Dashboard                   │    │
│  │  - Real-time status                          │    │
│  │  - Metrics & insights                        │    │
│  │  - Learning history                          │    │
│  └─────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────┘
```

## Core Features

### 1. Intent Detection

A1 automatically detects Claude's current intent by analyzing hook event patterns:

- **Exploring**: Multiple Read operations, Grep searches, no writes
- **Implementing**: Read followed by Edit, test creation, systematic changes
- **Debugging**: Focused Read/Edit cycles, error searches, log analysis
- **Refactoring**: Multi-file edits, pattern replacement, no feature changes

### 2. Context-Aware Rule Management

Implements the graduated enforcement system from AGENT_RULE_IMPROVEMENTS.md:

- **Inform**: Log violation, continue work, track for review
- **Warn**: Show warning, highlight consequences, allow continuation
- **Justify**: Require explanation, record justification
- **Block**: Hard stop for critical safety/security rules

Rules adapt based on detected intent:
```python
# Example: Function length rule
- Exploring: INFORM (relaxed)
- Implementing: WARN (standard)
- Debugging: INFORM (relaxed)
- Refactoring: JUSTIFY (strict)
```

### 3. LSP-like Context Building

Using patterns similar to pretty-mod, A1 provides deep code understanding:

- Module structure analysis
- Function signature extraction
- Import relationship mapping
- Test coverage detection
- Cross-file dependency tracking

### 4. Pattern Learning

A1 learns from Claude's behavior:

- Common workflow patterns
- Project-specific conventions
- Frequently accessed file clusters
- Testing patterns
- Error resolution strategies

### 5. Predictive Assistance

Based on learned patterns, A1 predicts:

- Next files likely to be accessed
- Missing test files
- Incomplete implementations
- Required imports
- Documentation gaps

## TUI Dashboard Design

```
╭────────────────── A1 Intelligence Dashboard ─────────────────╮
│ Status: 🟢 Active  │  Session: 2h 34m  │  Events: 1,247      │
├──────────────────────────────────────────────────────────────┤
│ Current Intent: 🔧 Implementing Authentication               │
│ Confidence: 87%  │  Duration: 12m  │  Files: 5              │
│                                                              │
│ 📁 Context Understanding:                                    │
│ ├─ Working on: auth/login.py                                │
│ ├─ Related: auth/models.py, tests/test_auth.py             │
│ ├─ Imports: config.py, utils/jwt.py                        │
│ └─ Pattern: OAuth2 Implementation                           │
│                                                              │
│ 📏 Active Rules:                                            │
│ ├─ ✓ Security checks: ENFORCED (critical)                  │
│ ├─ ⚡ Function length: RELAXED (auth flow exception)       │
│ ├─ ⚠️  Test coverage: WATCHING (85% current)               │
│ └─ 📝 Documentation: INFORM (3 functions missing)          │
│                                                              │
│ 🧠 Recent Learnings:                                        │
│ • Auth flows in this project typically span 60-80 lines    │
│ • JWT tokens stored in config/secrets.py                   │
│ • Test files follow test_*.py pattern in tests/            │
│ • Team prefers class-based views for auth                  │
│                                                              │
│ 🔮 Predictions (Next Actions):                              │
│ • 85% - Edit auth/tokens.py (token generation)             │
│ • 72% - Create tests/test_login.py                         │
│ • 68% - Read config/auth.py (auth settings)                │
│ • 45% - Run pytest tests/test_auth.py                      │
│                                                              │
│ 📊 Session Metrics:                                         │
│ Files: 23 read, 8 edited │ Tests: 12 run, 2 failed        │
│ Rules: 5 relaxed, 2 enforced │ Patterns: 3 learned         │
╰──────────────────────────────────────────────────────────────╯
```

## Implementation Phases

### Phase 1: Foundation (Week 1)
- Set up A1 as Quaestor addon
- Implement basic hook event processing
- Create event queue system
- Basic intent detection from event patterns

### Phase 2: TUI Dashboard (Week 2)
- Build TUI using Rich/Textual
- Real-time event display
- Basic metrics tracking
- Intent visualization

### Phase 3: Rule Intelligence (Week 3-4)
- Implement graduated enforcement
- Context-aware rule adaptation
- Rule learning system
- Exception tracking

### Phase 4: Deep Context (Week 5-6)
- Integrate pretty-mod style analysis
- Build import graphs
- Test coverage mapping
- Semantic code understanding

### Phase 5: Predictive Engine (Week 7-8)
- Pattern recognition system
- Next action prediction
- Workflow template detection
- Suggestion engine

## Technical Implementation Details

### Hook Event Processing

```python
# A1 receives events from Quaestor hooks
class A1EventProcessor:
    def __init__(self):
        self.intent_detector = IntentDetector()
        self.context_builder = ContextBuilder()
        self.rule_adapter = RuleAdapter()
        self.pattern_learner = PatternLearner()
        self.tui = A1Dashboard()
    
    def on_hook_event(self, event: HookEvent):
        # Automatic processing - no user interaction
        intent = self.intent_detector.update(event)
        context = self.context_builder.update(event)
        rules = self.rule_adapter.adapt(intent, context)
        patterns = self.pattern_learner.learn(event, context)
        
        # Update TUI in real-time
        self.tui.update({
            'intent': intent,
            'context': context,
            'rules': rules,
            'patterns': patterns,
            'predictions': self.predict_next(context, patterns)
        })
```

### Event Types

```python
@dataclass
class HookEvent:
    type: str  # 'pre_tool_use', 'post_tool_use', 'stop'
    tool: str  # 'Read', 'Edit', 'Bash', etc.
    data: dict  # Tool-specific data
    timestamp: float
    session_id: str
```

### Communication Protocol

```python
# Quaestor → A1
{
    "event": "post_tool_use",
    "tool": "Edit",
    "data": {
        "file": "auth/login.py",
        "changes": 15,
        "duration": 1.2
    },
    "context": {
        "recent_files": ["auth/models.py", "config.py"],
        "active_rules": ["function_length", "security"]
    }
}

# A1 → Quaestor (Rule Adaptation)
{
    "rule_adaptations": {
        "function_length": {
            "level": "inform",
            "reason": "Auth flow implementation detected"
        }
    }
}
```

## Integration with Existing Systems

### Quaestor Hooks

A1 integrates seamlessly with Quaestor's existing hook system:

```python
# .quaestor/hooks/post_edit.py
def post_edit_hook(file_path, **kwargs):
    # Existing Quaestor logic
    
    # Send event to A1
    if a1_enabled():
        send_to_a1({
            'event': 'post_tool_use',
            'tool': 'Edit',
            'data': {'file': file_path, **kwargs}
        })
```

### MEMORY.md Enhancement

A1 automatically updates MEMORY.md with learned patterns:

```markdown
## A1 Learned Patterns

### 2024-01-16
- **Pattern**: OAuth2 Implementation
- **Files**: auth/login.py, auth/tokens.py, auth/models.py
- **Insight**: Auth flows typically 60-80 lines, use class-based views
- **Rule Adaptations**: Relaxed function_length for auth/*

### Project Conventions
- Test files: tests/test_*.py
- Config files: config/*.py  
- JWT tokens: config/secrets.py
```

## Benefits

### For Developers
- Real-time visibility into AI assistant's thinking
- Reduced friction from false-positive rule violations
- Better understanding of codebase patterns
- Predictive assistance saves time

### For AI Assistants
- Context-aware rule enforcement
- Learned exceptions reduce interruptions
- Richer context for better code generation
- Understanding of project-specific patterns

### For Teams
- Consistent handling of rule exceptions
- Shared learning across sessions
- Data-driven insights into development patterns
- Improved onboarding through captured knowledge

## Success Metrics

1. **Rule Effectiveness**
   - Reduction in false positives
   - Increase in voluntary compliance
   - Decrease in workarounds

2. **Productivity**
   - Time saved through predictions
   - Faster context building
   - Reduced repeated mistakes

3. **Learning Quality**
   - Pattern recognition accuracy
   - Prediction success rate
   - Context relevance score

4. **User Satisfaction**
   - TUI engagement metrics
   - Feature usage statistics
   - Developer feedback

## Future Enhancements

1. **Multi-Language Support**: Extend beyond Python to support JavaScript, TypeScript, Rust, etc.
2. **Team Learning**: Share learned patterns across team members
3. **Custom Dashboards**: Configurable TUI layouts for different workflows
4. **API Integration**: REST API for external tool integration
5. **Cloud Sync**: Optional pattern sharing across projects