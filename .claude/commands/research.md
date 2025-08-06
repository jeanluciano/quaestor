---
allowed-tools: [Read, Grep, Glob, Task, TodoWrite]
description: "Intelligent codebase exploration and discovery with multi-agent orchestration"

agent-strategy:
  codebase_exploration: researcher
  architecture_review: architect
  security_audit: security
  pattern_analysis: researcher
  complex_search: [researcher, architect]
---

# /research - Intelligent Discovery & Understanding

## Purpose
Explore, search, and analyze codebases to understand context, patterns, and dependencies before making changes. Leverages specialized agents for comprehensive exploration.

## Usage
```
/research "authentication patterns"
/research "how does the payment system work"
/research "user service dependencies"
/research "find all API endpoints"
```

## Auto-Intelligence

### Multi-Agent Orchestration
```yaml
Query Analysis:
  - Intent: explore|search|understand|find
  - Context: files|modules|system|patterns
  - Agents: auto-select based on query

Agent Selection:
  simple_search: researcher
  system_design: architect
  security_patterns: security
  multi_aspect: [researcher, architect, security]
```

### Smart Search Ranking
- **Relevance scoring**: File importance, modification frequency, centrality
- **Context building**: Related files, dependencies, usage patterns
- **Pattern detection**: Common implementations, conventions, anti-patterns

## Execution

**FIRST, use the workflow-coordinator agent to validate workflow state and coordinate the research phase.**

The workflow-coordinator will:
- Check if we're already in a research phase
- Initialize workflow state if needed
- Ensure proper phase progression
- Delegate to the appropriate research agents

Then follow the coordinator's guidance to:
- **Use the researcher agent** for codebase exploration and pattern analysis
- **Use the architect agent** when analyzing system design or dependencies
- **Use the security agent** when searching for security patterns or vulnerabilities

## Workflow: Analyze → Explore → Synthesize → Report

### Phase 1: Query Understanding 🎯
**Intent Classification:**
```yaml
Search Types:
  - Pattern: "How is X implemented?"
  - Architecture: "How does X connect to Y?"
  - Discovery: "What does X do?"
  - Security: "Is X secure?"
  - Performance: "Why is X slow?"
```

### Phase 2: Multi-Agent Exploration 🔍
**Parallel Agent Strategy:**
```yaml
Simple Query (1 agent):
  - Direct file search → researcher
  - Quick pattern match → researcher
  
Complex Query (2-3 agents):
  - Architecture + Implementation → [architect, researcher]
  - Security audit → [security, researcher]
  - Full analysis → [researcher, architect, security]

Agent Coordination:
  - Researcher: finds relevant code locations
  - Architect: analyzes structure and design
  - Security: identifies vulnerabilities
  - Consolidator: merges findings
```

**Search Strategies:**
- **Breadth-first**: Start with high-level structure, drill down
- **Depth-first**: Deep dive into specific modules
- **Pattern-based**: Find similar implementations across codebase
- **Dependency-driven**: Follow import/usage chains

### Phase 3: Intelligent Analysis 🧠
**Context Building:**
```yaml
File Relevance Scoring:
  - Direct matches: 100%
  - Dependencies: 80%
  - Similar patterns: 60%
  - Related tests: 40%
  - Documentation: 30%

Pattern Recognition:
  - Implementation patterns
  - Naming conventions
  - Code organization
  - Common abstractions
```

### Phase 4: Structured Reporting 📊
**Research Output Format:**
```
🔍 Research Report: [Query]

📍 Key Findings:
- Main implementation: [file:line]
- Related components: [list]
- Patterns identified: [patterns]

🏗️ Architecture Overview:
[Visual representation or description]

📂 Relevant Files (ranked by relevance):
1. auth/service.py:45 - Main authentication logic (100%)
2. auth/middleware.py:12 - Request validation (85%)
3. tests/test_auth.py:89 - Test examples (60%)

🔗 Dependencies:
- External: [libraries used]
- Internal: [modules imported]

💡 Insights:
- [Key understanding 1]
- [Key understanding 2]
- [Recommendation if applicable]

🎯 Next Steps:
- Suggested follow-up searches
- Recommended commands (/plan, /task)
```

## Search Intelligence

The research command automatically determines the appropriate search depth based on your query:

### Automatic Depth Selection
- **Simple queries** → Quick focused search (~2 min)
- **System questions** → Standard exploration (~5 min)
- **Architecture queries** → Deep analysis (~10 min)
- **Security/audit requests** → Comprehensive review (~15 min)

The system intelligently:
- Selects appropriate agents
- Determines search breadth
- Allocates time based on complexity
- Provides relevant depth of analysis

## Agent Specializations

### Researcher Agent Focus
```yaml
Responsibilities:
  - File discovery and pattern matching
  - Code reading and summarization
  - Example extraction
  - Convention identification
```

### Architect Agent Focus
```yaml
Responsibilities:
  - System design analysis
  - Dependency mapping
  - Component relationships
  - Design pattern identification
```

### Security Agent Focus
```yaml
Responsibilities:
  - Vulnerability scanning
  - Auth flow analysis
  - Input validation checks
  - Security pattern compliance
```

## Advanced Features

### Interactive Exploration
```yaml
Follow-up Queries:
  - "Show me more about X"
  - "How does this connect to Y?"
  - "Find similar patterns"
  - "Explain this in detail"
```

### Context Preservation
- Research findings documented in specification drafts
- Relevant files tracked for future commands
- Patterns documented for team reference

### Smart Suggestions
```yaml
Based on Research:
  - Architecture improvements
  - Refactoring opportunities
  - Security enhancements
  - Performance optimizations
```

## Integration with Workflow

### Handoff to Other Commands
```yaml
Research → Plan:
  - "Based on research, here's what needs planning..."
  - Context and findings passed to planning phase

Research → Task:
  - "Ready to implement with this understanding..."
  - Relevant files and patterns highlighted

Research → Debug:
  - "Found potential issue sources..."
  - Problem areas identified for debugging
```

## Success Criteria
- ✅ Query intent correctly understood
- ✅ Appropriate agents selected and coordinated
- ✅ Comprehensive results within time bounds
- ✅ Clear, actionable insights provided
- ✅ Context preserved for next steps

---
*Intelligent codebase exploration with multi-agent orchestration for deep understanding*