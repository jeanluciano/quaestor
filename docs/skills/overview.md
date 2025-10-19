# Agent Skills Overview

Quaestor v1.0 introduces **Agent Skills** - auto-activating capabilities that handle specification management without manual invocation.

## What are Agent Skills?

Agent Skills are specialized capabilities that Claude automatically uses based on your natural language requests. You don't need to know they exist - they just work!

### Traditional Approach (Pre-v1.0)
```
User: "Create a spec for user auth"
You: Manually invoke planner agent → speccer agent → save file
```

### Skills Approach (v1.0+)
```
User: "Create a spec for user auth"
Claude: ✅ Spec Writing Skill activates automatically
Result: Spec created in .quaestor/specs/draft/
```

## Quaestor's Skills

### 1. Spec Writing Skill
**Auto-activates when:** User describes features/fixes, mentions "create spec", "plan feature"

**What it does:**
- Asks clarifying questions
- Generates Markdown specifications
- Saves to `.quaestor/specs/draft/`
- No manual file creation needed

**Example triggers:**
- "I want to add user authentication"
- "Create a spec for API rate limiting"
- "Plan a bug fix for memory leak"

### 2. Spec Management Skill
**Auto-activates when:** User mentions "spec status", "activate", "complete", "progress"

**What it does:**
- Tracks progress from checkbox completion
- Moves specs between draft/active/completed
- Enforces 3-active-spec limit
- Calculates completion percentages

**Example triggers:**
- "What's the status of my specs?"
- "Activate spec-feature-001"
- "Complete spec-feature-002"
- "Show me active specifications"

### 3. PR Generation Skill
**Auto-activates when:** User mentions "create pr", "pull request", "submit for review"

**What it does:**
- Reads completed specifications
- Generates comprehensive PR descriptions
- Creates GitHub PRs via `gh` CLI
- Includes acceptance criteria and test info

**Example triggers:**
- "Create a pull request"
- "Make a PR for spec-feature-001"
- "Submit this for review"

## How Skills Work

### Automatic Activation
Skills activate based on context and keywords:

```
User says: "What's the status of spec-auth-001?"

Behind the scenes:
1. Claude detects keywords: "status", "spec"
2. Spec Management Skill activates
3. Reads .quaestor/specs/ folders
4. Calculates progress from checkboxes
5. Reports status to user

You see: "spec-auth-001: 80% complete (4/5 criteria)"
```

### Tool Restrictions
Skills have limited tool access for safety:

- **Spec Writing**: Can Write, Read, Glob (creates files)
- **Spec Management**: Can Read, Edit, Bash, Grep, Glob (manages lifecycle)
- **PR Generation**: Can Read, Bash (reads specs, runs gh CLI)

### Progressive Disclosure
Skills only load what they need:

```
spec-management/
├── SKILL.md           # Always loaded (core instructions)
├── lifecycle.md       # Loaded when needed (detailed state info)
└── progress.md        # Loaded when calculating progress
```

This keeps context usage low.

## Benefits

### For Users
- **Zero learning curve** - Just describe what you want
- **No manual coordination** - Skills activate automatically
- **Natural language** - Talk normally, not in commands
- **Always available** - Installed with plugin

### For Developers
- **Maintainable** - Skills are markdown files, easy to update
- **Composable** - Skills can work together
- **Discoverable** - Users can read SKILL.md to understand
- **Safe** - Tool restrictions prevent accidental damage

## Customization

Skills are just markdown files - you can customize them!

### View a Skill
```bash
cat src/quaestor/skills/spec-writing/SKILL.md
```

### Modify a Skill
Edit the SKILL.md file to change behavior:
- Update trigger keywords in description
- Modify instructions
- Add examples
- Change tool permissions

### Create Your Own
Follow the same structure:

```markdown
---
name: Your Skill Name
description: What it does and when to use it
allowed-tools: [Read, Write, Grep]
---

# Your Skill Name

## When to Use Me
[Trigger conditions]

## Instructions
[Step-by-step guide]
```

## Comparison with Agents

| Feature | Agent Skills | Traditional Agents |
|---------|-------------|-------------------|
| **Activation** | Automatic (model-invoked) | Manual (user-invoked) |
| **Invocation** | Natural language triggers | Explicit Task tool call |
| **Use case** | Context-triggered capabilities | Complex multi-step workflows |
| **Tool access** | Restricted by allowed-tools | Full access |
| **Learning curve** | Zero - just talk | Need to know when to invoke |

### When to Use Each

**Use Skills for:**
- Spec management (create, track, complete)
- PR generation
- Status checking
- File operations with clear triggers

**Use Agents for:**
- Complex research (multi-file analysis)
- Architectural design (deep thinking)
- Implementation (multi-step coding)
- Debugging (investigation workflows)

## Migration from v0.x

If you're upgrading from Quaestor v0.x:

### What Changed
- ❌ Removed: `quaestor spec` CLI commands
- ❌ Removed: spec-manager and speccer agents
- ❌ Removed: manifest.json tracking
- ✅ Added: 3 Agent Skills
- ✅ Simplified: specifications.py (944→261 lines)
- ✅ Simplified: /plan command (522→336 lines)

### What Stayed the Same
- ✅ Folder structure: draft/active/completed
- ✅ Markdown specifications
- ✅ Checkbox progress tracking
- ✅ Other agents (researcher, architect, etc.)

### Migration Steps
1. Update to v1.0.0
2. Existing specs work as-is (no conversion needed)
3. Use natural language instead of CLI commands:
   - Old: `quaestor spec activate spec-001`
   - New: "activate spec-001"

## Examples

### Complete Workflow
```
1. User: "I want to add user authentication"
   → Spec Writing Skill: Creates spec in draft/

2. User: "Activate spec-feature-001"
   → Spec Management Skill: Moves to active/

3. User: "/impl spec-feature-001"
   → Implementation happens, checkboxes marked

4. User: "What's the progress?"
   → Spec Management Skill: "80% complete (4/5 criteria)"

5. User: "Complete spec-feature-001"
   → Spec Management Skill: Moves to completed/

6. User: "Create a pull request"
   → PR Generation Skill: Creates GitHub PR
```

### All Natural Language
No commands to memorize - just describe what you want!

## Learn More

- [Spec Writing Skill](./spec-writing.md) - Details on spec creation
- [Spec Management Skill](./spec-management.md) - Lifecycle management
- [PR Generation Skill](./pr-generation.md) - Pull request automation
- [Claude Code Skills Docs](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview) - Official documentation

---

*Agent Skills make Quaestor effortless - just describe what you want, and it happens automatically!*
