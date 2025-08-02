# /project-init Command

The `/project-init` command provides intelligent project initialization with automatic framework detection, architecture analysis, and adaptive setup. It analyzes your existing codebase and generates appropriate Quaestor configuration, documentation, and specifications.

## Overview

The project-init command uses multiple specialized agents for comprehensive analysis:
- **Researcher & Architect**: Project architecture and pattern analysis
- **Security Agent**: Security audit and vulnerability assessment
- **Planner Agent**: Specification generation based on project structure
- **QA Agent**: Quality standards definition and testing strategy

Project-init helps with:
- Automatic framework and technology stack detection
- Intelligent Quaestor setup based on project characteristics
- Migration from existing documentation and tools
- Generation of initial specifications and workflows

## Usage

### Basic Project Initialization
```bash
/project-init
```

Automatically analyzes the current project and sets up Quaestor:
- Detects programming language, frameworks, and architecture patterns
- Generates appropriate configuration and documentation
- Creates initial specifications based on existing code
- Sets up quality gates and development workflows

### Typed Project Initialization
```bash
/project-init --type web-api
```

Forces specific project type for targeted setup:
- Uses predefined templates for known project types
- Applies best practices for the specified architecture
- Generates type-specific specifications and documentation

### Existing Project Migration
```bash
/project-init --existing --migrate
```

Migrates existing projects to Quaestor:
- Imports existing documentation and configuration
- Preserves current development workflows
- Enhances existing setup with Quaestor capabilities
- Creates specifications from existing features

## Initialization Workflow

### Phase 1: Project Analysis 🔍

**Framework Detection:**
```yaml
Technology Stack Analysis:
  Languages: Python, Rust, JavaScript, TypeScript, Go, Java
  Frameworks: React, Django, Express, FastAPI, Spring Boot, Axum
  Architectures: MVC, Domain-Driven Design, Microservices, Monolith
  Patterns: Repository, Service Layer, CQRS, Event-Driven
```

**Agent-Orchestrated Discovery:**
The command spawns specialized agents for parallel analysis:

#### Researcher Agent Analysis
```bash
# Analyzes codebase structure and patterns
- Directory structure and organization
- Dependency analysis and technology detection  
- Code patterns and architectural decisions
- Integration points and external services
```

#### Architect Agent Analysis  
```bash
# Evaluates architecture and design patterns
- System boundaries and component relationships
- Design pattern usage and consistency
- Architecture quality and technical debt
- Scalability and maintainability assessment
```

#### Security Agent Analysis
```bash
# Performs security audit and risk assessment
- Vulnerability scanning and security patterns
- Authentication and authorization mechanisms
- Input validation and data sanitization
- Security configuration and best practices
```

### Phase 2: Intelligent Setup Generation 🔧

Based on the analysis, the command generates:

#### Configuration Files
```yaml
# .quaestor/project-config.yaml
project:
  type: "web-api"
  framework: "fastapi"
  language: "python"
  architecture: "layered"
  
development:
  testing_framework: "pytest"
  linting: "ruff"
  formatting: "black"
  
quality_gates:
  test_coverage: 85
  complexity_threshold: 10
  security_scan: true
```

#### Documentation Structure
```markdown
# Generated documentation based on project type
- ARCHITECTURE.md - System design and component overview
- API.md - API documentation (for web APIs)
- DEPLOYMENT.md - Deployment procedures and environments
- CONTRIBUTING.md - Development workflow and standards
- SECURITY.md - Security considerations and practices
```

#### Initial Specifications
```yaml
# spec-api-001.yaml - Generated from existing endpoints
id: "spec-api-001"
title: "User Authentication API"
type: "api"
status: "implemented"
description: "JWT-based authentication system"

endpoints:
  - path: "/auth/login"
    method: "POST"
    description: "User login with credentials"
  - path: "/auth/refresh"
    method: "POST" 
    description: "Refresh authentication token"

tests:
  - "test_user_login_success"
  - "test_user_login_failure"
  - "test_token_refresh"
```

### Phase 3: Quality Standards Setup 📊

**Testing Strategy:**
```yaml
# Based on detected testing framework
Testing:
  unit_tests: "pytest with fixtures"
  integration_tests: "pytest with test database"
  api_tests: "httpx client testing"
  coverage_target: 85%
  
Quality_Gates:
  pre_commit: "ruff check and format"
  ci_pipeline: "tests + security scan"
  code_review: "automated pattern checking"
```

**Development Workflow:**
```yaml
# Tailored to project characteristics  
Workflow:
  feature_development: "specification-driven"
  branch_strategy: "feature branches with PR review"
  deployment: "automated via CI/CD"
  monitoring: "logging and metrics collection"
```

### Phase 4: Agent Configuration 🤖

Sets up agent configurations based on project needs:

#### Web API Projects
```yaml
agents:
  primary: [researcher, architect, implementer, qa]
  specialized:
    - security: "for API security and authentication"
    - reviewer: "for code quality and best practices"
    
commands:
  focus: [research, plan, impl, review, debug]
  api_specific: [test-api, deploy, monitor]
```

#### Frontend Projects
```yaml
agents:
  primary: [researcher, implementer, qa, reviewer]
  specialized:
    - architect: "for component design and state management"
    - performance: "for bundle optimization and UX"
    
commands:
  focus: [research, plan, impl, review, debug]
  frontend_specific: [build, test-ui, deploy-static]
```

## Project Types

### Web API Projects
```bash
/project-init --type web-api
```

**Detected Patterns:**
- REST API endpoints with OpenAPI documentation
- Database models and migrations
- Authentication and authorization systems
- API versioning and rate limiting

**Generated Setup:**
- API documentation templates
- Endpoint testing specifications
- Security review workflows
- Performance monitoring setup

### Frontend Applications
```bash
/project-init --type frontend
```

**Detected Patterns:**
- Component-based architecture (React, Vue, Angular)
- State management (Redux, Vuex, NgRx)
- Build tools and bundlers (Webpack, Vite, Parcel)
- UI testing frameworks (Jest, Cypress, Playwright)

**Generated Setup:**
- Component documentation templates  
- UI testing specifications
- Performance optimization workflows
- Accessibility review processes

### Full-Stack Applications
```bash
/project-init --type fullstack
```

**Detected Patterns:**
- Frontend and backend integration
- Database design and ORM usage
- API client-server communication
- Authentication flow (frontend + backend)

**Generated Setup:**
- End-to-end workflow documentation
- Integration testing specifications
- Deployment pipeline configuration
- Monitoring and logging setup

### Microservices Architecture
```bash
/project-init --type microservices
```

**Detected Patterns:**
- Service communication (REST, gRPC, messaging)
- Service discovery and load balancing
- Distributed tracing and monitoring
- Data consistency and transaction patterns

**Generated Setup:**
- Service documentation templates
- Integration testing strategies
- Deployment orchestration workflows
- Distributed system monitoring

## Migration Scenarios

### From Existing Documentation
```bash
/project-init --migrate --from-docs ./docs
```

**Migration Process:**
1. Import existing README, API docs, and guides
2. Convert to Quaestor specification format
3. Generate missing documentation sections
4. Create specifications from documented features

### From Issue Trackers
```bash
/project-init --migrate --from-issues github
```

**Migration Process:**
1. Analyze GitHub issues and pull requests
2. Identify feature patterns and development workflow  
3. Generate specifications from completed features
4. Create development process documentation

### From Existing Tests
```bash
/project-init --migrate --from-tests
```

**Migration Process:**
1. Analyze test files and test patterns
2. Generate specifications from test scenarios
3. Document testing strategy and coverage
4. Create quality gate configurations

## Advanced Features

### Custom Project Templates
```yaml
# .quaestor/templates/custom-web-api.yaml
template:
  type: "custom-web-api"
  base: "web-api"
  
customizations:
  database: "postgresql"
  authentication: "oauth2"
  caching: "redis"
  messaging: "rabbitmq"
  
specifications:
  - "auth-oauth2"
  - "caching-strategy" 
  - "message-processing"
```

### Integration Detection
```yaml
# Automatically detects and configures integrations
Detected_Integrations:
  databases: ["postgresql", "redis"]
  external_apis: ["stripe", "sendgrid", "aws"]
  monitoring: ["prometheus", "grafana"]
  deployment: ["docker", "kubernetes"]
```

### Quality Metrics Setup
```yaml
# Configures quality tracking based on project
Quality_Tracking:
  code_metrics: "complexity, duplication, maintainability"
  security_metrics: "vulnerability count, compliance score"
  performance_metrics: "response time, throughput, error rate"
  test_metrics: "coverage, test count, failure rate"
```

## Best Practices

### 1. Run Early in Development
```bash
# Best: Run on new or early-stage projects
/project-init

# Good: Run when adding Quaestor to existing projects
/project-init --existing --migrate
```

### 2. Customize After Generation
After initialization, review and customize:
- Adjust quality thresholds in configuration
- Modify generated specifications as needed
- Update documentation templates for your team
- Configure agent preferences and workflows

### 3. Iterative Improvement
```bash
# Re-run periodically to update configuration
/project-init --update

# Add new project types as they're discovered
/project-init --analyze --suggest-types
```

### 4. Team Collaboration
```bash
# Generate team-specific setup
/project-init --mode team

# Create shared configuration and standards
/project-init --generate-team-config
```

## Integration with Other Commands

### After Project Initialization
```bash
# Start with research to understand the generated setup
/research "project structure and specifications"

# Create additional specifications as needed
/plan "new feature based on project architecture"

# Begin implementation with established patterns
/impl "implement feature following project standards"
```

### Updating Existing Projects
```bash
# Analyze changes and update configuration
/project-init --update --analyze-changes

# Migrate new patterns or frameworks
/project-init --migrate --detect-new-patterns
```

## Troubleshooting

### When Detection Fails
If the command can't detect your project type:
1. Use `--type` to specify the project type manually
2. Provide hints with `--framework` and `--architecture` flags
3. Use `--existing` for complex or non-standard projects
4. Check that your project has recognizable patterns and structure

### When Setup is Incorrect
If the generated setup doesn't match your needs:
1. Review and modify the generated configuration files
2. Use `--template` to specify a custom template
3. Run `--update` after making manual changes
4. Provide feedback to improve future detection

### When Migration Fails
If migration from existing tools fails:
1. Use `--migrate --force` to override conflicts
2. Manually import specific documentation sections
3. Run initialization in stages (docs first, then config)
4. Use `--dry-run` to preview changes before applying

## Next Steps

- Learn about [Specification Creation](../specs/creating.md)
- Explore [Agent Configuration](../agents/overview.md)
- Understand [Quality Gates](../advanced/quality.md)
- Read about [Project Architecture](../advanced/architecture.md)