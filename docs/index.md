# Quaestor

**Context management for AI-assisted development**

Quaestor is a powerful framework that enhances AI-assisted development by providing structured context management, specification-driven workflows, and intelligent automation hooks. It transforms how you work with AI coding assistants like Claude Code.

## Key Features

### 🤖 Intelligent Agent System
- Specialized AI agents for different development phases
- Context-aware agent suggestions based on project state
- Seamless integration with Claude Code

### 🔄 Smart Automation Hooks
- Enforce specification-driven workflows
- Automatic progress tracking and specification updates
- Quality gates and compliance checking

### 🎯 Specification-Driven Development
- Create detailed specifications with contracts, acceptance criteria, and test scenarios
- Automatic branch-to-specification linking
- Progress tracking through specification status

### 📊 Progress Management
- Visual progress dashboards
- Progress tracking through specification completion
- Memory management for project context

## Quick Start

```bash
# Install Quaestor
pip install quaestor

# Initialize in your project
quaestor init

# Create your first specification
/plan --spec "User Authentication System"

# Implement according to the specification
/impl "implement user login"
```

## Architecture

Quaestor consists of several integrated components:

- **Core Specification System**: Manages specifications as first-class entities
- **Agent Framework**: Provides specialized AI agents for different workflows
- **Hook System**: Enforces workflows and tracks progress automatically
- **Command Interface**: Slash commands for Claude Code integration
- **Memory Management**: Maintains project context and progress

## Why Quaestor?

Traditional AI-assisted development often lacks structure, leading to:
- Unclear requirements and scope creep
- Inconsistent implementation patterns
- Poor progress tracking
- Difficulty maintaining context across sessions

Quaestor solves these problems by providing:
- **Clear Contracts**: Specifications define exact inputs, outputs, and behavior
- **Systematic Workflows**: Enforced development processes
- **Automatic Tracking**: Progress tracked without manual intervention
- **Context Preservation**: Project memory maintained across sessions

## Getting Started

Ready to transform your AI-assisted development workflow? Check out our [Quick Start Guide](getting-started/quickstart.md) to begin using Quaestor in your projects.

## Community

- [GitHub Repository](https://github.com/jeanluciano/quaestor)
- [Issues & Bug Reports](https://github.com/jeanluciano/quaestor/issues)
- [PyPI Package](https://pypi.org/project/quaestor/)

---

*Quaestor: Where AI meets systematic development*