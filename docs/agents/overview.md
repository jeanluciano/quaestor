# Agents Overview

Quaestor uses specialized sub-agents internally within Skills to handle specific development tasks. These agents are not invoked directly - instead, Skills automatically delegate to the appropriate agents based on the task at hand.

## What are Sub-Agents?

Sub-agents are specialized AI assistants with:
- **Domain Expertise**: Deep knowledge in specific areas (architecture, testing, security, etc.)
- **Focused Tools**: Access to only the tools they need
- **Quality Standards**: Specific criteria for their domain
- **Automatic Invocation**: Called by Skills, not by users directly

## Available Sub-Agents

Quaestor includes 10 specialized sub-agents used internally by Skills:

### 🏗️ Development Sub-Agents

**architect** - System design and architecture specialist
- Design patterns and system architecture
- API design and contracts
- Technology selection and trade-offs
- Component boundaries and data flow

**implementer** - Feature development and code writing specialist
- Writing production-quality code
- Following established patterns
- Implementing specifications
- Creating new components

**refactorer** - Code improvement and refactoring specialist
- Identifying code smells
- Applying design patterns
- Performance optimization
- Safe refactoring techniques

### 🧪 Quality Assurance Sub-Agents

**qa** - Testing and quality assurance specialist
- Comprehensive test design
- Coverage analysis
- Edge case identification
- Test framework expertise

**debugger** - Expert debugging specialist
- Root cause analysis
- Performance profiling
- Systematic debugging
- Bug fix validation

**reviewer** - Code review specialist
- Quality assessment
- Security review
- Best practices enforcement
- Architectural consistency

### 🔍 Research & Analysis Sub-Agents

**researcher** - Codebase analysis specialist
- Pattern analysis and system mapping
- Dependency mapping and hidden relationships
- Usage discovery and impact assessment
- Architecture visualization and documentation generation

### 🛡️ Security Sub-Agent

**security** - Security analysis specialist
- Vulnerability detection
- Threat modeling
- Secure coding practices
- Security pattern implementation

### 📊 Planning & Coordination Sub-Agents

**planner** - Specification design specialist
- Creating specifications
- Use case analysis
- Acceptance criteria
- Project planning

**workflow-coordinator** - Workflow orchestration specialist
- Phase transitions
- Agent coordination
- Context preservation
- State management

## How Sub-Agents Work

Sub-agents are invoked internally by Skills using the Task tool. You don't call them directly - Skills handle all agent orchestration.

### Example: implementing-features Skill

When you use `/implement`, the implementing-features skill automatically:

1. Uses **researcher** to analyze existing code patterns
2. Uses **architect** to design the technical approach
3. Uses **implementer** to write production code
4. Uses **qa** to create comprehensive tests
5. Uses **reviewer** to validate code quality

### Example: debugging-issues Skill

When you say "debug the login issue", the debugging-issues skill:

1. Uses **debugger** to perform root cause analysis
2. Uses **implementer** to fix the issue
3. Uses **qa** to create regression tests

## Agent Collaboration Patterns

Skills orchestrate agents in various patterns:

**Sequential Execution** - Agents work in order, passing context:
```
researcher → architect → implementer → qa → reviewer
```

**Parallel Execution** - Independent agents work simultaneously:
```
┌─ researcher: analyze patterns
├─ security: scan vulnerabilities
└─ architect: design system
```

**Conditional Execution** - Agents triggered based on findings:
```
if (complexity > 0.7):
    use architect
if (security_keywords):
    use security
```

## Sub-Agent Specializations

Each sub-agent excels at specific tasks:
- **architect**: System design, not implementation details
- **implementer**: Writing code, not designing systems
- **qa**: Testing strategies, not fixing bugs
- **debugger**: Root cause analysis, not feature development
- **reviewer**: Code quality assessment, not implementation
- **researcher**: Codebase analysis, not code writing
- **security**: Vulnerability detection, not general review
- **planner**: Specification creation, not implementation
- **refactorer**: Code improvement, not new features
- **workflow-coordinator**: Process orchestration, not technical work

## Next Steps

- Learn about [Skills](../skills/overview.md) that orchestrate agents
- Explore [Commands](../commands/plan.md) that activate Skills
- Read about [Specification-Driven Development](../specs/overview.md)