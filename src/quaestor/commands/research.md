---
allowed-tools: [Task, Read, Grep, Glob, TodoWrite]
description: "Lightweight router for intelligent codebase exploration via researcher agent"
---

# /research - Codebase Exploration Router

ARGUMENTS: $QUERY

## Purpose
Routes research queries to the specialized researcher agent for comprehensive codebase exploration and analysis.

## Usage
```
/research "authentication patterns"
/research "how does the payment system work"
/research "user service dependencies"
/research "find all API endpoints"
```

## Execution

This command is a lightweight router that delegates all research to the **researcher agent** with appropriate thoroughness level.

**Primary Agent: researcher**
- Handles all codebase exploration
- Pattern analysis and discovery
- Dependency mapping
- Code understanding

**Supporting Agents (invoked by researcher when needed):**
- architect: System design analysis
- security: Security pattern review
- Other agents as appropriate for the query

## Routing Logic

### Thoroughness Level Selection

Automatically select thoroughness level based on query complexity:

**Quick (simple queries):**
```
Pattern: "find X", "where is Y", "show Z"
Thoroughness: "quick"
Time: ~2 minutes
```

**Medium (standard queries):**
```
Pattern: "how does X work", "explain Y", "understand Z"
Thoroughness: "medium"
Time: ~5 minutes
```

**Very Thorough (complex queries):**
```
Pattern: "architecture of X", "full analysis of Y", "comprehensive review"
Thoroughness: "very thorough"
Time: ~10-15 minutes
```

### Agent Invocation

**Always use Task tool with subagent_type=Explore:**
```
Task(
  subagent_type="Explore",
  description="Research [user query]",
  prompt="[Full query with context and thoroughness level]"
)
```

**Example:**
```
User: /research "authentication patterns"
→ Detect: Pattern analysis request
→ Thoroughness: "medium" (standard complexity)
→ Invoke: Task(subagent_type="Explore", prompt="Research authentication patterns in the codebase at medium thoroughness. Identify all authentication implementations, patterns used, and provide examples with file locations.")
```

## Implementation Notes

**No Direct Search:**
This command should NOT perform grep/glob operations directly. All code exploration is delegated to the Explore agent.

**Agent Handles:**
- File discovery and pattern matching
- Relevance scoring and ranking
- Context building
- Report generation
- Follow-up suggestions

**Command Responsibilities:**
1. Parse user query
2. Detect thoroughness level needed
3. Invoke Explore agent via Task tool
4. Return agent's findings to user

---
*Intelligent codebase exploration with multi-agent orchestration for deep understanding*