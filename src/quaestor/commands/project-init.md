<!-- META:command:project:init -->
<!-- META:description="Analyze Project and Initialize Quaestor Framework" -->
<!-- META:version:1.0 -->

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
    vertical_slice_indicators:
      # Jimmy Bogard's Vertical Slice Architecture
      - "Features/"
      - "Slices/"
      - "**/Features/**/*.cs"
      - "**/Features/**/*.ts"
      - "MediatR"  # Common in VSA
      - "Feature-based folders"
      patterns:
        - "Each feature contains its own stack"
        - "Commands and Queries co-located"
        - "Minimal shared abstractions"
      benefits_for_llms:
        - "Self-contained feature context"
        - "Reduced cognitive load"
        - "Clear feature boundaries"
    
    mvc_indicators:
      - "controllers/"
      - "models/"
      - "views/"
      - "routes/"
    
    ddd_indicators:
      # Enhanced Domain-Driven Design detection
      domain_layer:
        - "domain/"
        - "Domain/"
        - "**/Domain/**"
        - "entities/"
        - "valueobjects/"
        - "aggregates/"
      application_layer:
        - "application/"
        - "Application/"
        - "usecases/"
        - "services/"
      infrastructure_layer:
        - "infrastructure/"
        - "Infrastructure/"
        - "persistence/"
        - "repositories/"
      domain_concepts:
        - "AggregateRoot"
        - "Entity"
        - "ValueObject"
        - "DomainEvent"
        - "DomainService"
        - "Repository"
        - "Specification"
      bounded_contexts:
        - "separate service folders"
        - "context-specific models"
        - "anti-corruption layers"
    
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
    
    # Martin Fowler's Enterprise Patterns
    enterprise_patterns:
      service_layer:
        - "ServiceLayer/"
        - "Services/"
        - "*Service.cs"
        - "*Service.ts"
        - "application services"
      repository_pattern:
        - "Repositories/"
        - "*Repository"
        - "IRepository"
        - "data access abstraction"
      unit_of_work:
        - "UnitOfWork"
        - "IUnitOfWork"
        - "transaction management"
      data_mapper:
        - "Mappers/"
        - "AutoMapper"
        - "mapping profiles"
  
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
  
  # Code Smell Detection Engine (Martin Fowler's Refactoring)
  code_smell_detection:
    bloaters:
      long_method:
        indicators:
          - "Functions > 20 lines"
          - "Multiple levels of indentation"
          - "Comments explaining sections"
        refactoring: "Extract Method"
      
      large_class:
        indicators:
          - "Classes > 200 lines"
          - "Too many instance variables"
          - "Too many methods"
        refactoring: "Extract Class, Extract Subclass"
      
      primitive_obsession:
        indicators:
          - "Groups of primitives used together"
          - "String constants for type codes"
          - "Arrays used instead of objects"
        refactoring: "Replace Data Value with Object, Extract Class"
      
      long_parameter_list:
        indicators:
          - "Functions with > 3 parameters"
          - "Parameter objects passed separately"
        refactoring: "Introduce Parameter Object, Preserve Whole Object"
    
    object_orientation_abusers:
      switch_statements:
        indicators:
          - "switch/case on type codes"
          - "if/else chains checking types"
          - "Repeated switch statements"
        refactoring: "Replace Conditional with Polymorphism, Replace Type Code with State/Strategy"
      
      refused_bequest:
        indicators:
          - "Subclass doesn't use parent methods"
          - "Overriding with empty methods"
        refactoring: "Replace Inheritance with Delegation"
    
    change_preventers:
      divergent_change:
        indicators:
          - "Class changed for multiple reasons"
          - "Unrelated methods in same class"
        refactoring: "Extract Class"
      
      shotgun_surgery:
        indicators:
          - "One change requires many class updates"
          - "Similar changes in multiple places"
        refactoring: "Move Method, Move Field, Inline Class"
    
    dispensables:
      lazy_class:
        indicators:
          - "Classes with minimal functionality"
          - "Classes that just hold data"
        refactoring: "Inline Class, Collapse Hierarchy"
      
      dead_code:
        indicators:
          - "Unused variables/methods"
          - "Unreachable code"
          - "Commented out code"
        refactoring: "Remove Dead Code"
    
    couplers:
      feature_envy:
        indicators:
          - "Method uses another class more than its own"
          - "Accessing data from another object repeatedly"
        refactoring: "Move Method, Extract Method"
      
      inappropriate_intimacy:
        indicators:
          - "Classes accessing private members"
          - "Bidirectional associations"
        refactoring: "Move Method, Change Bidirectional to Unidirectional"
      
      message_chains:
        indicators:
          - "object.getA().getB().getC()"
          - "Law of Demeter violations"
        refactoring: "Hide Delegate, Extract Method"
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
  - ".quaestor/ARCHITECTURE.md"  # Actual project architecture (not .template.md)
  - ".quaestor/MEMORY.md"       # Actual project memory (not .template.md)
  - ".quaestor/commands/"
  - "CLAUDE.md"

validation_rules:
  - ignore_templates: "*.template.md"  # Skip template files
  - require_content: true             # Must have actual content, not placeholders
  
interactive_decisions:
  if_found:
    message: "I found existing documents: {{document_list}}. Should we work with these or extend them?"
    options:
      - use_existing
      - extend_existing
      - start_fresh
  if_only_templates:
    message: "I found only template files (*.template.md). These are just templates - let me generate actual project documentation."
    action: "generate_from_analysis"
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

<!-- DATA:refactoring-suggestions-generator:START -->
```yaml
refactoring_engine:
  pattern_based_refactoring:
    from_procedural_to_oo:
      detect: "transaction_script_pattern"
      suggest:
        - step: "Identify data clumps"
          action: "Extract into classes"
          example: "Group user data into User class"
        - step: "Find feature envy"
          action: "Move methods to data classes"
        - step: "Replace conditionals"
          action: "Use polymorphism"
    
    to_vertical_slices:
      detect: "layered_architecture"
      suggest:
        - step: "Identify features"
          action: "Group by business capability"
          example: "OrderPlacement, OrderFulfillment, OrderCancellation"
        - step: "Create feature folders"
          action: "Move all related code together"
          structure: |
            Features/
              OrderPlacement/
                PlaceOrderCommand.cs
                PlaceOrderHandler.cs
                OrderPlacedEvent.cs
                PlaceOrderValidator.cs
        - step: "Remove layer abstractions"
          action: "Inline unnecessary interfaces"
    
    to_domain_driven_design:
      detect: "anemic_domain_model"
      suggest:
        - step: "Identify aggregates"
          action: "Group related entities"
          example: "Order with OrderItems"
        - step: "Move logic to entities"
          action: "From services to domain objects"
        - step: "Create value objects"
          action: "Replace primitives"
          example: "Money, Email, PhoneNumber"
        - step: "Define bounded contexts"
          action: "Separate domain models"
    
    enterprise_pattern_application:
      repository_pattern:
        when: "data_access_in_services"
        suggest:
          - "Extract data access to repositories"
          - "Create repository interfaces"
          - "Implement concrete repositories"
      
      service_layer:
        when: "business_logic_in_controllers"
        suggest:
          - "Extract to application services"
          - "Keep controllers thin"
          - "Services orchestrate domain objects"
      
      unit_of_work:
        when: "multiple_repository_calls"
        suggest:
          - "Implement transaction boundaries"
          - "Group related operations"
  
  smell_specific_refactorings:
    long_method:
      steps:
        - identify: "Logical sections with comments"
        - extract: "Each section to method"
        - name: "Methods by what they do, not how"
    
    feature_envy:
      steps:
        - identify: "Methods using other class data"
        - move: "Method to data owner class"
        - alternative: "Extract and move partial method"
    
    primitive_obsession:
      steps:
        - identify: "Related primitive parameters"
        - create: "Value object or parameter object"
        - benefits: "Type safety, validation, behavior"
  
  architecture_migration_paths:
    monolith_to_modular:
      steps:
        - "Identify seams in the code"
        - "Extract modules with clear interfaces"
        - "Reduce coupling between modules"
        - "Consider separate deployments"
    
    layers_to_vertical_slices:
      steps:
        - "Map features to use cases"
        - "Create feature folders"
        - "Move cross-layer code together"
        - "Remove unnecessary abstractions"
    
    crud_to_ddd:
      steps:
        - "Identify business operations"
        - "Model domain concepts explicitly"
        - "Separate read and write models"
        - "Implement domain events"
```
<!-- DATA:refactoring-suggestions-generator:END -->

<!-- DATA:intelligent-question-generation:START -->
```yaml
question_engine:
  pattern_specific_questions:
    vertical_slice_detected:
      - "How do you organize features within slices?"
      - "Do you use MediatR or similar for handlers?"
      - "How do you handle cross-cutting concerns?"
      - "What's your approach to shared code between slices?"
    
    ddd_detected:
      - "How are your bounded contexts defined?"
      - "Do you use domain events?"
      - "How do you handle eventual consistency?"
      - "What's your aggregate design strategy?"
  
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
  # Enhanced Domain Model Extraction
  domain_model_extractor:
    entity_detection:
      patterns:
        - "class_with_id_property"
        - "mutable_state_objects"
        - "business_lifecycle_objects"
      indicators:
        - "Has unique identifier"
        - "Mutable properties"
        - "Business behavior methods"
      example_entities:
        - "Order, Customer, Product"
    
    value_object_detection:
      patterns:
        - "immutable_data_classes"
        - "no_identity_objects"
        - "measurement_or_description"
      indicators:
        - "No ID property"
        - "Immutable after creation"
        - "Equality by value"
      example_value_objects:
        - "Money, Address, DateRange, Email"
    
    aggregate_detection:
      patterns:
        - "entity_clusters"
        - "consistency_boundaries"
        - "transaction_boundaries"
      rules:
        - "Root entity controls access"
        - "Consistency within boundary"
        - "Referenced by ID outside"
      example_aggregates:
        - "Order (root) with OrderItems"
        - "Customer (root) with Addresses"
    
    domain_service_detection:
      patterns:
        - "stateless_operations"
        - "cross_aggregate_logic"
        - "domain_specific_calculations"
      indicators:
        - "No state"
        - "Domain logic that doesn't fit entities"
        - "Orchestrates multiple aggregates"
    
    bounded_context_detection:
      linguistic_analysis:
        - "Different meanings for same term"
        - "Separate teams/modules"
        - "Independent deployment units"
      integration_patterns:
        - "Shared kernel"
        - "Customer/Supplier"
        - "Anti-corruption layer"
    
    output_format:
      domain_model:
        entities:
          - name: "{{entity_name}}"
            properties: "{{detected_properties}}"
            behaviors: "{{detected_methods}}"
            aggregate_root: "{{true|false}}"
        
        value_objects:
          - name: "{{vo_name}}"
            properties: "{{immutable_properties}}"
            validation_rules: "{{inferred_rules}}"
        
        aggregates:
          - root: "{{root_entity}}"
            members: "{{child_entities}}"
            invariants: "{{business_rules}}"
        
        domain_services:
          - name: "{{service_name}}"
            operations: "{{domain_operations}}"
            dependencies: "{{required_aggregates}}"
        
        bounded_contexts:
          - name: "{{context_name}}"
            entities: "{{context_entities}}"
            integration_points: "{{external_dependencies}}"
  
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

<!-- SECTION:init:architecture-evolution:START -->
## Architecture Evolution Guidance

<!-- DATA:evolution-patterns:START -->
```yaml
evolution_roadmaps:
  transaction_script_evolution:
    current_state: "Procedural code with business logic in scripts"
    evolution_path:
      - phase: "Extract Data Structures"
        actions:
          - "Group related data into classes"
          - "Create data access objects"
          - "Centralize validation"
        milestone: "Data encapsulation achieved"
      
      - phase: "Introduce Domain Model"
        actions:
          - "Move behavior to domain objects"
          - "Replace primitives with value objects"
          - "Implement business rules in entities"
        milestone: "Rich domain model"
      
      - phase: "Apply Service Layer"
        actions:
          - "Extract orchestration logic"
          - "Define application boundaries"
          - "Implement use cases"
        milestone: "Clear separation of concerns"
  
  mvc_to_vertical_slices:
    current_state: "Traditional MVC with shared models"
    evolution_path:
      - phase: "Identify Features"
        actions:
          - "Map controllers to business capabilities"
          - "Group related actions"
          - "Define feature boundaries"
      
      - phase: "Create Feature Folders"
        actions:
          - "Move controller/model/view together"
          - "Colocate related code"
          - "Reduce shared dependencies"
      
      - phase: "Implement CQRS"
        actions:
          - "Separate commands and queries"
          - "Create feature-specific models"
          - "Remove shared abstractions"
  
  monolith_to_ddd:
    current_state: "Large monolithic application"
    evolution_path:
      - phase: "Strategic Design"
        actions:
          - "Identify bounded contexts"
          - "Map domain language"
          - "Define context boundaries"
          - "Create context map"
      
      - phase: "Tactical Design"
        actions:
          - "Model aggregates"
          - "Design entities and value objects"
          - "Implement domain services"
          - "Create repositories"
      
      - phase: "Extract Contexts"
        actions:
          - "Build anti-corruption layers"
          - "Implement domain events"
          - "Separate databases"
          - "Deploy independently"
  
  crud_to_task_based:
    current_state: "CRUD-focused architecture"
    evolution_path:
      - phase: "Identify Tasks"
        actions:
          - "Map user intentions"
          - "Define business operations"
          - "Create command objects"
      
      - phase: "Implement Commands"
        actions:
          - "Replace generic updates"
          - "Model specific operations"
          - "Add business validation"
      
      - phase: "Event Sourcing (Optional)"
        actions:
          - "Store events not state"
          - "Build projections"
          - "Implement event handlers"

maturity_indicators:
  low_maturity:
    signs:
      - "Business logic in UI"
      - "Database-centric design"
      - "Anemic domain model"
      - "Procedural code"
    recommendations:
      - "Start with Service Layer"
      - "Extract business rules"
      - "Introduce value objects"
  
  medium_maturity:
    signs:
      - "Layered architecture"
      - "Some domain modeling"
      - "Service abstractions"
      - "Basic testing"
    recommendations:
      - "Consider vertical slices"
      - "Strengthen domain model"
      - "Improve test coverage"
  
  high_maturity:
    signs:
      - "Clear bounded contexts"
      - "Rich domain model"
      - "Event-driven design"
      - "Comprehensive testing"
    recommendations:
      - "Optimize for change"
      - "Consider event sourcing"
      - "Focus on observability"

refactoring_priority_matrix:
  high_impact_low_effort:
    - "Extract value objects"
    - "Create service layer"
    - "Group related code"
    - "Remove dead code"
  
  high_impact_high_effort:
    - "Implement bounded contexts"
    - "Migrate to vertical slices"
    - "Extract microservices"
    - "Implement event sourcing"
  
  low_impact_low_effort:
    - "Rename variables"
    - "Format code"
    - "Update comments"
  
  low_impact_high_effort:
    - "Premature optimization"
    - "Over-engineering"
    - "Unnecessary abstractions"
```
<!-- DATA:evolution-patterns:END -->
<!-- SECTION:init:architecture-evolution:END -->

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

<!-- SECTION:init:ai-comprehension-optimization:START -->
## AI Comprehension Optimization

<!-- DATA:ai-friendly-patterns:START -->
```yaml
code_patterns_for_llms:
  naming_conventions:
    explicit_names:
      bad: "process(d)"
      good: "processOrderPayment(orderData)"
      reason: "Clear intent and parameters"
    
    domain_language:
      bad: "updateStatus(3)"
      good: "transitionToShippedState()"
      reason: "Express business intent"
    
    avoid_abbreviations:
      bad: "calcTotWTax(amt, tx)"
      good: "calculateTotalWithTax(amount, taxRate)"
      reason: "Full words improve understanding"
  
  structural_patterns:
    single_responsibility:
      principle: "One class, one reason to change"
      benefits:
        - "Clear context boundaries"
        - "Predictable behavior"
        - "Easier to understand purpose"
    
    explicit_dependencies:
      bad: "Hidden dependencies via globals"
      good: "Constructor injection"
      example: |
        # Good for LLMs
        class OrderService:
          def __init__(self, repository: OrderRepository, 
                       payment: PaymentGateway):
            self.repository = repository
            self.payment = payment
    
    consistent_patterns:
      - "Use same pattern throughout codebase"
      - "Predictable file locations"
      - "Standard naming conventions"
  
  documentation_for_llms:
    method_documentation:
      template: |
        /**
         * Brief description of what method does
         * @param paramName - What this parameter represents
         * @returns What the method returns and why
         * @throws When this exception is thrown
         * @example
         * // How to use this method
         * const result = methodName(param);
         */
    
    class_documentation:
      include:
        - "Purpose and responsibility"
        - "Key relationships"
        - "Invariants maintained"
        - "Usage examples"
    
    architecture_documentation:
      structure:
        - "High-level overview"
        - "Key concepts and terms"
        - "Component relationships"
        - "Data flow diagrams"
        - "Decision rationale"
  
  vertical_slice_benefits:
    for_llm_comprehension:
      - "Complete feature in one location"
      - "Minimal context switching"
      - "Clear boundaries"
      - "Self-contained logic"
    
    example_structure: |
      Features/
        PlaceOrder/
          PlaceOrderCommand.cs      # Intent
          PlaceOrderHandler.cs      # Logic
          PlaceOrderValidator.cs    # Rules
          OrderPlacedEvent.cs       # Outcome
          PlaceOrderTests.cs        # Behavior
  
  ddd_benefits:
    ubiquitous_language:
      - "Consistent terminology"
      - "Business-aligned naming"
      - "Clear domain boundaries"
    
    explicit_models:
      - "Rich domain objects"
      - "Clear aggregates"
      - "Explicit value objects"
  
  anti_patterns_to_avoid:
    god_classes:
      problem: "Too much context for LLM"
      solution: "Break into focused classes"
    
    implicit_behavior:
      problem: "Hidden side effects"
      solution: "Make operations explicit"
    
    magic_values:
      problem: "Unclear intent"
      solution: "Named constants or enums"
    
    deep_inheritance:
      problem: "Complex context chains"
      solution: "Composition over inheritance"

architecture_recommendations:
  for_new_projects:
    preferred: "Vertical Slice Architecture"
    reasons:
      - "Minimal cognitive load"
      - "Clear feature boundaries"
      - "Easy to understand scope"
    
    secondary: "Domain-Driven Design"
    reasons:
      - "Rich domain models"
      - "Clear business alignment"
      - "Explicit boundaries"
  
  for_existing_projects:
    identify_seams:
      - "Find natural boundaries"
      - "Group related functionality"
      - "Extract cohesive modules"
    
    incremental_improvement:
      - "Start with high-value areas"
      - "Apply patterns gradually"
      - "Maintain consistency"

generated_documentation_optimization:
  yaml_structure:
    benefits:
      - "Machine parseable"
      - "Clear hierarchy"
      - "Explicit relationships"
    
    guidelines:
      - "Use consistent indentation"
      - "Group related concepts"
      - "Avoid deep nesting"
  
  markdown_formatting:
    - "Clear section headers"
    - "Code examples with language tags"
    - "Bullet points for lists"
    - "Tables for comparisons"
```
<!-- DATA:ai-friendly-patterns:END -->
<!-- SECTION:init:ai-comprehension-optimization:END -->

<!-- SECTION:init:implementation-notes:START -->
## Implementation Notes for AI Agents

<!-- DATA:agent-instructions:START -->
```yaml
for_ai_agents:
  pattern_recognition_priority:
    1_vertical_slices: "Check for feature-based organization first"
    2_ddd: "Look for domain modeling patterns"
    3_traditional: "Fall back to MVC/layered patterns"
  
  code_analysis_phase:
    - scan_all_files: "Use glob patterns from deep_analysis_engine"
    - identify_entry_points: "main.*, index.*, app.*, server.*"
    - trace_dependencies: "Build import graph"
    - detect_patterns: "Match against pattern indicators"
    - confidence_scoring: "Rate pattern match confidence"
    - detect_code_smells: "Use code_smell_detection rules"
  
  question_generation_phase:
    - prioritize_questions: "Most important first"
    - limit_questions: "Max 5-7 per session"
    - use_context: "Reference detected components in questions"
    - natural_language: "Conversational, not robotic"
    - pattern_specific: "Ask about detected patterns"
  
  document_generation_phase:
    - populate_all_fields: "No placeholder text"
    - use_real_paths: "From actual file system"
    - calculate_progress: "From git history or estimates"
    - infer_relationships: "From import statements"
    - generate_descriptions: "Based on code analysis"
    - apply_ai_optimization: "Use ai-friendly patterns"
    - suggest_refactorings: "Based on detected smells"
  
  validation_phase:
    - present_clearly: "Use formatting and structure"
    - highlight_uncertain: "Mark low-confidence items"
    - allow_iteration: "User can regenerate sections"
    - save_preferences: "Learn from user corrections"
    - suggest_evolution_path: "Based on maturity indicators"
```
<!-- DATA:agent-instructions:END -->
<!-- SECTION:init:implementation-notes:END -->