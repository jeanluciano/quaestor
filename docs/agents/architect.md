# Architect Agent

The Architect agent is a senior software architect specializing in system design, architectural patterns, and strategic technical decisions. It designs robust, scalable, and maintainable solutions while considering both immediate needs and long-term implications.

## Core Capabilities

### System Architecture
- Designs comprehensive system architectures
- Creates component diagrams and data flow models
- Defines service boundaries and interfaces
- Plans microservices and distributed systems
- Designs for scalability and resilience

### API Design
- Creates RESTful API specifications
- Designs GraphQL schemas
- Defines API contracts and versioning strategies
- Plans authentication and authorization flows
- Considers rate limiting and caching strategies

### Pattern Application
- Applies appropriate design patterns
- Recommends architectural patterns (MVC, CQRS, Event-Driven)
- Suggests refactoring strategies
- Identifies anti-patterns
- Ensures SOLID principles

### Technology Selection
- Evaluates technology options
- Performs trade-off analysis
- Considers team expertise
- Assesses long-term maintenance
- Plans migration strategies

## When to Use

The Architect agent excels at:
- **System design** for new features or services
- **Refactoring planning** for legacy systems
- **Technology decisions** and evaluations
- **Performance optimization** strategies
- **Integration design** between systems
- **Security architecture** planning

## Design Process

### Phase 1: Requirements Analysis
```yaml
analysis:
  - Understand functional requirements
  - Identify non-functional requirements
  - Determine constraints and assumptions
  - Analyze existing architecture
  - Consider future scalability needs
```

### Phase 2: Solution Design
```yaml
design:
  - Component identification and boundaries
  - Interface definition and contracts
  - Data flow modeling and storage design
  - Integration planning and API design
  - Security and performance considerations
```

### Phase 3: Validation
```yaml
validation:
  - Trade-off analysis of options
  - Risk assessment and mitigation
  - Implementation planning and phases
  - Documentation and diagrams
  - Review with stakeholders
```

## Architecture Artifacts

### Component Diagrams
```
┌─────────────────┐     ┌─────────────────┐
│   Web Client    │────▶│   API Gateway   │
└─────────────────┘     └────────┬────────┘
                                 │
                    ┌────────────┴────────────┐
                    ▼                         ▼
          ┌─────────────────┐       ┌─────────────────┐
          │   Auth Service  │       │  User Service   │
          └────────┬────────┘       └────────┬────────┘
                   │                         │
                   └────────────┬────────────┘
                                ▼
                        ┌─────────────────┐
                        │    Database     │
                        └─────────────────┘
```

### Design Decisions
The Architect documents key decisions:

```markdown
## Decision: Authentication Strategy

### Context
Need secure, scalable authentication for 100k+ users

### Decision
JWT-based authentication with refresh tokens

### Rationale
- Stateless and scalable
- Works well with microservices
- Standard implementation available

### Trade-offs
- Token size larger than session IDs
- Requires careful key management
- Cannot revoke tokens instantly

### Alternatives Considered
1. Session-based auth - Not scalable enough
2. OAuth2 - Overkill for internal use
3. API Keys - Not suitable for user auth
```

## Architectural Patterns

### Microservices Architecture
When designing distributed systems:
- Service boundaries based on business domains
- API gateway for unified entry point
- Service discovery and load balancing
- Distributed tracing and monitoring
- Event-driven communication

### Event-Driven Architecture
For loosely coupled systems:
- Event sourcing for audit trails
- CQRS for read/write separation
- Message queues for reliability
- Event schema evolution
- Idempotency patterns

### Layered Architecture
For monolithic applications:
- Clear separation of concerns
- Dependency injection
- Repository pattern
- Service layer abstraction
- Clean architecture principles

## Integration with Other Agents

### With Planner
- Reviews specification feasibility
- Suggests technical approaches
- Estimates complexity accurately
- Identifies technical risks

### With Implementer
- Provides implementation guidance
- Reviews code architecture
- Suggests patterns to follow
- Validates implementation approach

### With Security
- Designs secure architectures
- Plans authentication/authorization
- Reviews data flow security
- Suggests encryption strategies

## Best Practices

### Design Principles
1. **Simplicity First**: Start simple, evolve as needed
2. **Loose Coupling**: Minimize dependencies between components
3. **High Cohesion**: Keep related functionality together
4. **Open/Closed**: Open for extension, closed for modification
5. **DRY**: Don't repeat yourself, but don't over-abstract

### Documentation Standards
- Always create visual diagrams
- Document key decisions with ADRs
- Include example API calls
- Provide implementation notes
- Consider failure scenarios

### Performance Considerations
- Design for horizontal scaling
- Plan caching strategies
- Optimize database queries
- Consider async processing
- Monitor performance metrics

## Common Architecture Solutions

### Authentication System
```yaml
Components:
  - API Gateway: Route and authenticate requests
  - Auth Service: Handle login/logout/refresh
  - User Service: Manage user data
  - Token Store: Redis for refresh tokens

Flow:
  1. Client → API Gateway → Auth Service
  2. Auth Service validates credentials
  3. Generate JWT + Refresh token
  4. Store refresh token in Redis
  5. Return tokens to client
```

### File Processing Pipeline
```yaml
Components:
  - Upload Service: Accept file uploads
  - Queue: Process files asynchronously
  - Worker Pool: Parallel processing
  - Storage: S3 or similar
  - Notification: Webhook on completion

Patterns:
  - Queue for reliability
  - Workers for scalability
  - Checkpointing for resumability
  - Dead letter queue for failures
```

## Configuration

Customize architect behavior:

```json
{
  "agent_preferences": {
    "architect": {
      "diagram_style": "mermaid",
      "include_alternatives": true,
      "max_complexity": "high",
      "focus_areas": ["scalability", "security"]
    }
  }
}
```

## Quality Standards

The Architect ensures:
- **Scalability**: Can handle 10x growth
- **Maintainability**: Easy to understand and modify
- **Testability**: Components can be tested in isolation
- **Security**: Defense in depth approach
- **Performance**: Meet response time requirements
- **Reliability**: 99.9% uptime capability

## Anti-Patterns to Avoid

1. **Big Ball of Mud**: No clear architecture
2. **God Object**: One component does everything
3. **Spaghetti Code**: Tangled dependencies
4. **Golden Hammer**: One solution for everything
5. **Premature Optimization**: Optimizing too early
6. **Analysis Paralysis**: Over-designing

## Next Steps

- Learn about the [Implementer Agent](implementer.md) for building designs
- Explore the [QA Agent](qa.md) for testing strategies
- Understand [System Architecture](../advanced/architecture.md)
- Read about [API Design Best Practices](../advanced/api-design.md)