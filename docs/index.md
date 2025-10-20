# Quaestor

**A minimal Claude Code plugin for specification-driven development**

Quaestor provides Skills and slash commands for structured development workflows. Write lightweight specs, implement with context, ship with confidence.

**Design Principles:**
- **Zen** - Minimal surface area, maximum utility
- **Engineer as Driver** - You make decisions, Quaestor provides structure
- **Light Spec-Driven** - Just enough specification to stay aligned

## What's Included

### 7 Skills (Auto-Activating)
- `managing-specifications` - Create and manage specifications
- `implementing-features` - Implement features with quality gates
- `reviewing-and-shipping` - Code review and PR generation
- `debugging-issues` - Systematic bug investigation
- `security-auditing` - Security analysis and vulnerability detection
- `optimizing-performance` - Performance profiling and optimization
- `initializing-project` - Setup Quaestor in any project

### 3 Slash Commands
- `/plan` - Create specifications
- `/implement` - Implement specs with tracking
- `/research` - Explore codebase patterns

### Spec Lifecycle
- Folder-based state: `draft/` → `active/` → `completed/`
- Automatic progress tracking via checkboxes
- Max 3 active specs (enforced)

## Quick Start

```bash
# Add the marketplace
/plugin marketplace add jeanluciano/quaestor

# Install the plugin
/plugin install quaestor:quaestor

# In Claude Code, create a spec
/plan "User authentication with JWT"

# Implement it
/implement spec-auth-001

# Ship it
"Create a pull request for spec-auth-001"
```

Skills activate automatically based on what you're doing:
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

## Getting Started

Ready to transform your AI-assisted development workflow? Check out our [Quick Start Guide](getting-started/quickstart.md) to begin using Quaestor in your projects.

## Community

- [GitHub Repository](https://github.com/jeanluciano/quaestor)
- [Issues & Bug Reports](https://github.com/jeanluciano/quaestor/issues)
- [PyPI Package](https://pypi.org/project/quaestor/)

---

*Quaestor: Where AI meets systematic development*