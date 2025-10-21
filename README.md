# Quaestor

> A minimal Claude Code plugin for specification-driven development

[![PyPI Version](https://img.shields.io/pypi/v/quaestor.svg)](https://pypi.org/project/quaestor/)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue.svg)](https://jeanluciano.github.io/quaestor)

Quaestor is a Claude Code plugin that provides Skills and slash commands for specification-driven development. Write lightweight specs, implement with context, ship with confidence.

**Design Principles:**
- **Zen** - Minimal surface area, maximum utility
- **Engineer as Driver** - You make decisions, Quaestor provides structure
- **Light Spec-Driven** - Just enough specification to stay aligned

**_NOTE:_** Quaestor has been many things, but mainly a learning sandbox for me. Nowadays, it's a tool that I and a small number of people use. From 1.0 forward, Quaestor will be boring and stable. New features will be planned and added as Anthropic releases new features for Claude Code. This is all to say that Quaestor is "feature complete," and hardly any skills, sub-agents, or commands will be added. I've gotta get back to work, and so do you.

## What's Included

**7 Skills** (auto-activate based on context):
- `managing-specifications` - Create and manage specifications
- `implementing-features` - Implement features with quality gates
- `reviewing-and-shipping` - Code review and PR generation
- `debugging-issues` - Systematic bug investigation
- `security-auditing` - Security analysis and vulnerability detection
- `optimizing-performance` - Performance profiling and optimization
- `initializing-project` - Setup Quaestor in any project

**3 Slash Commands:**
- `/plan` - Create specifications
- `/implement` - Implement specs with tracking
- `/research` - Explore codebase patterns

**Spec Lifecycle:**
- Folder-based state: `draft/` → `active/` → `completed/`
- Automatic progress tracking via checkboxes
- Max 3 active specs (enforced)

## Installation

### As a Claude Code Plugin (Recommended)

Install directly from the marketplace:
```bash
/plugin install quaestor@quaestor-official
```

Alternatively, you can add the marketplace and install separately:
```bash
/plugin marketplace add jeanluciano/quaestor
/plugin install quaestor:quaestor
```

See [Claude Code plugins documentation](https://docs.claude.com/en/docs/claude-code/plugins) for details.

### Via pip/uv (Project-Level)

For project-level installation:
```bash
pip install quaestor
# or
uv pip install quaestor
```

Then initialize in your project:
```bash
quaestor init
```

## Quick Start

```bash
# Install the plugin
/plugin install quaestor@quaestor-official

# Create a spec
/plan "User authentication with JWT"

# Implement it
/implement spec-auth-001

# Ship it
"Create a pull request for spec-auth-001"
```

Skills activate automatically based on what you're doing. Just describe what you want in natural language:
- "Show my active specs" → managing-specifications skill
- "Debug the login failure" → debugging-issues skill
- "Review this code for security issues" → security-auditing skill

## How It Works

### Specifications
Create lightweight specifications that define:
- What you're building (title and description)
- Why you're building it (motivation)
- What success looks like (acceptance criteria as checkboxes)

Specs live in `.quaestor/specs/` and move through folders as they progress:
```
.quaestor/specs/
├── draft/      # Planned work
├── active/     # In progress (max 3)
└── completed/  # Finished
```

### Skills
Skills are auto-activating workflows that trigger based on context. You don't invoke them directly - just describe what you want:
- Want to plan? Say "create a spec for X" → managing-specifications activates
- Want to implement? Use `/implement spec-id` → implementing-features activates
- Want to ship? Say "create a PR" → reviewing-and-shipping activates

### Example Session
```bash
# Create a spec
/plan "Add rate limiting to API endpoints"
# → spec-feature-042.md created in draft/

# Start implementing
/implement spec-feature-042
# → Skills guide you through implementation with quality checks

# Check progress
"What's the status of spec-feature-042?"
# → "spec-feature-042: 3/5 criteria complete (60%)"

# Ship it
"Create a pull request for spec-feature-042"
# → PR created with spec context included
```

## Documentation

📚 **[Full Documentation](https://jeanluciano.github.io/quaestor)**

- [Installation & Setup](https://jeanluciano.github.io/quaestor/getting-started/installation/)
- [Quick Start Guide](https://jeanluciano.github.io/quaestor/getting-started/quickstart/)
- [Specification-Driven Development](https://jeanluciano.github.io/quaestor/specs/overview/)
- [Agent System](https://jeanluciano.github.io/quaestor/agents/overview/)

## Contributing

```bash
git clone https://github.com/jeanluciano/quaestor.git
cd quaestor
pip install -e .
pytest
```

## License

MIT License

---

<div align="center">

[Documentation](https://jeanluciano.github.io/quaestor) · [Issues](https://github.com/jeanluciano/quaestor/issues)

</div>