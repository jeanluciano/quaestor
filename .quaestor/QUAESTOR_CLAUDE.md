# Working with Quaestor - AI Collaboration Guide

<!-- QUAESTOR:version:1.0 -->

## ⚠️ CRITICAL: MANDATORY RULES ENFORCEMENT

**BEFORE READING FURTHER**: Load and validate [RULES.md](./.quaestor/RULES.md)

```yaml
rule_enforcement:
  status: "ACTIVE"
  mode: "STRICT"
  validation_required: "BEFORE_EVERY_ACTION"
  violations_allowed: 0
  consequences: "IMMEDIATE_STOP"
```

### Pre-Action Checklist (MANDATORY)
- [ ] Have I loaded RULES.md?
- [ ] Am I running quality checks (make lint, make test)?
- [ ] Am I following the manager/service pattern?
- [ ] Are file operations atomic and safe?
- [ ] Is hook feedback being treated as mandatory?

## Important
- **Production Quality**: We're building production-quality code TOGETHER. Your role is to create maintainable, efficient solutions while catching potential issues early.
- **Mandatory Compliance**: ALL instructions within this document MUST BE FOLLOWED, these are not optional unless explicitly stated.
- **Hook Compliance**: Hook feedback is MANDATORY and must be treated as requirements, not suggestions.
- **Ask for Help**: ASK FOR CLARIFICATION when you seem stuck or overly complex, I'll redirect you.
- **CRITICAL**: Rules in [RULES.md](./.quaestor/RULES.md) override everything else.

## CRITICAL WORKFLOW

### Research → Plan → Implement

**NEVER JUMP STRAIGHT TO CODING!** Always research the codebase first to understand existing patterns.

**Required Response**: When asked to implement any feature, you MUST say: "Let me research the codebase and create a plan before implementing."

### USE MULTIPLE AGENTS!

**Required Response**: You MUST say: "I'll spawn agents to tackle different aspects of this problem" whenever a task has multiple independent parts like:
- Analyzing different layers (CLI, core, utils)
- Creating tests and implementation
- Security review and performance optimization

### Reality Checkpoints
**Stop and validate** at these moments:
- After implementing a complete feature
- Before starting a new major component
- When something feels wrong
- Before declaring "done"
- **After receiving hook feedback** - MANDATORY compliance required

Run the project's test suite regularly: `make test` and `make lint`

## Working Memory Management

### When context gets long:
- Re-read this QUAESTOR_CLAUDE.md file
- Check active specifications in .quaestor/specs/active/
- Review RULES.md for compliance

### Active Work Tracking:
Track progress directly in your specification files:
- **Active Specs**: Located in .quaestor/specs/active/
- **Current Work**: Update task status and progress
- **Progress**: Track completed tasks in specifications
- **Next Actions**: Listed in specification tasks

### Problem-Solving Together

When you're stuck or confused:
1. **Stop** - Don't spiral into complex solutions
2. **Delegate** - Consider spawning agents for parallel investigation
3. **Step back** - Re-read the requirements
4. **Simplify** - The simple solution is usually correct
5. **Ask** - "I see two approaches: [A] vs [B]. Which do you prefer?"

**Remember**: My insights on better approaches are valued - please ask for them!

## Hook System Integration

### MANDATORY Hook Compliance

**CRITICAL**: Hooks provide MANDATORY feedback, not suggestions. All hook outputs must be treated as requirements and addressed before proceeding with any action.

### Hook Types and Required Actions

**Current Hooks**:
- `session_context_loader.py` - Loads project context and active specifications
- `base.py` - Base hook functionality
- **Required Action**: Follow ALL hook recommendations

### Hook Feedback Processing

1. **Read ALL hook output completely**
2. **Address EVERY requirement listed**
3. **Do not proceed until ALL hook feedback is resolved**
4. **Treat hook failures as blocking errors**

# PROJECT OVERVIEW

### Project Context
Quaestor is a Python CLI tool for AI-assisted development context management. It helps developers manage specifications, track work progress, and maintain project documentation in a way that's optimized for AI collaboration.

### Current Status
- Version: 0.5.2 (PyPI) / 0.6.0 (development)
- Architecture: Service-oriented with manager pattern
- Framework: Typer CLI with Rich UI
- Storage: File-based YAML persistence

### Project Documentation
For detailed information about the project:
- **[Active Specifications](./.quaestor/specs/active/)**: Current work in progress
- **[ARCHITECTURE.md](./.quaestor/ARCHITECTURE.md)**: Technical architecture and design principles

# ARCHITECTURE & CODE GUIDELINES

See **[ARCHITECTURE.md](./.quaestor/ARCHITECTURE.md)** for:
- Service/Manager architecture pattern
- Layer responsibilities and boundaries
- Component interactions

### Code Style Guidelines
- **Language**: Python 3.12+
- **Focused changes**: Only implement explicitly requested or fully understood changes
- **Type Safety**: Full type hints on all functions and methods
- **Documentation**: Docstrings for all public functions
- **Formatting**: Ruff for linting and formatting
- **Imports**: 
  - Order: standard library, third-party, local imports
  - Use absolute imports from project root
- **Naming Conventions**:
  - Functions/variables: `snake_case`
  - Classes: `PascalCase`
  - Constants: `UPPER_SNAKE_CASE`
  - Files: `snake_case.py`
- **Best Practices**:
  - Managers handle business logic, dataclasses hold data
  - All file operations must be atomic
  - Use Path objects from pathlib, not strings
  - Comprehensive error handling with user-friendly messages

# AVAILABLE COMMANDS

The project provides these main commands:
- `quaestor init` - Initialize a new Quaestor project
- `quaestor configure` - Configure project settings
- `quaestor update` - Update project configuration

Slash commands for Claude:
- `/plan` - Create specifications and plan work
- `/impl` - Implement approved specifications
- `/project-init` - Initialize Quaestor in a project

# DEVELOPMENT WORKFLOW

### Testing and Quality

**MANDATORY before any commit**:
```bash
# Run all tests
make test

# Run linting
make lint

# Run specific test file
pytest tests/unit/test_specifications.py

# Run with coverage
make test-cov
```

### Working with the Codebase

1. Follow established patterns in the codebase
2. Use managers for business logic, not dataclasses
3. All file operations through utils for atomicity
4. **MANDATORY**: Address all hook compliance issues before proceeding

### Development Process

1. Create specifications for new features
2. Write tests before implementing features (TDD)
3. Keep commits small and focused
4. Write clear commit messages
5. Update documentation as you go
6. **CRITICAL**: Follow hook feedback as mandatory requirements

### Common Tasks

**Creating a new manager**:
```python
# In src/quaestor/core/
class NewManager:
    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        # Initialize as needed
    
    def perform_action(self) -> bool:
        """Business logic here."""
        # Use utils for file operations
        # Return success/failure
```

**Adding a CLI command**:
```python
# In src/quaestor/cli/
@app.command()
def new_command(
    arg: str = typer.Argument(..., help="Description"),
    option: bool = typer.Option(False, "--flag", help="Description"),
) -> None:
    """Command description."""
    console.print("[bold]Running command...[/bold]")
    # Delegate to manager
    # Show progress with rich
    # Handle errors gracefully
```

---
*This document helps Claude work effectively with the Quaestor project. Generated by project-init based on codebase analysis.*