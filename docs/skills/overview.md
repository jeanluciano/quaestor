# Skills Overview

Quaestor provides **Skills** - auto-activating workflows that handle specific development tasks. Skills trigger automatically based on context and orchestrate sub-agents internally.

## What are Skills?

Skills are specialized workflows that:
- Activate automatically based on keywords and context
- Orchestrate multiple sub-agents internally
- Provide focused capabilities for specific tasks
- Work through natural language - no manual invocation needed

## Available Skills

Quaestor includes 7 Skills:

### 1. managing-specifications
**Activates when:** Creating specs, checking status, managing lifecycle

**What it does:**
- Creates specifications from requirements
- Manages spec lifecycle (draft → active → completed)
- Tracks progress from checkboxes
- Enforces 3-active-spec limit

**Example triggers:**
- "Create a spec for user authentication"
- "Show my active specs"
- "Activate spec-feature-001"
- "Complete spec-auth-001"

### 2. implementing-features
**Activates when:** Using `/implement` or implementing features

**What it does:**
- Loads specifications and requirements
- Coordinates research, architecture, implementation, testing, review
- Tracks progress via TODOs
- Runs tests and validates criteria

**Example triggers:**
- `/implement spec-auth-001`
- `/implement "Add rate limiting"`

### 3. reviewing-and-shipping
**Activates when:** Creating PRs, shipping work

**What it does:**
- Validates code quality
- Checks test coverage
- Auto-fixes issues
- Generates commit messages
- Creates GitHub PRs with context

**Example triggers:**
- "Create a pull request for spec-feature-001"
- "Ship this code"
- "Review and create PR"

### 4. debugging-issues
**Activates when:** Debugging issues, investigating errors

**What it does:**
- Systematic root cause analysis
- Error reproduction steps
- Hypothesis testing
- Fix implementation with tests

**Example triggers:**
- "Debug the login failure"
- "Investigate why the API is slow"
- "Fix the memory leak"

### 5. security-auditing
**Activates when:** Security analysis, vulnerability detection

**What it does:**
- Scans for vulnerabilities
- OWASP Top 10 checking
- Authentication/authorization review
- Input validation analysis

**Example triggers:**
- "Review this code for security issues"
- "Audit authentication security"
- "Check for SQL injection"

### 6. optimizing-performance
**Activates when:** Performance improvements, profiling

**What it does:**
- Profiles code execution
- Identifies bottlenecks
- Implements caching strategies
- Database query optimization

**Example triggers:**
- "Optimize database queries"
- "Profile the API endpoint"
- "Improve response time"

### 7. initializing-project
**Activates when:** Setting up Quaestor in projects

**What it does:**
- Auto-detects project framework
- Creates `.quaestor/specs/` structure
- Configures appropriate settings
- Adaptive setup based on project type

**Example triggers:**
- "Initialize Quaestor"
- "Setup this project"

## How Skills Work

### Automatic Activation
Skills activate based on context and keywords:

```
User says: "What's the status of spec-auth-001?"

Behind the scenes:
1. Claude detects keywords: "status", "spec"
2. managing-specifications skill activates
3. Reads .quaestor/specs/ folders
4. Calculates progress from checkboxes
5. Reports status to user

You see: "spec-auth-001: 80% complete (4/5 criteria)"
```

### Sub-Agent Orchestration
Skills coordinate multiple sub-agents internally:

**Example: implementing-features**
```
/implement spec-auth-001

Skill orchestrates:
1. researcher → analyze existing patterns
2. architect → design approach
3. implementer → write code
4. qa → create tests
5. reviewer → validate quality
```

You don't call agents directly - Skills handle all orchestration.

### Tool Restrictions
Skills have controlled tool access for safety:

- `managing-specifications`: Write, Read, Edit, Bash, Glob, Grep
- `implementing-features`: All tools (full implementation capability)
- `reviewing-and-shipping`: Read, Write, Edit, Bash, Grep, Glob
- `debugging-issues`: Read, Edit, MultiEdit, Bash, Grep, Glob
- `security-auditing`: Read, Grep, Glob, Bash, Task, WebSearch
- `optimizing-performance`: Read, Edit, Bash, Grep, Glob, Task
- `initializing-project`: Read, Write, Edit, Glob, Grep

## Benefits

**For Users:**
- Zero learning curve - just describe what you want
- No manual coordination - skills activate automatically
- Natural language interface
- Always available via plugin

**For Development:**
- Maintainable - skills are markdown files
- Composable - skills can work together
- Safe - tool restrictions prevent accidents
- Discoverable - users can read SKILL.md files

## Skills vs Sub-Agents

| Feature | Skills | Sub-Agents |
|---------|--------|-----------|
| **Activation** | Automatic (keyword-triggered) | Internal (skill-invoked) |
| **Invocation** | Natural language | Task tool by skills |
| **Purpose** | Workflow orchestration | Specialized technical work |
| **Tool access** | Restricted by allowed-tools | Determined by skill |
| **User interaction** | Direct | Indirect (via skills) |

**Key difference:** You interact with Skills, Skills orchestrate sub-agents.

## Complete Workflow Example

```
1. User: "Create a spec for user authentication"
   → managing-specifications: Creates spec in draft/

2. User: "Activate spec-auth-001"
   → managing-specifications: Moves to active/

3. User: "/implement spec-auth-001"
   → implementing-features: Orchestrates research/design/code/test/review

4. User: "What's the progress?"
   → managing-specifications: "80% complete (4/5 criteria)"

5. User: "Complete spec-auth-001"
   → managing-specifications: Moves to completed/

6. User: "Create a pull request"
   → reviewing-and-shipping: Validates quality and creates GitHub PR
```

All natural language - no commands to memorize!

## Learn More

- [/plan Command](../commands/plan.md) - Activates managing-specifications
- [/implement Command](../commands/implement.md) - Activates implementing-features
- [Sub-Agents](../agents/overview.md) - Internal agents orchestrated by skills
- [Specification-Driven Development](../specs/overview.md) - Core workflow

---

*Skills make Quaestor effortless - describe what you want, and it happens automatically.*
