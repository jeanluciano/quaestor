# Quaestor Architecture

## Architecture Overview

```yaml
pattern:
  selected: "Service-Oriented Architecture with Manager Pattern"
  description: "Quaestor uses a layered architecture with service/manager components handling business logic, anemic domain models for data representation, and clear separation between CLI, core services, and utilities"
```

### Architecture Pattern Details

```yaml
layers:
  - name: "CLI Layer"
    path: "src/quaestor/cli"
    description: "Command-line interface using Typer framework"
    components:
      - type: "Commands"
        description: "CLI command handlers (init, configure, update, etc.)"
      - type: "Command Processor"
        description: "Template-based command generation system"
  
  - name: "Core Services Layer"
    path: "src/quaestor/core"
    description: "Business logic and domain services"
    components:
      - type: "Managers"
        description: "Service components (SpecificationManager, FolderManager)"
      - type: "Data Models"
        description: "Dataclass-based entities (Specification, Contract, etc.)"
      - type: "Project Analysis"
        description: "Code analysis and pattern detection services"
  
  - name: "Claude Integration Layer"
    path: "src/quaestor/claude"
    description: "AI assistant integration and hook system"
    components:
      - type: "Hooks"
        description: "Event-driven hooks for Claude integration"
      - type: "Agents"
        description: "Specialized AI agent configurations"
      - type: "Templates"
        description: "Command and documentation templates"
  
  - name: "Utilities Layer"
    path: "src/quaestor/utils"
    description: "Shared utilities and infrastructure"
    components:
      - type: "File Operations"
        description: "Safe file I/O with atomic operations"
      - type: "YAML Processing"
        description: "YAML serialization/deserialization"
      - type: "Console Output"
        description: "Rich terminal UI components"
```

## Core Concepts

```yaml
components:
  - name: "SpecificationManager"
    responsibility: "Manages the lifecycle of specifications from draft to completion"
    dependencies: ["FolderManager", "YAML utilities"]
  - name: "FolderManager"
    responsibility: "Handles atomic folder operations and enforces active specification limits"
    dependencies: ["File utilities", "Platform-specific locking"]
  - name: "ProjectAnalyzer"
    responsibility: "Analyzes project structure and generates context-aware rules"
    dependencies: ["File system operations", "Pattern detection"]
  - name: "CommandProcessor"
    responsibility: "Processes and generates Claude-compatible commands from templates"
    dependencies: ["Template engine", "YAML processing"]
  - name: "Hook System"
    responsibility: "Provides extensible integration points for Claude AI"
    dependencies: ["Base hook class", "Mode detection"]
```

```yaml
concepts:
  - name: "Specification"
    description: "Core unit of work representing a feature, bugfix, or other development task"
    related_to: ["Contract", "TestScenario", "SpecStatus"]
  - name: "Specification Lifecycle"
    description: "Workflow from draft → active → completed with enforced limits"
    related_to: ["FolderManager", "SpecStatus", "Git integration"]
  - name: "Hook"
    description: "Extension point for Claude AI integration with mode-aware behavior"
    related_to: ["Drive mode", "Framework mode", "Command processing"]
  - name: "Project Context"
    description: "Analyzed project information used for rule generation and AI guidance"
    related_to: ["ProjectAnalyzer", "RULES.md", "Team/Personal modes"]
```

```yaml
rules:
  - id: "active_spec_limit"
    description: "Maximum of 3 active specifications to maintain focus"
    enforcement: "FolderManager.enforce_active_limit() prevents exceeding limit"
  - id: "atomic_operations"
    description: "All file operations must be atomic with rollback capability"
    enforcement: "File utilities provide atomic write operations with backups"
  - id: "yaml_serialization"
    description: "All data persistence uses YAML format for human readability"
    enforcement: "Consistent use of yaml_utils for all serialization"
```

## External Integrations

```yaml
services:
  - name: "Claude AI"
    purpose: "AI-powered development assistance and code generation"
    api_type: "Hook-based integration"
    authentication: "N/A - Local hook system"
  - name: "Git"
    purpose: "Version control integration for branch mapping and status"
    api_type: "Command-line subprocess"
    authentication: "System git credentials"
```

```yaml
internal:
  - name: "Hook System"
    purpose: "Extensible integration points for Claude AI"
    protocol: "Python method calls with standardized signatures"
  - name: "Template Engine"
    purpose: "Generate context-aware commands and documentation"
    protocol: "String template processing with variable substitution"
```

## Code Organization

```yaml
structure:
  - path: "src/"
    contains:
      - path: "quaestor/"
        description: "Main package root"
        subdirs:
          - path: "cli/"
            description: "CLI commands and interface"
          - path: "core/"
            description: "Core business logic and services"
          - path: "utils/"
            description: "Shared utilities and helpers"
          - path: "claude/"
            description: "Claude AI integration"
            subdirs:
              - path: "hooks/"
                description: "Hook implementations"
              - path: "agents/"
                description: "AI agent configurations"
              - path: "commands/"
                description: "Command templates"
              - path: "templates/"
                description: "Documentation templates"
  - path: "tests/"
    contains:
      - path: "unit/"
        description: "Unit tests for individual components"
      - path: "integration/"
        description: "Integration tests"
      - path: "e2e/"
        description: "End-to-end tests"
      - path: "performance/"
        description: "Performance benchmarks"
  - path: ".quaestor/"
    contains:
      - path: "specs/"
        description: "Specification storage"
        subdirs:
          - path: "draft/"
            description: "Draft specifications"
          - path: "active/"
            description: "Active specifications (max 3)"
          - path: "completed/"
            description: "Completed specifications"
```

```yaml
organization_patterns:
  - type: "Service-based"
    description: "Services/Managers handle business logic with data models"
    when_to_use: "Current pattern - works well for CLI tools"
```

## Data Flow

```yaml
request_flow:
  - step: 1
    name: "CLI Command"
    description: "User executes quaestor command via terminal"
    components_involved: ["Typer", "CLI commands"]
  - step: 2
    name: "Command Processing"
    description: "Command handler validates input and delegates to services"
    components_involved: ["Command handlers", "Input validation"]
  - step: 3
    name: "Service Execution"
    description: "Managers/services execute business logic"
    components_involved: ["SpecificationManager", "FolderManager", "ProjectAnalyzer"]
  - step: 4
    name: "Data Persistence"
    description: "Changes persisted to YAML files atomically"
    components_involved: ["YAML utilities", "File operations"]
  - step: 5
    name: "Response Display"
    description: "Rich terminal output displayed to user"
    components_involved: ["Rich console", "Progress indicators"]
```

```yaml
storage:
  primary_database:
    type: "File-based YAML"
    purpose: "Store specifications and configuration"
    connection_pool: false
  cache_layer:
    type: "None"
    purpose: "N/A - Direct file access"
    ttl: "N/A"
  file_storage:
    type: "Local filesystem"
    purpose: "All data storage (specs, config, logs)"
    location: ".quaestor/ directory"
  message_queue:
    type: "None"
    purpose: "N/A - Synchronous processing"
    retention: "N/A"
```

## Communication Patterns

```yaml
internal:
  patterns:
    - type: "Synchronous"
      description: "Direct method calls between components"
      use_cases: ["All internal operations"]
    - type: "Hook-based"
      description: "Extension points for Claude integration"
      event_bus: "Python method dispatch"
```

```yaml
external:
  patterns:
    - type: "CLI"
      description: "Command-line interface via Typer"
      authentication: "None - local tool"
      rate_limiting: "None required"
```

## Security Considerations

```yaml
authentication:
  method: "None - local CLI tool"
  token_expiry: "N/A"
  refresh_strategy: "N/A"

authorization:
  model: "File system permissions"
  permission_check: "OS-level file access"
  
data_security:
  encryption_at_rest: "No - relies on OS encryption"
  encryption_in_transit: "N/A - local only"
  sensitive_data_handling: "No sensitive data stored"
  compliance: "N/A - development tool"

security_issues:
  - issue: "Command injection in git operations"
    severity: "High"
    mitigation: "Input validation needed for subprocess calls"
  - issue: "Path traversal in file operations"
    severity: "High"
    mitigation: "Strengthen path validation with symlink checks"
```

## Performance & Scalability

```yaml
caching:
  levels:
    - level: "None"
      what_cached: "N/A - Direct file access"
      ttl: "N/A"
  invalidation:
    strategy: "N/A"
    description: "No caching layer"

performance_concerns:
  - concern: "YAML parsing on every operation"
    impact: "Medium"
    mitigation: "Consider caching parsed YAML"
  - concern: "Large file operations"
    impact: "Low"
    mitigation: "Files typically small"
```

```yaml
scaling:
  horizontal:
    enabled: "No"
    auto_scaling: "N/A"
    metrics: "N/A"
  vertical:
    enabled: "N/A - Local tool"
    limits: "System resources"
  load_balancing:
    strategy: "N/A"
    health_checks: "N/A"
  database_scaling:
    read_replicas: "No"
    sharding: "No"
    strategy: "N/A - File-based storage"
```

## Development Guidelines

```yaml
principles:
  - name: "Separation of Concerns"
    description: "Clear layer boundaries between CLI, services, and utilities"
  - name: "Single Responsibility"
    description: "Each manager/service has one clear purpose"
  - name: "Explicit Over Implicit"
    description: "Clear method names and type hints throughout"
```

```yaml
standards:
  - rule: "Manager pattern for business logic"
    reason: "Centralized logic in service components"
  - rule: "Dataclasses for data models"
    reason: "Clean, type-safe data structures"
  - rule: "Atomic file operations"
    reason: "Prevent data corruption"
  - rule: "Type hints on all functions"
    coverage_target: "100%"
  - rule: "Comprehensive error handling"
    format: "Try-except with user-friendly messages"
```

```yaml
testing_standards:
  framework: "pytest"
  structure:
    - type: "Unit tests"
      location: "tests/unit/"
      coverage_target: "80%"
    - type: "Integration tests"
      location: "tests/integration/"
      focus: "Component interactions"
    - type: "E2E tests"
      location: "tests/e2e/"
      focus: "Full command workflows"
    - type: "Performance tests"
      location: "tests/performance/"
      focus: "Operation benchmarks"
```

## Deployment Architecture

```yaml
environments:
  - name: "Development"
    description: "Local development environment"
    url: "N/A - Local CLI"
    deployment: "pip install -e ."
  - name: "Production"
    description: "PyPI package distribution"
    url: "https://pypi.org/project/quaestor/"
    deployment: "GitHub Actions on release"
```

```yaml
infrastructure:
  hosting:
    provider: "PyPI"
    services: "Package hosting"
    regions: "Global CDN"
  ci_cd:
    pipeline: "GitHub Actions"
    stages: ["Test", "Build", "Publish"]
    triggers: ["Push to main", "Pull requests", "Release tags"]
  monitoring:
    apm: "None - CLI tool"
    logging: "Local .quaestor/logs/"
    alerting: "None required"
```

---
*This document describes the technical architecture of Quaestor. Generated by project-init based on codebase analysis.*