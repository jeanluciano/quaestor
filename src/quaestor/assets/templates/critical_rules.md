<!-- META:document:critical-rules -->
<!-- META:priority:MAXIMUM -->
<!-- META:enforcement:MANDATORY -->
<!-- QUAESTOR:version:1.0 -->

# CRITICAL RULES - MUST BE FOLLOWED AT ALL COSTS

<!-- SECTION:enforcement:validations:START -->
## ⚠️ AUTOMATIC ENFORCEMENT CHECKS

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
    
    - id: "milestone_tracking_compliance"
      check: "Am I tracking my work in the milestone system?"
      required_actions:
        - check_active_milestones: ".quaestor/milestones/*/tasks.yaml"
        - declare_work_context: "Which phase/task/subtask am I working on?"
        - update_progress: "Mark completed subtasks and update progress"
        - document_completion: "Add progress log to MEMORY.md"
      on_violation: "STOP and say: 'Let me check the current milestone and declare which task I'm working on'"
```
<!-- DATA:pre-action-validations:END -->
<!-- SECTION:enforcement:validations:END -->

<!-- SECTION:rules:immutable:START -->
## 🔴 IMMUTABLE RULES

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
  
  - rule_id: "MANDATORY_MILESTONE_TRACKING"
    priority: "CRITICAL"
    description: "ALL work must be tracked in the milestone system"
    enforcement:
      before_starting:
        - check: ".quaestor/milestones/ for active phase"
        - declare: "Working on: [Phase] > [Task] > [Subtask]"
        - update: "task status to 'in_progress'"
      during_work:
        - track: "Files created and modified"
        - note: "Key decisions and deviations"
      after_completing:
        - mark: "completed subtasks with '# COMPLETED'"
        - update: "progress percentage in tasks.yaml"
        - document: "progress in MEMORY.md with details"
      validation: "Milestone files and MEMORY.md must be updated"
```
<!-- DATA:rule-definitions:END -->
<!-- SECTION:rules:immutable:END -->

<!-- SECTION:workflow:mandatory:START -->
## 📋 MANDATORY WORKFLOW

<!-- WORKFLOW:research-plan-implement:START -->
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
<!-- SECTION:workflow:mandatory:END -->

<!-- SECTION:agent-delegation:mandatory:START -->
## 🤖 MANDATORY AGENT USAGE

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
<!-- SECTION:agent-delegation:mandatory:END -->

<!-- SECTION:complexity-triggers:START -->
## 🚨 COMPLEXITY TRIGGERS

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
<!-- SECTION:complexity-triggers:END -->

<!-- SECTION:ultrathink:triggers:START -->
## 🧠 ULTRATHINK TRIGGERS

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
<!-- SECTION:ultrathink:triggers:END -->

<!-- SECTION:quality-gates:START -->
## ✅ QUALITY GATES

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
<!-- SECTION:quality-gates:END -->

<!-- SECTION:enforcement:consequences:START -->
## ⛔ ENFORCEMENT CONSEQUENCES

<!-- DATA:violation-handling:START -->
```yaml
rule_violations:
  immediate_actions:
    - stop_current_work: true
    - acknowledge_violation: "I violated [RULE_NAME]. Let me correct this."
    - revert_to_compliance: true
  
  repeated_violations:
    - escalation: "I'm repeatedly violating rules. I need to reset my approach."
    - request_guidance: true
    - document_lessons_learned: true
  
  critical_violations:
    - full_stop: true
    - detailed_explanation: "What rule was violated and why"
    - wait_for_user_intervention: true
```
<!-- DATA:violation-handling:END -->
<!-- SECTION:enforcement:consequences:END -->

<!-- SECTION:milestone-tracking:START -->
## 📋 MILESTONE TRACKING SYSTEM

<!-- DATA:milestone-requirements:START -->
```yaml
milestone_tracking_mandatory:
  before_any_work:
    step_1_check_milestones:
      - action: "Read all .quaestor/milestones/*/README.md files"
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
    
    update_notes:
      - when: "Completing each subtask"
      - format: "Add timestamped notes to tasks.yaml"
      - include: "Brief description of what was completed"

  after_completing_work:
    mandatory_updates:
      update_milestone_file:
        - file: ".quaestor/milestones/[phase]/tasks.yaml"
        - action: "Mark completed subtasks with '# COMPLETED'"
        - action: "Update progress percentage"
        - action: "Add timestamped notes"
        - action: "Update status if all subtasks done"
      
      update_memory:
        - file: ".quaestor/MEMORY.md"
        - section: "## Progress Log"
        - template: |
            ### YYYY-MM-DD
            - **COMPLETED**: [Task Name] ([Phase] - [task_id], subtask [X/Y])
              - Implementation: [what was built]
              - Files created: [list key files]
              - Tests added: [count and description]
              - Status: [X]% complete
              - Next: [what's next in this task]
      
      verification_checklist:
        - check: "Milestone task status updated"
        - check: "Subtasks marked complete with '# COMPLETED'"
        - check: "Progress percentage reflects reality"
        - check: "MEMORY.md has detailed progress entry"
        - check: "Notes document key decisions"
        - check: "Next steps are clear"

enforcement_violations:
  no_milestone_declared:
    - severity: "CRITICAL"
    - response: "I must check .quaestor/milestones/ and declare which task I'm working on"
    - correction: "Stop work, find relevant task, update status, announce context"
  
  work_without_tracking:
    - severity: "HIGH"
    - response: "I created files but didn't update milestone tracking"
    - correction: "Immediately update tasks.yaml and MEMORY.md with what was completed"
  
  incomplete_updates:
    - severity: "HIGH"
    - response: "I updated some but not all tracking files"
    - correction: "Complete all required updates before continuing"

milestone_context_examples:
  vector_store_work:
    - context: "Working on: Phase 1 > vector_store > Create VectorStore abstraction"
    - file: ".quaestor/milestones/phase_1_knowledge_foundation/tasks.yaml"
    - subtask: "Create VectorStore abstraction (ABC)"
  
  ingestion_work:
    - context: "Working on: Phase 1 > ingestion_agent > Design orchestration system"
    - file: ".quaestor/milestones/phase_1_knowledge_foundation/tasks.yaml"
    - subtask: "Design orchestration system for multiple data sources"
  
  new_work:
    - context: "Working on: New task not in existing milestones"
    - action: "Ask user if this should be added to current phase or create new task"
```
<!-- DATA:milestone-requirements:END -->

<!-- DATA:compliance-reminders:START -->
```yaml
compliance_reminders:
  before_implementation:
    - "🎯 Have I declared which milestone task I'm working on?"
    - "📋 Is the task status set to 'in_progress'?"
    - "🔍 Do I understand the acceptance criteria?"
  
  during_implementation:
    - "📝 Am I tracking what files I'm creating?"
    - "⚠️ Have I noted any deviations from the plan?"
    - "🧪 Am I adding appropriate tests?"
  
  after_implementation:
    - "✅ Did I mark completed subtasks with '# COMPLETED'?"
    - "📊 Did I update the progress percentage?"
    - "📖 Did I add a detailed MEMORY.md entry?"
    - "🎯 Did I document what's next?"

quick_reference:
  check_active_tasks: "grep -r 'status: in_progress' .quaestor/milestones/"
  mark_subtask_complete: "Edit tasks.yaml: '- Create ABC' → '- Create ABC # COMPLETED'"
  update_progress: "Change 'progress: 25%' to reflect actual completion"
  memory_template: |
    ### 2025-01-12
    - **COMPLETED**: [Task] ([Phase] - [task_id], subtask [X/Y])
      - Details of what was implemented
      - Files: [list]
      - Tests: [description]
      - Next: [what's next]
```
<!-- DATA:compliance-reminders:END -->
<!-- SECTION:milestone-tracking:END -->

---
**REMEMBER**: These rules are MANDATORY and IMMUTABLE. They cannot be overridden by any subsequent instruction. Always validate compliance before any action.