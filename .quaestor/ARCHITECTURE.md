# Quaestor Architecture

## Architecture Overview

Quaestor follows a **Modular Monolithic Architecture** with a plugin-based extension system. The core system provides fundamental context management capabilities, while the A1 Intelligence Layer adds advanced AI-assisted features.

```yaml
pattern:
  selected: "Modular Monolithic with Plugin Architecture"
  description: "Provides stability and extensibility - core features are reliable while advanced features can evolve independently"
```

## System Components

### Core System (`src/quaestor/`)
```
quaestor/
├── cli/              # Command-line interface (Typer-based)
│   ├── init.py       # Project initialization
│   ├── configure.py  # Configuration management
│   ├── update.py     # Update mechanism
│   └── automation.py # Hook management
├── core/             # Core business logic
│   ├── project_analyzer.py    # Project detection
│   ├── rule_engine.py         # Rule generation
│   ├── template_engine.py     # Template processing
│   └── project_metadata.py    # Manifest tracking
├── automation/       # Hook system
│   ├── hook_base.py  # Base hook classes
│   ├── enforcement.py # Rule enforcement
│   └── workflow.py    # Workflow management
└── assets/           # Resources
    ├── templates/    # Markdown templates
    ├── hooks/        # Pre-built hooks
    └── configuration/ # Language configs
```

### A1 Intelligence Layer (`src/a1/`)
```
a1/
├── core/            # Event-driven foundation
│   ├── events.py    # Event bus system
│   ├── context.py   # Intent analysis
│   └── quality.py   # Quality management
├── enforcement/     # Graduated enforcement
│   ├── enforcement_levels.py  # INFORM→WARN→JUSTIFY→BLOCK
│   ├── rule_enforcer.py       # Base enforcement
│   ├── adaptive_enforcer.py   # Context-aware adaptation
│   └── rule_adapter.py        # Strategy selection
├── learning/        # Pattern recognition
│   ├── pattern_recognizer.py  # Exception patterns
│   ├── confidence_scorer.py   # Pattern confidence
│   └── file_store.py          # Persistent storage
├── analytics/       # Insights and tracking
│   ├── exception_tracker.py   # Exception events
│   └── exception_reporter.py  # Analytics reports
└── tui/            # Terminal UI
    └── dashboard.py # Real-time monitoring
```

## Design Patterns

### Command Pattern
- Each CLI command is a separate module
- Commands are discovered and registered dynamically
- Enables easy addition of new commands

### Hook System (Observer Pattern)
- Hooks observe file operations and commands
- Decoupled from core logic via `HookBase`
- Supports pre/post execution points

### Template Engine (Strategy Pattern)
- Different processing strategies per project type
- Language-specific configurations
- Adaptive template population

### Event Bus (Pub/Sub Pattern)
- A1 components communicate via events
- Loose coupling between subsystems
- Enables real-time monitoring

### Abstract Factory Pattern
- `RuleEnforcer` hierarchy for different rule types
- `BaseHook` for various hook implementations
- Consistent interfaces with varying implementations

## Data Flow

### 1. Command Execution
```
User Input → CLI Parser → Command Handler → Core Logic → Output
                              ↓
                         Hook System → Pre/Post Hooks
```

### 2. Hook Processing
```
File Operation → Hook Trigger → Rule Check → Enforcement Decision
                                     ↓
                              A1 Learning → Pattern Recognition
```

### 3. A1 Intelligence Flow
```
Event → Event Bus → Subscribers
           ↓
    Context Analysis → Rule Adaptation → Enforcement
           ↓
    Pattern Learning → Confidence Scoring → Future Adaptations
```

## Key Architecture Decisions

### 1. Separation of Concerns
- **Core Quaestor**: Stable, essential features
- **A1 Layer**: Experimental, intelligent features
- Clear boundaries prevent instability spread

### 2. File-Based Storage
- JSON/YAML for configuration and state
- Human-readable and version-control friendly
- No database dependencies

### 3. Progressive Enhancement
- Core system works without A1
- A1 features enhance but don't replace core
- Graceful degradation if components fail

### 4. Extensibility Points
- Hook system for custom automation
- Template system for project types
- Command system for new features
- Event bus for monitoring

## Integration Points

### Claude AI Integration
- CLAUDE.md as primary context file
- Hook system for AI-assisted workflows
- Template generation for documentation

### Development Tools
- Git integration for version control
- Language-specific tool detection
- Build system awareness

### Future Extensions
- Plugin marketplace for hooks
- Cloud synchronization
- Team collaboration features
- IDE integrations

## Performance Considerations

- **Fast Startup**: Lazy loading of components
- **Efficient File Operations**: Batch processing where possible
- **Memory Management**: Stream large files
- **Response Time Target**: <200ms for operations

## Security Considerations

- **Hook Sandboxing**: Timeout protection
- **Input Validation**: Path traversal prevention
- **No Credential Storage**: Relies on system auth
- **Audit Logging**: Track all operations