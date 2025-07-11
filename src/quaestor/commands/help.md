---
allowed-tools: []
description: Show available Quaestor commands and their usage
---

# HELP - Quaestor Command Reference
<!-- META:command:help -->
<!-- META:version:1.0 -->

## 🏛️ Quaestor Commands

### Setup & Configuration
- **`/project-init`** - Initialize Quaestor documentation for your project
  - Analyzes your codebase structure
  - Generates ARCHITECTURE.md and MEMORY.md
  - Creates first project milestone
  - Interactive Q&A to understand your project

- **`quaestor init`** - Set up Quaestor in your repository (CLI command)
  - Creates .quaestor directory with templates
  - Installs commands to ~/.claude/commands
  - Sets up automation hooks

- **`quaestor update`** - Update Quaestor files to latest version (CLI command)

### Development Workflow
- **`/task "description"`** - Implement a feature or fix
  - Auto-detects project language (Python, Rust, JS, etc.)
  - Enforces Research → Plan → Implement workflow
  - Runs quality checks automatically
  - Example: `/task "add user authentication endpoint"`

- **`/check`** - Run comprehensive quality validation
  - Executes all linters and formatters
  - Runs test suite
  - Validates type checking
  - Reports any issues found

### Project Management
- **`/milestone-commit`** - Create atomic commits for completed work
  - Groups related changes
  - Generates clear commit messages
  - Updates progress tracking
  - Prepares for PR if configured

- **`/status`** - Show current project state
  - Current milestone progress
  - Pending tasks
  - Recent completions
  - Quality metrics

- **`/milestone`** - Create or complete project milestones
  - Mark current phase complete
  - Archive completed work
  - Start new development phase
  - Example: `/milestone --complete` or `/milestone --create "API Integration"`

### Getting Help
- **`/help`** - Show this help message
- **`/help [command]`** - Show detailed help for specific command *(coming soon)*

## 💡 Quick Start

1. **Starting a new feature:**
   ```
   /task "implement password reset flow"
   ```

2. **After making changes:**
   ```
   /check
   ```

3. **When ready to commit:**
   ```
   /milestone-commit
   ```

## 📋 Workflow Best Practices

1. **Always start with a task:** Don't jump straight to coding
2. **Use atomic commits:** Let /milestone-commit group related changes
3. **Run checks frequently:** Use /check after major changes
4. **Update progress:** Keep MEMORY.md current with your progress

## 🔧 Configuration

Your project's Quaestor configuration lives in:
- `.quaestor/` - Project-specific settings and docs
- `~/.claude/commands/` - Globally available commands
- `.claude/settings/` - Project hooks configuration

## 🚀 Examples

### Implementing a new feature:
```
> /task "add email notification system"
[Claude will research, plan, then implement with quality checks]
```

### Checking code quality:
```
> /check
[Claude will run all configured quality tools]
```

### Creating a commit:
```
> /milestone-commit
[Claude will analyze changes and create atomic commits]
```

## ❓ Need More Help?

- Read the full documentation in `.quaestor/QUAESTOR_CLAUDE.md`
- Check project conventions in `.quaestor/ARCHITECTURE.md`
- Review progress in `.quaestor/MEMORY.md`

---
*Quaestor - Maintaining consistency and productivity in AI-assisted development*