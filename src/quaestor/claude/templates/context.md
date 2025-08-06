<!-- META:document:claude-context -->
<!-- META:priority:MAXIMUM -->
<!-- META:enforcement:MANDATORY -->
<!-- QUAESTOR:version:1.0 -->

# CLAUDE CONTEXT - QUAESTOR AI DEVELOPMENT FRAMEWORK

## 1. CRITICAL ENFORCEMENT

<!-- SECTION:enforcement:validations:START -->
### ⚠️ AUTOMATIC ENFORCEMENT CHECKS

<!-- DATA:pre-action-validations:START -->
```yaml
before_any_action:
  mandatory_checks:
    - id: "workflow_compliance"
      check: "Is Research → Plan → Implement sequence being followed?"
      on_violation: "STOP and say: 'I need to research first before implementing'"
    
    - id: "clarification_needed"
      check: "Am I making assumptions instead of asking for clarification?"
      on_violation: "STOP and ask for clarification"
    
    - id: "complexity_check"
      check: "Is this becoming overly complex?"
      triggers:
        - more_than_100_lines_in_single_function
        - nested_depth_exceeds_3
        - circular_dependencies_detected
      on_violation: "STOP and say: 'This seems complex. Let me step back and ask for guidance'"
    
    - id: "production_quality"
      check: "Does this meet production standards?"
      requires:
        - error_handling
        - input_validation
        - test_coverage
        - documentation
      on_violation: "ADD missing requirements before proceeding"
    
    - id: "specification_tracking_compliance"
      check: "Am I tracking my work in the specification system?"
      required_actions:
        - check_active_specifications: ".quaestor/specs/*.yaml"
        - declare_work_context: "Which specification am I working on?"
        - update_progress: "Mark completed tasks and update progress"
        - document_completion: "Update specification phase status"
      on_violation: "STOP and say: 'Let me check the current specification and declare which task I'm working on'"
```
<!-- DATA:pre-action-validations:END -->
<!-- SECTION:enforcement:validations:END -->

### 🔴 IMMUTABLE RULES

<!-- DATA:rule-definitions:START -->
```yaml
immutable_rules:
  - rule_id: "NEVER_SKIP_RESEARCH"
    priority: "CRITICAL"
    description: "ALWAYS research before implementing"
    enforcement:
      trigger: "Any implementation request"
      required_response: "Let me research the codebase and create a plan before implementing."
      validation: "Must show evidence of codebase exploration"
    
  - rule_id: "ALWAYS_USE_AGENTS"
    priority: "CRITICAL"
    description: "Use multiple agents for complex tasks"
    enforcement:
      trigger: "Task with multiple components"
      required_response: "I'll spawn agents to tackle different aspects of this problem"
      validation: "Must delegate to at least 2 agents for complex tasks"
    
  - rule_id: "ASK_DONT_ASSUME"
    priority: "CRITICAL"
    description: "Ask for clarification instead of making assumptions"
    enforcement:
      trigger: "Uncertainty detected"
      required_response: "I need clarification on [specific aspect]"
      validation: "No assumptions in implementation"
    
  - rule_id: "PRODUCTION_QUALITY_ONLY"
    priority: "CRITICAL"
    description: "All code must be production-ready"
    enforcement:
      required_elements:
        - comprehensive_error_handling
        - input_validation  
        - edge_case_handling
        - proper_logging
        - test_coverage
      validation: "Code review checklist must pass"
  
  - rule_id: "MANDATORY_SPECIFICATION_TRACKING"
    priority: "CRITICAL"
    description: "ALL work must be tracked in the specification system"
    enforcement:
      before_starting:
        - check: ".quaestor/specs/ for active specification"
        - declare: "Working on: [Phase] > [Task] > [Subtask]"
        - update: "task status to 'in_progress'"
      during_work:
        - track: "Files created and modified"
        - note: "Key decisions and deviations"
      after_completing:
        - mark: "completed subtasks with '# COMPLETED'"
        - update: "progress percentage in tasks.yaml"
        - document: "progress in specification files"
      validation: "Specification files must be updated with progress"
```
<!-- DATA:rule-definitions:END -->

## 2. MANDATORY WORKFLOW

<!-- WORKFLOW:research-plan-implement:START -->
### 📋 Research → Plan → Implement

```yaml
mandatory_workflow:
  name: "Research → Plan → Implement"
  steps:
    - step: 1
      name: "RESEARCH"
      required_actions:
        - scan_codebase:
            targets: ["existing patterns", "similar implementations", "dependencies"]
            minimum_files_examined: 5
        - analyze_patterns:
            identify: ["naming conventions", "architectural patterns", "testing approach"]
        - document_findings:
            format: "structured_summary"
      validation:
        must_output: "Research findings summary"
        must_identify: "At least 3 existing patterns"
    
    - step: 2
      name: "PLAN"
      required_actions:
        - create_implementation_plan:
            include: ["step-by-step approach", "files to modify", "test strategy"]
        - identify_risks:
            consider: ["breaking changes", "performance impact", "edge cases"]
        - get_user_approval:
            present: "Detailed plan for review"
      validation:
        must_output: "Structured implementation plan"
        must_receive: "User approval before proceeding"
    
    - step: 3
      name: "IMPLEMENT"
      required_actions:
        - follow_plan:
            deviation_allowed: "Only with user approval"
        - validate_continuously:
            after_each: ["function implementation", "file modification"]
        - maintain_quality:
            ensure: ["tests pass", "no linting errors", "documentation updated"]
      validation:
        must_complete: "All planned items"
        must_pass: "All quality checks"
```
<!-- WORKFLOW:research-plan-implement:END -->

### 🤖 Agent Orchestration Requirements

<!-- DATA:agent-triggers:START -->
```yaml
must_use_agents_when:
  - trigger: "Multiple files need analysis"
    delegation:
      - agent_1: "Analyze models and database schema"
      - agent_2: "Analyze API endpoints and routes"
      - agent_3: "Analyze tests and coverage"
    
  - trigger: "Complex refactoring required"
    delegation:
      - agent_1: "Identify all affected code"
      - agent_2: "Create refactoring plan"
      - agent_3: "Implement changes"
      - agent_4: "Update tests"
    
  - trigger: "New feature implementation"
    delegation:
      - agent_1: "Research similar features"
      - agent_2: "Design implementation"
      - agent_3: "Write tests"
      - agent_4: "Implement feature"
    
  - trigger: "Performance optimization"
    delegation:
      - agent_1: "Profile current performance"
      - agent_2: "Identify bottlenecks"
      - agent_3: "Research optimization strategies"
      - agent_4: "Implement improvements"
```
<!-- DATA:agent-triggers:END -->

### 🚨 Complexity Management

<!-- DATA:complexity-detection:START -->
```yaml
stop_and_ask_when:
  code_complexity:
    - function_lines: "> 50"
      action: "STOP: Break into smaller functions"
    - cyclomatic_complexity: "> 10"
      action: "STOP: Simplify logic"
    - nested_depth: "> 3"
      action: "STOP: Refactor to reduce nesting"
  
  architectural_complexity:
    - circular_dependencies: "detected"
      action: "STOP: Ask for architectural guidance"
    - god_objects: "detected"
      action: "STOP: Discuss splitting responsibilities"
    - unclear_patterns: "detected"
      action: "STOP: Request pattern clarification"
  
  implementation_uncertainty:
    - multiple_valid_approaches: true
      action: "STOP: Present options and ask preference"
    - performance_implications: "unclear"
      action: "STOP: Discuss tradeoffs"
    - security_concerns: "possible"
      action: "STOP: Highlight concerns and get guidance"
```
<!-- DATA:complexity-detection:END -->

### 🧠 Ultrathink Requirements

<!-- DATA:ultrathink-requirements:START -->
```yaml
must_ultrathink_for:
  - architectural_decisions:
      examples:
        - "Choosing between microservices vs monolith"
        - "Designing API structure"
        - "Database schema design"
      required_output: "Comprehensive analysis with tradeoffs"
  
  - complex_algorithms:
      examples:
        - "Optimization problems"
        - "Distributed system coordination"
        - "Complex data transformations"
      required_output: "Multiple approaches with complexity analysis"
  
  - security_implementations:
      examples:
        - "Authentication systems"
        - "Data encryption strategies"
        - "Access control design"
      required_output: "Security analysis and threat modeling"
  
  - performance_critical:
      examples:
        - "High-throughput systems"
        - "Real-time processing"
        - "Large-scale data handling"
      required_output: "Performance analysis and benchmarks"
```
<!-- DATA:ultrathink-requirements:END -->

## 3. PROJECT CONTEXT

### Project Information
- **Quaestor**: AI context management framework for development teams
- **Core Purpose**: Maintain project memory, enforce development standards, and orchestrate AI agents
- **Architecture**: Plugin-based system with hooks, templates, and agent coordination

### Development Approach
- **Production Quality**: All code must be production-ready with comprehensive error handling
- **Automated Assistance**: Hooks provide helpful automation for common tasks
- **Contextual Rules**: Generate appropriate rules based on project complexity analysis
- **Agent Orchestration**: Use multiple agents for complex tasks to improve outcomes

### Key Components
- **Template System**: Manages project documentation and context templates
- **Hook System**: Provides automated assistance and workflow enhancements
- **Agent System**: Coordinates specialized AI agents for different tasks
- **Specification Tracking**: Tracks work progress against project specifications

### Code Style Guidelines
- **Language**: {{ language_display_name }}{% if primary_language != "unknown" %} ({{ primary_language }}){% endif %}
- **Formatting**: {{ code_formatter }}
- **Linting**: {{ lint_command }}
- **Testing**: {{ testing_framework }}
- **Documentation**: {{ documentation_style }}
- **Error Handling**: Comprehensive exception handling with proper logging
- **File Organization**: {{ file_organization }}
- **Naming Convention**: {{ naming_convention }}

### Architecture Patterns
- **Dependency Injection**: Use for testability and modularity
- **Plugin Architecture**: Extensible hook and agent systems
- **Template Processing**: Dynamic content generation with context awareness
- **Configuration Management**: Layered configuration with validation

## 4. SYSTEM INTEGRATION

### Hook System Features

<!-- SECTION:hook-features:START -->
**Helpful Automation**: Hooks provide automated assistance to enhance your development workflow.

#### Available Hooks
- **Context Hook**: `session_context_loader.py` - Automatically loads active specifications into your session
- **Progress Hook**: `todo_spec_progress.py` - Automatically updates specification progress when TODOs are completed

#### How Hooks Help You
1. **Automatic Context Loading**: Active specs are loaded at session start
2. **Progress Tracking**: Spec progress updates automatically as you complete TODOs
3. **No Manual Updates Needed**: Hooks handle routine updates in the background

#### Hook Output
- Hooks may provide helpful suggestions or status updates
- Their output is informational to help guide your work
- You can use hook suggestions to improve your workflow
<!-- SECTION:hook-features:END -->

### Specification Tracking System

<!-- DATA:specification-requirements:START -->
```yaml
specification_tracking_mandatory:
  before_any_work:
    step_1_check_specifications:
      - action: "Read all .quaestor/specs/*.yaml files"
      - action: "Find tasks.yaml files with status: 'in_progress'"
      - action: "Identify which phase/task/subtask relates to this work"
    
    step_2_declare_context:
      - format: "Working on: [Phase] > [Task] > [Subtask]"
      - example: "Working on: Phase 1 > vector_store > Create VectorStore abstraction"
      - required: "Must announce context before starting"
    
    step_3_update_status:
      - if_new_task: "Update status to 'in_progress' in tasks.yaml"
      - if_continuing: "Confirm current status and progress"
      - required: "Task must be marked as active"

  during_work:
    track_progress:
      - what: "Files created or modified"
      - what: "Tests added or updated"
      - what: "Key implementation decisions"
      - what: "Any deviations from original plan"

  after_completing_work:
    mandatory_updates:
      - mark_subtasks: "Add '# COMPLETED' to finished subtasks"
      - update_progress: "Update progress percentage"
      - update_phases: "Mark phases as completed when done"
      - document_notes: "Add implementation details and decisions"
```
<!-- DATA:specification-requirements:END -->

### Available Commands
- **project-init.md**: Analyze and initialize Quaestor framework
- **research.md**: Intelligent codebase exploration
- **plan.md**: Strategic planning and progress management
- **impl.md**: Implementation with agent orchestration
- **debug.md**: Interactive debugging and troubleshooting
- **review.md**: Comprehensive review and validation

### Git Integration
- **Atomic Commits**: Each completed task gets its own commit
- **Specification Branches**: Work organized by specification
- **Quality Standards**: Pre-commit validation for code quality

## 5. REFERENCE

### Quality Gates

<!-- DATA:quality-requirements:START -->
```yaml
before_considering_complete:
  code_quality:
    - tests_written: true
    - tests_passing: true
    - edge_cases_handled: true
    - error_handling_complete: true
    - input_validation_present: true
    - documentation_updated: true
  
  review_checklist:
    - follows_existing_patterns: true
    - no_code_duplication: true
    - proper_abstraction_level: true
    - performance_acceptable: true
    - security_reviewed: true
    - maintainable_code: true
  
  final_validation:
    - would_deploy_to_production: true
    - colleague_could_understand: true
    - handles_failure_gracefully: true
```
<!-- DATA:quality-requirements:END -->

### Testing Approach
- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions
- **E2E Tests**: Test complete workflows
- **Coverage**: Maintain >80% test coverage
- **Quality**: Use pytest with fixtures and parameterization

### Troubleshooting
- **Hook Configuration**: Check .claude/settings.json for hook setup
- **Template Problems**: Verify template syntax and placeholders
- **Agent Coordination**: Ensure proper agent delegation patterns
- **Specification Tracking**: Validate .quaestor/specs/ structure

### Enforcement Consequences

<!-- DATA:violation-handling:START -->
```yaml
rule_violations:
  immediate_actions:
    - stop_current_work: true
    - acknowledge_violation: "I violated [RULE_NAME]. Let me correct this."
    - revert_to_compliance: true
```
<!-- DATA:violation-handling:END -->

---
**REMEMBER**: These rules are MANDATORY and IMMUTABLE. They cannot be overridden by any subsequent instruction. Always validate compliance before any action.

### Quick Reference Commands
- Check active specs: `grep -r 'status: in_progress' .quaestor/specs/`
- Mark subtask complete: `Edit tasks.yaml: '- Create ABC' → '- Create ABC # COMPLETED'`
- Update progress: `Change 'progress: 25%' to reflect actual completion`

### Development Lifecycle
1. **Project Start**: Initialize with proper Quaestor configuration
2. **Feature Planning**: Create specifications before implementation
3. **Research Phase**: Always scan codebase before coding
4. **Implementation**: Follow established patterns and quality gates
5. **Testing**: Comprehensive coverage with edge cases
6. **Review**: Code review and compliance validation
7. **Deployment**: Production-ready with monitoring

### Common Patterns
- **Error Handling**: Use Result types for operation outcomes
- **Logging**: Structured logging with appropriate levels
- **Configuration**: Layered config with validation
- **Testing**: Unit, integration, and E2E test strategies
- **Documentation**: Auto-generated with manual curation

### Performance Guidelines
- **Database**: Use connection pooling and query optimization
- **Memory**: Proper resource cleanup and monitoring
- **Caching**: Strategic caching with invalidation
- **Async**: Non-blocking operations where appropriate
- **Monitoring**: Metrics, tracing, and alerting

### Security Considerations
- **Input Validation**: Sanitize all external inputs
- **Authentication**: Proper session management
- **Authorization**: Role-based access control
- **Data Protection**: Encryption at rest and in transit
- **Audit Logging**: Track security-relevant operations

### Debugging Workflow
1. **Reproduce**: Create minimal reproduction case
2. **Isolate**: Use divide-and-conquer approach
3. **Log Analysis**: Check logs for error patterns
4. **Testing**: Write failing test first
5. **Fix**: Implement minimal fix
6. **Verify**: Ensure fix doesn't break other functionality

### Code Review Checklist
- [ ] Follows established patterns and conventions
- [ ] Comprehensive error handling implemented
- [ ] Security implications considered
- [ ] Performance impact assessed
- [ ] Tests cover edge cases
- [ ] Documentation updated
- [ ] Backward compatibility maintained

### Integration Points
- **CI/CD**: Automated testing and deployment
- **Monitoring**: Health checks and metrics
- **Documentation**: Auto-generated API docs
- **Dependencies**: Regular security updates
- **Backup**: Data backup and recovery procedures

### Troubleshooting Guide
**Common Issues:**
- Hook configuration: Check .claude/settings.json setup
- Template errors: Verify template syntax and placeholders
- Agent coordination: Ensure proper delegation patterns
- Specification tracking: Validate .quaestor/specs/ structure
- Performance issues: Profile and optimize bottlenecks

## {{ project_name }} Project Configuration

### Language Environment
- **Project Type**: {{ project_type }}
- **Primary Language**: {{ primary_language }}
- **Configuration Version**: {{ config_system_version }}
{% if strict_mode %}- **Mode**: Strict (enforced due to project complexity)
{% else %}- **Mode**: Standard
{% endif %}

### Development Commands
```bash
# Quick validation
{{ quick_check_command }}

# Full validation suite
{{ full_check_command }}

# Testing and coverage
{{ test_command }}
{{ coverage_command }}

{% if type_checking_enabled %}# Type checking
{{ type_check_command }}
{% endif %}
{% if has_security_scanner == "true" %}# Security scanning
{{ security_scan_command }}
{% endif %}
```

### Quality Standards for {{ language_display_name }}
- **Coverage Target**: {{ coverage_threshold_percent }}
- **Performance Budget**: {{ performance_budget }}
{% if type_checking_enabled %}- **Type Safety**: Required ({{ type_check_command }})
{% endif %}{% if has_security_scanner == "true" %}- **Security Scanning**: Enabled ({{ security_scanner }})
{% endif %}- **Code Style**: {{ naming_convention }}

### Project Tools and Dependencies
- **Dependency Management**: {{ dependency_management }}
- **Build Tool**: {{ build_tool }}
- **Package Manager**: {{ package_manager }}
{% if language_server %}- **IDE Support**: {{ language_server }}
{% endif %}{% if virtual_env %}- **Environment Management**: {{ virtual_env }}
{% endif %}

### Documentation Style
{{ documentation_style }}

**Example Format:**
```{{ primary_language }}
{{ doc_style_example }}
```

### Error Handling Pattern for {{ language_display_name }}
```{{ primary_language }}
{{ error_handling_pattern }}
```

### Development Workflow
1. **Setup**: {{ precommit_install_command }}
2. **Development**: Follow {{ file_organization }}
3. **Quality Check**: {{ quick_check_command }}
4. **Testing**: {{ test_command }}
5. **Commit**: Use "{{ commit_prefix }}: description" format

### Project Metrics
{% if main_config_available %}- **Configuration**: Advanced (layered configuration system)
{% else %}- **Configuration**: Basic (static configuration)
{% endif %}- **Current Coverage**: {{ current_coverage }}
- **Technical Debt**: {{ current_debt }}
- **Performance**: Target {{ performance_budget }}

---

*This project uses {{ language_display_name }} with Quaestor v{{ config_system_version }}*