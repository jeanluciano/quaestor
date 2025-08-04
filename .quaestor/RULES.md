# CRITICAL RULES - Python CLI Project

## ⚠️ AUTOMATIC ENFORCEMENT CHECKS

```yaml
before_any_action:
  mandatory_checks:
    - id: "quality_standards"
      check: "Are Python quality tools being used?"
      requires:
        - ruff_linting: "Run 'make lint' before commits"
        - pytest_passing: "Run 'make test' for all changes"
        - type_hints: "All functions must have type annotations"
      on_violation: "STOP and run quality checks first"
    
    - id: "manager_pattern_compliance"
      check: "Am I following the service/manager pattern?"
      triggers:
        - adding_business_logic_to_dataclasses
        - creating_god_objects
        - mixing_concerns_in_single_class
      on_violation: "STOP and refactor to use appropriate managers"
    
    - id: "file_operation_safety"
      check: "Are file operations atomic and safe?"
      requires:
        - atomic_writes: "Use safe_write_text from utils"
        - path_validation: "Validate all user-provided paths"
        - backup_on_modify: "Create backups when modifying files"
      on_violation: "Use proper file utilities from utils module"
    
    - id: "specification_system_usage"
      check: "Am I properly using the specification system?"
      required_for:
        - new_features: "Create specification first"
        - major_changes: "Document in specification"
        - work_tracking: "Update spec status and progress"
      on_violation: "STOP and create/update specification"
```

## 🔄 WORKFLOW PATTERN

### Research → Plan → Implement

**ALWAYS follow this pattern for non-trivial tasks:**

1. **RESEARCH FIRST**
   - Required Response: "Let me research the codebase first..."
   - Use grep/read to understand existing patterns
   - Check similar implementations
   - Understand dependencies

2. **PLAN BEFORE IMPLEMENTING**  
   - Required Response: "Based on my research, here's my plan..."
   - Present approach for approval
   - Identify files to modify
   - Consider edge cases

3. **IMPLEMENT WITH QUALITY**
   - Follow the approved plan
   - Use appropriate subagents
   - Test as you go
   - Validate changes

**EXCEPTIONS:**
- Trivial changes (typos, simple fixes)
- Explicit user override
- Emergency debugging

## 🔴 FRAMEWORK-SPECIFIC RULES

```yaml
python_cli_rules:
  - rule_id: "USE_TYPER_PATTERNS"
    priority: "CRITICAL"
    description: "Follow established Typer CLI patterns"
    enforcement:
      examples:
        - use_app_command: "Use @app.command() decorator"
        - rich_output: "Use console from rich for output"
        - progress_bars: "Use rich.progress for long operations"
      validation: "CLI commands must follow existing patterns"
  
  - rule_id: "MANAGER_PATTERN_ONLY"
    priority: "CRITICAL"
    description: "Business logic in managers, not in dataclasses"
    enforcement:
      correct:
        - "SpecificationManager handles all spec logic"
        - "FolderManager handles all folder operations"
        - "Dataclasses are pure data containers"
      incorrect:
        - "Methods on Specification dataclass doing business logic"
        - "Complex operations in __post_init__"
      validation: "Managers orchestrate, dataclasses hold data"
  
  - rule_id: "YAML_FOR_PERSISTENCE"
    priority: "HIGH"
    description: "All data persistence uses YAML format"
    enforcement:
      always_use:
        - "yaml_utils.load_yaml() for reading"
        - "yaml_utils.save_yaml() for writing"
        - "yaml.safe_load() never yaml.load()"
      validation: "Consistent YAML serialization"
  
  - rule_id: "ATOMIC_FILE_OPERATIONS"
    priority: "CRITICAL"
    description: "All file operations must be atomic"
    enforcement:
      required_pattern: |
        # Always use utils for file operations
        from quaestor.utils.file_utils import safe_write_text
        success = safe_write_text(path, content, backup=True)
      never_use:
        - "Direct Path.write_text() without backup"
        - "Open file without proper error handling"
      validation: "File operations use utility functions"
```

## 📋 QUALITY STANDARDS

```yaml
python_quality_gates:
  before_commit:
    linting:
      - command: "make lint"
      - tool: "ruff"
      - must_pass: true
    
    type_checking:
      - all_functions_typed: true
      - use_type_hints: "str, Path, dict[str, Any], etc."
      - avoid_any: "Minimize use of Any type"
    
    testing:
      - command: "make test"
      - framework: "pytest"
      - coverage_target: "80%"
      - test_new_code: "All new features need tests"
  
  code_patterns:
    imports:
      - order: "standard library, third-party, local"
      - style: "from x import y preferred"
      - no_wildcards: "Never use from x import *"
    
    error_handling:
      - pattern: "try-except with specific exceptions"
      - user_feedback: "Use console.print with [red] for errors"
      - logging: "Log errors for debugging"
    
    path_handling:
      - always_use_pathlib: "Path objects, not strings"
      - resolve_paths: "path.resolve() for absolute paths"
      - validate_inputs: "Check paths exist and are accessible"
```

## 🚨 SECURITY REQUIREMENTS

```yaml
security_critical:
  - rule_id: "VALIDATE_SUBPROCESS_INPUTS"
    priority: "CRITICAL"
    description: "Prevent command injection"
    enforcement:
      required: |
        # Validate and sanitize all subprocess inputs
        import shlex
        
        def validate_git_path(path: Path) -> Path:
            safe_path = path.resolve()
            if any(char in str(safe_path) for char in [';', '&', '|', '`', '$']):
                raise ValueError("Invalid characters in path")
            return safe_path
      applies_to: ["git operations", "any subprocess calls"]
  
  - rule_id: "PREVENT_PATH_TRAVERSAL"
    priority: "CRITICAL"
    description: "Validate all file paths"
    enforcement:
      required: |
        # Check for path traversal attempts
        def validate_path(path: str) -> Path:
            p = Path(path).resolve(strict=True)
            
            # Ensure within project boundaries
            if not (p.is_relative_to(Path.cwd()) or p.is_relative_to(Path.home())):
                raise ValueError("Path outside allowed directories")
            
            return p
      validation: "All user-provided paths must be validated"
```

## 🤖 HOOK SYSTEM COMPLIANCE

```yaml
hook_integration:
  - rule_id: "RESPECT_HOOK_DECISIONS"
    priority: "CRITICAL"
    description: "Hooks provide mandatory guidance"
    enforcement:
      when_hook_suggests_agent: "MUST use that agent"
      when_hook_blocks: "MUST resolve before continuing"
      validation: "All hook feedback is mandatory"
  
  - rule_id: "MODE_AWARE_BEHAVIOR"
    priority: "HIGH"
    description: "Respect Framework vs Drive mode"
    enforcement:
      framework_mode: "Hooks actively guide development"
      drive_mode: "User has full control"
      validation: "Check mode before applying rules"
```

## ✅ TESTING REQUIREMENTS

```yaml
pytest_standards:
  test_organization:
    - unit_tests: "tests/unit/ - Test individual functions"
    - integration_tests: "tests/integration/ - Test component interactions"
    - e2e_tests: "tests/e2e/ - Test full workflows"
    - performance_tests: "tests/performance/ - Benchmark critical paths"
  
  test_patterns:
    naming: "test_*.py files, test_* functions"
    structure: |
      def test_specification_creation():
          # Arrange
          manager = SpecificationManager(tmp_path)
          
          # Act
          spec = manager.create_specification(...)
          
          # Assert
          assert spec.status == SpecStatus.DRAFT
    
  fixtures:
    use_provided: "tmp_path, capfd, monkeypatch"
    create_custom: "In conftest.py for reusable setup"
```

## 📁 PROJECT STRUCTURE RULES

```yaml
maintain_structure:
  src_layout:
    quaestor/:
      cli/: "CLI commands only"
      core/: "Business logic and managers"
      utils/: "Shared utilities"
      claude/: "AI integration"
  
  new_features:
    - assess: "Which layer does this belong in?"
    - follow: "Existing patterns in that layer"
    - maintain: "Clear separation of concerns"
  
  imports:
    - relative: "Within same package"
    - absolute: "Cross-package imports"
    - circular: "NEVER create circular imports"
```

## ⛔ ENFORCEMENT

```yaml
violations:
  immediate_stop:
    - "Modifying without running tests"
    - "Direct file writes without atomicity"
    - "Adding business logic to dataclasses"
    - "Ignoring hook recommendations"
  
  correction_required:
    - acknowledge: "I need to follow [RULE]"
    - fix: "Correct the violation"
    - verify: "Run tests and linting"
    - proceed: "Only after compliance"
```

---
**REMEMBER**: These rules ensure code quality, security, and maintainability in the Quaestor Python CLI project. They are tailored to the specific architecture and patterns already established in the codebase.

**CRITICAL REMINDERS**:
- Always run `make lint` and `make test` before considering work complete
- Use managers for logic, dataclasses for data
- All file operations must be atomic with proper error handling
- Hook feedback is mandatory, not optional
- Create specifications for new features and track progress