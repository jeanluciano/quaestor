# Quaestor Tests

Quaestor is now a feature-complete Claude Code plugin. 

The previous test suite tested the old architecture:
- `quaestor.core` module (removed)
- CLI commands (removed) 
- Hooks system (removed)
- Configuration system (removed)

As a Claude Code plugin, Quaestor's functionality is now defined by:
- Skills in `src/quaestor/skills/`
- Slash commands in `src/quaestor/commands/`
- Sub-agents in `src/quaestor/agents/`

These are markdown-based and tested through Claude Code's plugin system.
