# Agents Overview

Quaestor's agent system provides specialized AI assistants that can be invoked through Claude Code to handle specific aspects of software development. Each agent has deep expertise in its domain and can work independently or collaborate with other agents.

## What are Agents?

Agents are specialized AI personalities with:
- **Domain Expertise**: Deep knowledge in specific areas (architecture, testing, security, etc.)
- **Focused Tools**: Access to only the tools they need
- **Quality Standards**: Specific criteria for their domain
- **Collaboration Ability**: Can work with other agents

## Core Agent Categories

### 🏗️ Development Agents

#### [Architect](architect.md)
System design and architecture specialist
- Design patterns and system architecture
- API design and contracts
- Technology selection and trade-offs
- Component boundaries and data flow

#### [Implementer](implementer.md)
Feature development and code writing specialist
- Writing production-quality code
- Following established patterns
- Implementing specifications
- Creating new components

#### [Refactorer](refactorer.md)
Code improvement and refactoring specialist
- Identifying code smells
- Applying design patterns
- Performance optimization
- Safe refactoring techniques

### 🧪 Quality Assurance Agents

#### [QA](qa.md)
Testing and quality assurance specialist
- Comprehensive test design
- Coverage analysis
- Edge case identification
- Test framework expertise

#### Debugger
Expert debugging specialist
- Root cause analysis
- Performance profiling
- Systematic debugging
- Bug fix validation

#### Reviewer
Code review specialist
- Quality assessment
- Security review
- Best practices enforcement
- Architectural consistency

### 🔍 Research & Analysis Agents

#### [Researcher](researcher.md)
Enhanced codebase analysis specialist (consolidated with former Explorer capabilities)
- Pattern analysis and system mapping
- Dependency mapping and hidden relationships
- Usage discovery and impact assessment
- Architecture visualization and documentation generation

### 🛡️ Security & Compliance

#### Security
Security analysis specialist
- Vulnerability detection
- Threat modeling
- Secure coding practices
- Security pattern implementation

#### Compliance Enforcer
Quaestor compliance specialist
- Rule enforcement
- Automated remediation
- Progress tracking
- Documentation standards

### 📊 Planning & Coordination

#### [Planner](planner.md)
Specification design specialist
- Creating specifications
- Use case analysis
- Acceptance criteria
- Project planning

#### Progress Tracker
Progress tracking specialist
- Specification lifecycle
- PR creation
- Progress reporting
- Phase completion

#### Workflow Coordinator
Workflow orchestration specialist
- Phase transitions
- Agent coordination
- Context preservation
- State management

## Agent Invocation

### Using Claude Code

Agents are invoked through the Task tool:

```python
# Direct invocation
Task(
    subagent_type="architect",
    description="Design authentication system",
    prompt="Design a JWT-based authentication system with refresh tokens..."
)
```

### Automatic Selection

Commands like `/impl` automatically select appropriate agents:

```python
/impl "add user authentication"
# Automatically uses: architect → implementer → qa
```

## Agent Collaboration Patterns

### Sequential Execution
Agents work in order, passing context:

```
researcher → architect → implementer → qa → reviewer
```

### Parallel Execution
Independent agents work simultaneously:

```
┌─ researcher: analyze patterns
├─ security: scan vulnerabilities  
└─ architect: design system
```

### Conditional Execution
Agents triggered based on findings:

```
if (complexity > 0.7):
    use architect
if (security_keywords):
    use security
```

## Best Practices

### 1. Let Commands Choose Agents
Commands like `/impl` and `/review` know which agents to use:
```bash
/impl "complex feature"  # Automatically uses multiple agents
```

### 2. Provide Clear Context
Give agents specific, detailed instructions:
```python
# Good
Task(subagent_type="architect", 
     prompt="Design REST API for user management with JWT auth, 
             considering scalability for 100k users")

# Too vague
Task(subagent_type="architect", 
     prompt="Design API")
```

### 3. Use Agent Strengths
Each agent excels at specific tasks:
- **Architect**: System design, not implementation details
- **Implementer**: Writing code, not designing systems
- **QA**: Testing strategies, not fixing bugs

### 4. Chain Agents Appropriately
Common successful patterns:
- **Feature Development**: architect → implementer → qa
- **Bug Fixing**: debugger → implementer → qa
- **Refactoring**: researcher → refactorer → qa
- **Security Review**: security → implementer (for fixes)

## Agent Configuration

Agents respect your project settings:

```json
{
  "agent_preferences": {
    "preferred_agents": ["implementer", "qa"],
    "complexity_threshold": 0.5,
    "parallel_execution": true
  }
}
```

## Performance Considerations

- **Timeout**: Default 30 seconds per agent
- **Parallel Limit**: Max 4 agents simultaneously
- **Context Size**: Agents share context efficiently
- **Fallback**: Graceful degradation on failures

## Next Steps

- Explore individual [agent documentation](planner.md)
- Learn about [Commands](../commands/plan.md) that use agents
- Understand [Hooks](../hooks/overview.md) that coordinate agents
- Read about [Specification-Driven Development](../specs/overview.md)