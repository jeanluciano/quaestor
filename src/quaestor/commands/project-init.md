<!-- META:command:project:init -->
<!-- META:description="Analyze Project and Initialize Quaestor Framework" -->

# Project Init - Analyze and Initialize Quaestor

Initialize the Quaestor project management framework through an adaptive, interactive process.

<!-- SECTION:init:todo-list:START -->
## Create a TODO with EXACTLY these items

<!-- DATA:todo-items:START -->
```yaml
todos:
  - id: scan_project
    name: "Scan and analyze the project"
    order: 1
  - id: interactive_confirm
    name: "Interactive confirmation with user"
    order: 2
  - id: check_existing
    name: "Check for existing Quaestor documents"
    order: 3
  - id: guide_creation
    name: "Guide document creation process"
    order: 4
  - id: create_milestone
    name: "Create first milestone for Quaestor"
    order: 5
  - id: generate_manifest
    name: "Generate project manifest"
    order: 6
  - id: provide_next_steps
    name: "Provide next steps"
    order: 7
```
<!-- DATA:todo-items:END -->
<!-- SECTION:init:todo-list:END -->

<!-- SECTION:init:details:START -->
## DETAILS on every TODO item

<!-- SECTION:init:scan-project:START -->
### 1. Scan and analyze the project

<!-- DATA:scan-config:START -->
```yaml
task_id: scan_project
inputs:
  project_type: "$ARGUMENTS"
detect:
  - overall_structure: true
  - project_age: "new_or_existing"
  - documentation:
      scan_paths:
        - "README.md"
        - "README.*"
        - "docs/"
        - "*.md"
output:
  format: "detailed"
  focus: "architecture_discovery"
  store_as: "analysis_results"
```
<!-- DATA:scan-config:END -->

<!-- DATA:deep-analysis-engine:START -->
```yaml
deep_analysis:
  language_detection:
    scan_files:
      - "package.json"
      - "requirements.txt"
      - "go.mod"
      - "Cargo.toml"
      - "pom.xml"
      - "build.gradle"
      - "*.csproj"
    identify:
      - primary_language
      - frameworks
      - runtime_version
  
  architecture_pattern_detection:
    mvc_indicators:
      - "controllers/"
      - "models/"
      - "views/"
      - "routes/"
    ddd_indicators:
      - "domain/"
      - "application/"
      - "infrastructure/"
      - "entities/"
    microservices_indicators:
      - "services/*/"
      - "docker-compose*.yml"
      - "kubernetes/"
      - "api-gateway/"
    clean_architecture_indicators:
      - "usecases/"
      - "entities/"
      - "adapters/"
      - "frameworks/"
  
  dependency_analysis:
    extract_from:
      - package_managers
      - import_statements
      - build_files
    categorize:
      - web_frameworks
      - database_drivers
      - testing_tools
      - build_tools
  
  api_detection:
    rest_patterns:
      - "*/routes/*"
      - "*/controllers/*"
      - "*/endpoints/*"
      - "@RestController"
      - "router.get"
    graphql_patterns:
      - "*.graphql"
      - "schema.gql"
      - "resolvers/"
    grpc_patterns:
      - "*.proto"
      - "grpc/"
  
  database_analysis:
    orm_detection:
      - "models/"
      - "entities/"
      - "@Entity"
      - "db.Model"
    migrations:
      - "migrations/"
      - "db/migrate/"
      - "alembic/"
    schema_files:
      - "schema.sql"
      - "*.prisma"
      - "database/*.sql"
  
  testing_infrastructure:
    frameworks:
      - jest_config: "jest.config.*"
      - pytest: "pytest.ini"
      - go_test: "*_test.go"
      - junit: "src/test/java"
    coverage_tools:
      - "coverage/"
      - ".coverage"
      - "lcov.info"
```
<!-- DATA:deep-analysis-engine:END -->
<!-- SECTION:init:scan-project:END -->

<!-- SECTION:init:interactive-confirm:START -->
### 2. Interactive confirmation with user

<!-- TEMPLATE:confirmation-dialog:START -->
```yaml
message_template: |
  I found this to be a {{project_type}} project named {{detected_name}}.
  Is this correct? Should I proceed with Quaestor setup?
action: "get_user_confirmation"
on_decline: "abort_setup"
```
<!-- TEMPLATE:confirmation-dialog:END -->
<!-- SECTION:init:interactive-confirm:END -->

<!-- SECTION:init:check-existing:START -->
### 3. Check for existing Quaestor documents

<!-- DATA:scan-existing:START -->
```yaml
scan_paths:
  - ".quaestor/ARCHITECTURE.md"
  - ".quaestor/MEMORY.md"
  - ".quaestor/commands/"
  - "CLAUDE.md"
  
interactive_decisions:
  if_found:
    message: "I found existing documents: {{document_list}}. Should we work with these or extend them?"
    options:
      - use_existing
      - extend_existing
      - start_fresh
  if_not_found:
    message: "No Quaestor documents found yet. Do you have any existing project documentation you'd like to copy in before we continue?"
    options:
      - proceed_without_docs
      - wait_for_manual_add
      - import_from_path
```
<!-- DATA:scan-existing:END -->
<!-- SECTION:init:check-existing:END -->

<!-- SECTION:init:guide-creation:START -->
### 4. Guide document creation process

<!-- WORKFLOW:document-creation:START -->
```yaml
states:
  - id: fresh_or_extending
    actions:
      - deep_analysis:
          targets: ["codebase", "architecture", "patterns"]
          store_results: "analysis_cache"
      - pattern_matching:
          input: "analysis_cache"
          determine: "architecture_pattern"
      - intelligent_qa:
          based_on: "detected_patterns"
          generate: "contextual_questions"
      - generate_ai_documents:
          architecture: "AI_ARCHITECTURE.md"
          memory: "AI_MEMORY.md"
          format: "yaml_structured"
      - validate_with_user:
          review: "generated_documents"
          allow_edits: true
  
  - id: using_existing
    actions:
      - import_docs:
          from: "existing_paths"
      - adapt_to_quaestor:
          ensure: "framework_compatibility"
      - fill_gaps:
          add: "quaestor_specific_sections"
```
<!-- WORKFLOW:document-creation:END -->

<!-- DATA:intelligent-question-generation:START -->
```yaml
question_engine:
  context_based_questions:
    - trigger: "web_framework_detected"
      framework_specific:
        react:
          - "Is this a single-page application or server-side rendered?"
          - "What state management solution are you using (Redux, Context, Zustand)?"
          - "Do you have a component library or design system?"
        django:
          - "Are you using Django REST Framework for APIs?"
          - "What's your authentication strategy (sessions, JWT, OAuth)?"
          - "Do you follow Django's app structure conventions?"
        express:
          - "Is this a REST API, GraphQL server, or full-stack app?"
          - "What middleware chain do you use for authentication?"
          - "How do you handle request validation?"
    
    - trigger: "microservices_detected"
      questions:
        - "How do your services communicate (REST, gRPC, message queues)?"
        - "What's your service discovery mechanism?"
        - "How do you handle distributed tracing?"
        - "What's your strategy for data consistency?"
    
    - trigger: "database_detected"
      database_specific:
        postgresql:
          - "Do you use any PostgreSQL-specific features (JSONB, arrays, full-text search)?"
          - "What's your indexing strategy?"
        mongodb:
          - "How do you handle schema validation?"
          - "Do you use aggregation pipelines?"
        redis:
          - "Is Redis used for caching, sessions, or as a primary store?"
          - "What's your key expiration strategy?"
    
    - trigger: "testing_detected"
      questions:
        - "What's your target test coverage percentage?"
        - "Do you follow TDD or BDD practices?"
        - "How do you handle integration vs unit tests?"
        - "Do you have E2E tests? What tools?"
    
    - trigger: "no_clear_pattern"
      discovery_questions:
        - "What type of application is this?"
        - "What problem does it solve?"
        - "Who are the primary users?"
        - "What are the main features?"
        - "What architectural pattern would you like to follow?"
```
<!-- DATA:intelligent-question-generation:END -->

<!-- DATA:yaml-structure-generators:START -->
```yaml
generators:
  architecture_pattern_generator:
    inputs:
      - detected_structure
      - user_answers
      - framework_conventions
    outputs:
      pattern:
        selected: "{{detected_pattern}}"
        description: "{{reasoning_based_on_analysis}}"
        confidence: "{{high|medium|low}}"
  
  directory_structure_generator:
    inputs:
      - file_tree_scan
      - detected_patterns
    outputs:
      structure:
        - path: "{{dir_path}}"
          description: "{{inferred_purpose}}"
          contains: "{{detected_contents}}"
  
  component_generator:
    inputs:
      - import_analysis
      - class_definitions
      - function_exports
    outputs:
      components:
        - name: "{{component_name}}"
          responsibility: "{{inferred_responsibility}}"
          dependencies: "{{detected_dependencies}}"
          type: "{{service|controller|model|utility}}"
  
  milestone_generator:
    inputs:
      - git_history
      - readme_content
      - package_version
      - user_input
    outputs:
      milestones:
        - id: "{{generated_id}}"
          name: "{{milestone_name}}"
          status: "{{current|upcoming|completed}}"
          progress: "{{calculated_percentage}}"
          tasks: "{{detected_or_suggested_tasks}}"
  
  metrics_generator:
    inputs:
      - project_type
      - testing_setup
      - user_goals
    outputs:
      technical_metrics:
        - metric: "Test Coverage"
          target: "{{suggested_target}}%"
          current: "{{detected_coverage}}%"
      business_metrics:
        - metric: "{{relevant_business_metric}}"
          target: "{{user_defined}}"
```
<!-- DATA:yaml-structure-generators:END -->
<!-- SECTION:init:guide-creation:END -->

<!-- SECTION:init:create-milestone:START -->
### 5. Create first milestone for Quaestor

<!-- DATA:milestone-logic:START -->
```yaml
decision_tree:
  - condition: "project_type == 'new'"
    action: "create_setup_milestone"
    milestone:
      name: "Project Foundation"
      focus: "setup_and_structure"
  
  - condition: "project_type == 'existing'"
    action: "identify_current_phase"
    milestone:
      name: "{{detected_phase}}"
      focus: "{{current_work}}"

interactive:
  suggest: "Based on the project state, I suggest creating milestone: {{milestone_name}}"
  ask: "What would you like to focus on in this milestone?"
  scope: "realistic_and_focused"
```
<!-- DATA:milestone-logic:END -->
<!-- SECTION:init:create-milestone:END -->

<!-- SECTION:init:generate-manifest:START -->
### 6. Generate project manifest

<!-- DATA:manifest-generation:START -->
```yaml
auto_generate: true
no_interaction: true
sources:
  - setup_information
  - created_documents
  - milestone_details
  - project_metadata
notify_when: "complete"
```
<!-- DATA:manifest-generation:END -->
<!-- SECTION:init:generate-manifest:END -->

<!-- SECTION:init:provide-next-steps:START -->
### 7. Provide next steps

<!-- TEMPLATE:completion-message:START -->
```yaml
message_template: |
  ✅ Quaestor initialized for {{project_name}}!
  
  Current setup:
  - Project type: {{project_type}}
  - Current milestone: {{milestone_name}}
  - Documents: {{documents_status}}
  
  Next steps:
  - Review your architecture: .quaestor/ARCHITECTURE.md
  - Check milestone requirements: .quaestor/{{milestone_path}}/
  - Start first task: /quaestor:task:create
  
  Ready to begin development!
```
<!-- TEMPLATE:completion-message:END -->
<!-- SECTION:init:provide-next-steps:END -->
<!-- SECTION:init:details:END -->

<!-- SECTION:init:process-notes:START -->
## ADAPTIVE PROCESS NOTES

<!-- DATA:process-guidelines:START -->
```yaml
principles:
  - key: "conversational"
    value: "Ask questions naturally, not like a form"
  - key: "intelligent"
    value: "Use AI to understand context and make smart suggestions"
  - key: "flexible"
    value: "User can skip, cancel, or modify at any point"
  - key: "value_focused"
    value: "Only create what's useful for the specific project"
  - key: "simple"
    value: "Don't overwhelm with options or details"
  - key: "adaptive"
    value: "Adjust questions based on what's discovered"
  - key: "comprehensive"
    value: "Generate complete, ready-to-use AI-format documents"
```
<!-- DATA:process-guidelines:END -->

<!-- SECTION:init:ai-generation-examples:START -->
## AI Document Generation Examples

<!-- EXAMPLE:generated-architecture:START -->
```yaml
when_detecting: "Express.js REST API with PostgreSQL"
generate_architecture:
  pattern:
    selected: "MVC with Service Layer"
    description: "Detected Express routes following RESTful conventions with service layer for business logic"
  
  layers:
    - name: "Controller Layer"
      path: "/src/controllers"
      description: "HTTP request handlers and response formatting"
      components:
        - type: "Controllers"
          description: "Handle HTTP requests, validate input, call services"
    
    - name: "Service Layer"
      path: "/src/services"
      description: "Business logic and orchestration"
      components:
        - type: "Services"
          description: "Implement business rules, coordinate between repositories"
    
    - name: "Data Layer"
      path: "/src/models"
      description: "Database models and data access"
      components:
        - type: "Models"
          description: "Sequelize/TypeORM models representing database tables"
        - type: "Repositories"
          description: "Data access patterns and queries"
```
<!-- EXAMPLE:generated-architecture:END -->

<!-- EXAMPLE:generated-memory:START -->
```yaml
when_analyzing: "Existing project with 6 months of commits"
generate_memory:
  status:
    last_updated: "{{current_date}}"
    current_phase: "Active Development"
    current_milestone: "Feature Enhancement"
    overall_progress: "65%"
  
  milestones:
    - id: "foundation"
      name: "Project Foundation"
      status: "completed"
      progress: "100%"
      completed:
        - task: "Basic API structure"
          date: "{{3_months_ago}}"
        - task: "Database schema"
          date: "{{3_months_ago}}"
    
    - id: "core_features"
      name: "Core Features"
      status: "in_progress"
      progress: "65%"
      in_progress:
        - task: "User authentication system"
          eta: "Next week"
      todo:
        - task: "Payment integration"
          priority: "High"
```
<!-- EXAMPLE:generated-memory:END -->
<!-- SECTION:init:ai-generation-examples:END -->
<!-- SECTION:init:process-notes:END -->

<!-- SECTION:init:validation-phase:START -->
## Validation and Review Phase

<!-- DATA:validation-workflow:START -->
```yaml
validation:
  generated_documents_review:
    show_user:
      - architecture_summary: "condensed_view"
      - key_components: "list_with_descriptions"
      - detected_patterns: "with_confidence_scores"
    
    ask_user:
      - "Does this architecture accurately reflect your project?"
      - "Are there any missing components or layers?"
      - "Would you like to adjust any of the detected patterns?"
    
    allow_modifications:
      - add_components: true
      - change_patterns: true
      - update_descriptions: true
      - regenerate_section: true
  
  memory_document_review:
    show_user:
      - current_status: "with_progress_bars"
      - milestones: "timeline_view"
      - next_actions: "prioritized_list"
    
    validate:
      - milestone_names: "are_they_meaningful"
      - progress_percentages: "are_they_accurate"
      - task_priorities: "align_with_user_goals"
```
<!-- DATA:validation-workflow:END -->
<!-- SECTION:init:validation-phase:END -->

<!-- SECTION:init:fallback-strategies:START -->
## Fallback Strategies

<!-- DATA:fallback-logic:START -->
```yaml
when_analysis_insufficient:
  minimal_detection:
    message: "I couldn't detect a clear architecture pattern. Let me help you choose one."
    offer_templates:
      - name: "Web Application (MVC)"
        when: "web_framework_detected"
      - name: "REST API (Service Layer)"
        when: "api_endpoints_detected"
      - name: "Microservices"
        when: "multiple_services_detected"
      - name: "Domain-Driven Design"
        when: "complex_business_logic"
      - name: "Simple Script/Tool"
        when: "single_file_or_simple"
    
    guided_setup:
      - ask: "What type of application is this?"
      - show: "Common patterns for {{app_type}}"
      - guide: "Let's build your architecture step by step"
  
  no_code_found:
    message: "This appears to be a new project. Let's plan your architecture."
    workflow:
      - ask_project_type: "What will you be building?"
      - suggest_architecture: "Based on {{project_type}}"
      - create_skeleton: "Generate starter structure"
      - plan_milestones: "Define initial development phases"
  
  partial_information:
    use_ai_inference:
      - from: "README content"
      - from: "Package dependencies"
      - from: "Directory names"
    fill_gaps:
      - with: "Common patterns for similar projects"
      - with: "Best practices for detected stack"
```
<!-- DATA:fallback-logic:END -->
<!-- SECTION:init:fallback-strategies:END -->

<!-- SECTION:init:implementation-notes:START -->
## Implementation Notes for AI Agents

<!-- DATA:agent-instructions:START -->
```yaml
for_ai_agents:
  code_analysis_phase:
    - scan_all_files: "Use glob patterns from deep_analysis_engine"
    - identify_entry_points: "main.*, index.*, app.*, server.*"
    - trace_dependencies: "Build import graph"
    - detect_patterns: "Match against pattern indicators"
    - confidence_scoring: "Rate pattern match confidence"
  
  question_generation_phase:
    - prioritize_questions: "Most important first"
    - limit_questions: "Max 5-7 per session"
    - use_context: "Reference detected components in questions"
    - natural_language: "Conversational, not robotic"
  
  document_generation_phase:
    - populate_all_fields: "No placeholder text"
    - use_real_paths: "From actual file system"
    - calculate_progress: "From git history or estimates"
    - infer_relationships: "From import statements"
    - generate_descriptions: "Based on code analysis"
  
  validation_phase:
    - present_clearly: "Use formatting and structure"
    - highlight_uncertain: "Mark low-confidence items"
    - allow_iteration: "User can regenerate sections"
    - save_preferences: "Learn from user corrections"
```
<!-- DATA:agent-instructions:END -->
<!-- SECTION:init:implementation-notes:END -->