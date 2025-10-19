"""Enhanced template processor for rendering markdown templates with language-specific configurations."""

import re
from pathlib import Path
from typing import Any

from quaestor.core import detect_project_type, get_project_complexity_indicators
from quaestor.core.yaml_config import load_yaml

from .config_manager import get_config_manager
from .config_schemas import LanguageConfig


def _create_template_mappings(
    lang_config: LanguageConfig | None, project_type: str, project_dir: Path
) -> dict[str, Any]:
    """Create comprehensive mappings from language config to template placeholders.

    Args:
        lang_config: Language-specific configuration from config manager
        project_type: Type of project (python, javascript, etc.)
        project_dir: Project directory path

    Returns:
        Dictionary mapping template placeholders to values
    """
    # Get config manager for additional configuration data
    config_manager = get_config_manager(project_dir)
    main_config = config_manager.get_main_config()

    # Extract language config values with safe defaults
    if lang_config:
        lint_cmd = lang_config.lint_command or "# Configure your linter"
        format_cmd = lang_config.format_command or "# Configure your formatter"
        test_cmd = lang_config.test_command or "# Configure your test runner"
        coverage_cmd = lang_config.coverage_command or "# Configure coverage tool"
        type_check_cmd = lang_config.type_check_command or None
        security_cmd = lang_config.security_scan_command or None
        profile_cmd = lang_config.profile_command or None
        coverage_threshold = lang_config.coverage_threshold or 80
        type_checking_enabled = lang_config.type_checking
        performance_target = lang_config.performance_target_ms or 200
        commit_prefix = lang_config.commit_prefix or "feat"
        quick_check_cmd = lang_config.quick_check_command or "make check"
        full_check_cmd = lang_config.full_check_command or "make validate"
        precommit_cmd = lang_config.precommit_install_command or "pre-commit install"
        doc_example = lang_config.doc_style_example or "# Add documentation"
        primary_lang = lang_config.primary_language
    else:
        # Fallback defaults for unknown languages
        lint_cmd = "# Configure your linter"
        format_cmd = "# Configure your formatter"
        test_cmd = "# Configure your test runner"
        coverage_cmd = "# Configure coverage tool"
        type_check_cmd = None
        security_cmd = None
        profile_cmd = None
        coverage_threshold = 80
        type_checking_enabled = False
        performance_target = 200
        commit_prefix = "chore"
        quick_check_cmd = "make check"
        full_check_cmd = "make validate"
        precommit_cmd = "pre-commit install"
        doc_example = "# Add documentation"
        primary_lang = "unknown"

    # Create comprehensive template mappings
    mappings = {
        # Core language information
        "primary_language": primary_lang,
        "project_type": project_type,
        "language_display_name": primary_lang.title() if primary_lang != "unknown" else "Generic",
        # Development commands
        "lint_command": lint_cmd,
        "linter_config": lint_cmd,
        "format_command": format_cmd,
        "test_command": test_cmd,
        "coverage_command": coverage_cmd,
        "type_checker": type_check_cmd or "# Type checking not configured",
        "type_check_command": type_check_cmd or "# Type checking not configured",
        "security_scanner": security_cmd or "# Security scanning not configured",
        "security_scan_command": security_cmd or "# Security scanning not configured",
        "sast_tools": security_cmd or "# Configure static analysis",
        "vulnerability_scanner": security_cmd or "# Configure vulnerability scanning",
        "profile_command": profile_cmd or "# Performance profiling not configured",
        "quick_check_command": quick_check_cmd,
        "full_check_command": full_check_cmd,
        "precommit_install_command": precommit_cmd,
        "pre_commit_hooks": precommit_cmd,
        # Quality thresholds and targets
        "coverage_threshold": coverage_threshold,
        "test_coverage_threshold": coverage_threshold,
        "test_coverage_target": coverage_threshold,
        "coverage_threshold_percent": f"{coverage_threshold}%" if coverage_threshold else "80%",
        "performance_target_ms": performance_target,
        "performance_budget": f"{performance_target}ms" if performance_target else "200ms",
        # Language features
        "type_checking": "true" if type_checking_enabled else "false",
        "type_checking_enabled": type_checking_enabled,
        "has_type_checker": "true" if type_check_cmd else "false",
        "has_security_scanner": "true" if security_cmd else "false",
        "has_profiler": "true" if profile_cmd else "false",
        # Git and workflow
        "commit_prefix": commit_prefix,
        "default_commit_type": commit_prefix,
        # Documentation
        "doc_style_example": doc_example,
        "documentation_style": f"{primary_lang.title()} standard" if primary_lang != "unknown" else "Project standard",
        # Build and deployment defaults (can be overridden by project config)
        "max_build_time": "5min",
        "max_bundle_size": "5MB",
        "memory_threshold": "512MB",
        "max_duplication": "5%",
        "max_debt_hours": "40h",
        "max_bugs_per_kloc": "1",
        # Current project metrics (placeholders for runtime data)
        "current_coverage": "Run 'quaestor status' to see current metrics",
        "current_duplication": "Run 'quaestor status' to see current metrics",
        "current_debt": "Run 'quaestor status' to see current metrics",
        "current_bug_density": "Run 'quaestor status' to see current metrics",
        # CI/CD configuration
        "ci_pipeline_config": _generate_ci_config(primary_lang, project_type),
        "ci_commands": {
            "lint": lint_cmd,
            "test": test_cmd,
            "coverage": coverage_cmd,
            "type_check": type_check_cmd,
            "security": security_cmd,
        },
        # Hook system configuration
        "hook_configuration": _generate_hook_config(main_config),
        "pre_edit_script": lint_cmd,
        "post_edit_script": format_cmd,
        "hook_enforcement_level": "strict" if main_config.hooks.strict_mode else "learning",
        # Automation settings
        "auto_commit_rules": "Atomic commits with descriptive messages",
        "branch_rules": "Feature branches with PR workflow",
        "pr_automation": "Auto-create PRs for completed specifications",
        "specification_automation": "Track progress and auto-update documentation",
        "context_rules": "Maintain .quaestor files for AI context",
        "rule_enforcement": "strict" if main_config.hooks.strict_mode else "learning",
        "template_automation": "Process templates with project data",
        "doc_automation": "Auto-update based on code changes",
        # Error handling and reliability
        "retry_configuration": "3 attempts with exponential backoff",
        "fallback_behavior": "Graceful degradation on failures",
        "error_handling_pattern": _generate_error_handling_pattern(primary_lang),
        "logging_config": "Structured JSON logging",
        "monitoring_setup": "Track execution time and success rate",
        "debug_configuration": "Enable with DEBUG=1 environment variable",
        # Language-specific patterns and conventions
        "naming_convention": _get_naming_convention(primary_lang),
        "file_organization": _get_file_organization(primary_lang),
        "testing_framework": _get_testing_framework(primary_lang, test_cmd),
        "dependency_management": _get_dependency_management(primary_lang),
        "build_tool": _get_build_tool(primary_lang),
        # Advanced features
        "language_server": _get_language_server(primary_lang),
        "package_manager": _get_package_manager(primary_lang),
        "virtual_env": _get_virtual_env_info(primary_lang),
        "code_formatter": _get_code_formatter(primary_lang, format_cmd),
    }

    return mappings


def get_project_data(
    project_dir: Path, language_override: str | None = None, runtime_overrides: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Gather project-specific data for template rendering using the modern configuration system.

    Args:
        project_dir: Path to project directory
        language_override: Optional language type to force instead of auto-detection
        runtime_overrides: Optional runtime configuration overrides

    Returns:
        Dictionary with project data for template processing
    """
    # Get basic project info
    project_type = language_override or detect_project_type(project_dir)
    complexity_info = get_project_complexity_indicators(project_dir, project_type)

    # Use modern configuration system
    try:
        config_manager = get_config_manager(project_dir, language_override)

        # Get language-specific configuration
        lang_config = config_manager.get_language_config(
            language=project_type,
            runtime_overrides=runtime_overrides.get("current_language") if runtime_overrides else None,
        )

        # Get main configuration for additional context
        main_config = config_manager.get_main_config(
            runtime_overrides=runtime_overrides.get("main") if runtime_overrides else None
        )

        # Get effective configuration for debugging/inspection
        effective_config = config_manager.get_effective_config(runtime_overrides)

    except Exception as e:
        # Fallback to legacy system if configuration fails
        print(f"Warning: Configuration system failed, falling back to legacy: {e}")
        config_path = Path(__file__).parent / "languages.yaml"
        language_configs = load_yaml(config_path, {})
        lang_config_dict = language_configs.get(project_type, language_configs.get("unknown", {}))

        # Create a minimal LanguageConfig-like object
        class FallbackConfig:
            def __init__(self, config_dict):
                for key, value in config_dict.items():
                    setattr(self, key, value)

        lang_config = FallbackConfig(lang_config_dict) if lang_config_dict else None
        main_config = None
        effective_config = {}

    # Calculate derived values
    strict_mode = (
        complexity_info.get("total_files", 0) > 50
        or complexity_info.get("max_directory_depth", 0) > 5
        or (main_config and main_config.hooks.strict_mode)
    )

    project_name = project_dir.name

    # Create comprehensive template mappings using the new system
    template_mappings = _create_template_mappings(lang_config, project_type, project_dir)

    # Combine all data with enhanced configuration information
    project_data = {
        # Basic project information
        "project_name": project_name,
        "project_type": project_type,
        "project_path": str(project_dir),
        "strict_mode": strict_mode,
        # Configuration system information
        "config_system_version": "2.0",
        "effective_config": effective_config,
        "main_config_available": main_config is not None,
        "language_config_available": lang_config is not None,
        # Legacy compatibility - include raw language config for backward compatibility
        **(
            lang_config.model_dump()
            if hasattr(lang_config, "model_dump") and lang_config
            else {attr: getattr(lang_config, attr) for attr in dir(lang_config) if not attr.startswith("_")}
            if lang_config
            else {}
        ),
        # Project complexity information
        **complexity_info,
        # Comprehensive template mappings (this is the main enhancement)
        **template_mappings,
    }

    return project_data


def process_template(template_path: Path, project_data: dict[str, Any]) -> str:
    """Process a template file with project data using simple variable substitution.

    Args:
        template_path: Path to template file
        project_data: Project-specific data for substitution

    Returns:
        Processed template content
    """
    content = template_path.read_text(encoding="utf-8")

    # Process simple variable substitutions: {{ variable_name }}
    for key, value in project_data.items():
        if value is None:
            value = ""
        elif isinstance(value, bool):
            value = "true" if value else "false"

        # Replace {{ key }} patterns
        content = re.sub(rf"\{{\{{\s*{re.escape(key)}\s*\}}\}}", str(value), content)

    # Process conditional patterns
    content = _process_conditionals(content, project_data)

    # Clean up any remaining template variables
    content = re.sub(r"\{\{\s*[^}]+\s*\}\}", "", content)

    return content


def _process_conditionals(content: str, data: dict[str, Any]) -> str:
    """Process conditional template patterns including Jinja-style blocks.

    Args:
        content: Template content
        data: Project data

    Returns:
        Content with conditionals processed
    """
    # Process Jinja-style conditional blocks: {% if condition %}...{% endif %}
    content = _process_jinja_conditionals(content, data)

    # Pattern: {{ "text" if condition else "other" }}
    conditional_pattern = r'\{\{\s*"([^"]*?)"\s+if\s+(\w+)\s+else\s+"([^"]*?)"\s*\}\}'

    def replace_conditional(match):
        true_text = match.group(1)
        condition_var = match.group(2)
        false_text = match.group(3)

        condition_value = data.get(condition_var, False)
        if isinstance(condition_value, str):
            condition_value = condition_value.lower() in ("true", "1", "yes", "on")

        return true_text if condition_value else false_text

    content = re.sub(conditional_pattern, replace_conditional, content)

    # Pattern: {{ value if condition else "default" }}
    value_conditional_pattern = r'\{\{\s*(\w+)\s+if\s+(\w+)\s+else\s+"([^"]*?)"\s*\}\}'

    def replace_value_conditional(match):
        value_var = match.group(1)
        condition_var = match.group(2)
        default_text = match.group(3)

        condition_value = data.get(condition_var, False)
        if isinstance(condition_value, str):
            condition_value = condition_value.lower() in ("true", "1", "yes", "on")

        return str(data.get(value_var, "")) if condition_value else default_text

    content = re.sub(value_conditional_pattern, replace_value_conditional, content)

    # Handle specific patterns used in templates
    content = _process_specific_patterns(content, data)

    return content


def _process_jinja_conditionals(content: str, data: dict[str, Any]) -> str:
    """Process Jinja-style conditional blocks: {% if condition %}...{% endif %}

    Args:
        content: Template content
        data: Project data

    Returns:
        Content with Jinja conditionals processed
    """
    # Pattern for {% if condition %}...{% endif %} blocks
    jinja_pattern = r"\{\%\s*if\s+([^%]+)\s*\%\}(.*?)\{\%\s*endif\s*\%\}"

    def replace_jinja_conditional(match):
        condition_expr = match.group(1).strip()
        block_content = match.group(2)

        # Evaluate the condition
        condition_result = _evaluate_condition(condition_expr, data)

        return block_content if condition_result else ""

    # Use DOTALL flag to match across newlines
    content = re.sub(jinja_pattern, replace_jinja_conditional, content, flags=re.DOTALL)

    # Pattern for {% if condition %}...{% else %}...{% endif %} blocks
    jinja_else_pattern = r"\{\%\s*if\s+([^%]+)\s*\%\}(.*?)\{\%\s*else\s*\%\}(.*?)\{\%\s*endif\s*\%\}"

    def replace_jinja_else_conditional(match):
        condition_expr = match.group(1).strip()
        true_content = match.group(2)
        false_content = match.group(3)

        # Evaluate the condition
        condition_result = _evaluate_condition(condition_expr, data)

        return true_content if condition_result else false_content

    content = re.sub(jinja_else_pattern, replace_jinja_else_conditional, content, flags=re.DOTALL)

    return content


def _evaluate_condition(condition_expr: str, data: dict[str, Any]) -> bool:
    """Evaluate a condition expression safely.

    Args:
        condition_expr: The condition expression to evaluate
        data: Project data for variable lookup

    Returns:
        Boolean result of the condition
    """
    # Handle simple variable checks
    if condition_expr in data:
        value = data[condition_expr]
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ("true", "1", "yes", "on")
        if isinstance(value, int | float):
            return value != 0
        return value is not None

    # Handle equality comparisons: variable == "value"
    equality_match = re.match(r'(\w+)\s*==\s*"([^"]*)"', condition_expr)
    if equality_match:
        var_name = equality_match.group(1)
        expected_value = equality_match.group(2)
        actual_value = data.get(var_name, "")
        return str(actual_value) == expected_value

    # Handle inequality comparisons: variable != "value"
    inequality_match = re.match(r'(\w+)\s*!=\s*"([^"]*)"', condition_expr)
    if inequality_match:
        var_name = inequality_match.group(1)
        expected_value = inequality_match.group(2)
        actual_value = data.get(var_name, "")
        return str(actual_value) != expected_value

    # Handle negation: not variable
    negation_match = re.match(r"not\s+(\w+)", condition_expr)
    if negation_match:
        var_name = negation_match.group(1)
        return not _evaluate_condition(var_name, data)

    # Default to false for unknown conditions
    return False


def _process_specific_patterns(content: str, data: dict[str, Any]) -> str:
    """Process specific template patterns found in the codebase.

    Args:
        content: Template content
        data: Project data

    Returns:
        Content with specific patterns processed
    """
    # Handle coverage threshold patterns
    coverage_threshold = data.get("coverage_threshold")
    if coverage_threshold:
        # Pattern: {{ ">=" + coverage_threshold|string + "%" if coverage_threshold else "optional" }}
        content = re.sub(
            r'\{\{\s*">=" \+ coverage_threshold\|string \+ "%"\s+if\s+coverage_threshold\s+else\s+"optional"\s*\}\}',
            f">={coverage_threshold}%",
            content,
        )

        # Pattern: {{ coverage_threshold|string + "%" if coverage_threshold else "80%" }}
        content = re.sub(
            r'\{\{\s*coverage_threshold\|string \+ "%"\s+if\s+coverage_threshold\s+else\s+"80%"\s*\}\}',
            f"{coverage_threshold}%",
            content,
        )
    else:
        content = re.sub(
            r'\{\{\s*">=" \+ coverage_threshold\|string \+ "%"\s+if\s+coverage_threshold\s+else\s+"optional"\s*\}\}',
            "optional",
            content,
        )
        content = re.sub(
            r'\{\{\s*coverage_threshold\|string \+ "%"\s+if\s+coverage_threshold\s+else\s+"80%"\s*\}\}', "80%", content
        )

    # Handle project type specific patterns
    project_type = data.get("project_type", "unknown")

    # Pattern: {{ "true" if project_type == "web" else "false" }}
    is_web = "true" if project_type == "web" else "false"
    content = re.sub(r'\{\{\s*"true"\s+if\s+project_type\s*==\s*"web"\s+else\s+"false"\s*\}\}', is_web, content)

    # Handle performance target patterns
    performance_target = data.get("performance_target_ms", 200)
    content = re.sub(
        r'\{\{\s*performance_target_ms\s+if\s+performance_target_ms\s+else\s+"200"\s*\}\}',
        str(performance_target),
        content,
    )

    return content


def render_template_string(template_str: str, project_data: dict[str, Any]) -> str:
    """Render a template string with project data.

    Args:
        template_str: Template string content
        project_data: Project-specific data

    Returns:
        Rendered string
    """
    # Create a temporary file to use existing process_template function
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as tf:
        tf.write(template_str)
        temp_path = Path(tf.name)

    try:
        result = process_template(temp_path, project_data)
        return result
    finally:
        temp_path.unlink()


def validate_template(template_path: Path) -> tuple[bool, list[str]]:
    """Validate a template for common issues.

    Args:
        template_path: Path to template file

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    if not template_path.exists():
        errors.append(f"Template file does not exist: {template_path}")
        return False, errors

    try:
        content = template_path.read_text(encoding="utf-8")
    except Exception as e:
        errors.append(f"Cannot read template file: {e}")
        return False, errors

    # Check for common template issues

    # Unmatched braces
    open_braces = content.count("{{")
    close_braces = content.count("}}")
    if open_braces != close_braces:
        errors.append(f"Unmatched template braces: {open_braces} opening, {close_braces} closing")

    # Invalid variable names (should be alphanumeric + underscore)
    invalid_vars = re.findall(r'\{\{\s*([^}]*[^a-zA-Z0-9_\s|"\'+-]+[^}]*)\s*\}\}', content)
    for var in invalid_vars:
        if not any(keyword in var for keyword in ["if", "else", "string", "+", '"']):  # Skip conditionals
            errors.append(f"Invalid variable name: {var}")

    return len(errors) == 0, errors


# Helper functions for language-specific configuration generation


def _generate_ci_config(language: str, project_type: str) -> str:
    """Generate CI/CD configuration template for the language."""
    ci_templates = {
        "python": """# Python CI/CD Configuration
name: Python CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v3
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Lint with ruff
        run: ruff check .
      - name: Test with pytest
        run: pytest --cov
""",
        "javascript": """# JavaScript CI/CD Configuration
name: Node.js CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Use Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install dependencies
        run: npm ci
      - name: Lint
        run: npm run lint
      - name: Test
        run: npm test
""",
        "typescript": """# TypeScript CI/CD Configuration
name: TypeScript CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Use Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install dependencies
        run: npm ci
      - name: Type check
        run: npx tsc --noEmit
      - name: Lint
        run: npm run lint
      - name: Test
        run: npm test
""",
        "rust": """# Rust CI/CD Configuration
name: Rust CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install Rust
        uses: actions-rs/toolchain@v1
        with:
          toolchain: stable
      - name: Format check
        run: cargo fmt -- --check
      - name: Clippy
        run: cargo clippy -- -D warnings
      - name: Test
        run: cargo test
""",
        "go": """# Go CI/CD Configuration
name: Go CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Go
        uses: actions/setup-go@v3
        with:
          go-version: '1.21'
      - name: Format check
        run: go fmt ./...
      - name: Vet
        run: go vet ./...
      - name: Test
        run: go test ./...
""",
    }
    return ci_templates.get(language, f"# Configure CI/CD for {project_type} project")


def _generate_hook_config(main_config) -> str:
    """Generate hook configuration based on main config settings."""
    hooks_enabled = main_config.hooks.enabled
    strict_mode = main_config.hooks.strict_mode

    config = {
        "hooks": {
            "enabled": hooks_enabled,
            "strict_mode": strict_mode,
        }
    }

    import json

    return json.dumps(config, indent=2)


def _generate_error_handling_pattern(language: str) -> str:
    """Generate error handling pattern for the language."""
    patterns = {
        "python": """try:
    result = hook.run(input_data)
    return result
except TimeoutError:
    logger.warning("Hook execution timed out, using fallback")
    return fallback_result()
except Exception as e:
    logger.error(f"Hook execution failed: {e}")
    return safe_default()""",
        "javascript": """try {
    const result = await hook.run(inputData);
    return result;
} catch (error) {
    if (error.name === 'TimeoutError') {
        console.warn('Hook execution timed out, using fallback');
        return fallbackResult();
    }
    console.error('Hook execution failed:', error);
    return safeDefault();
}""",
        "typescript": """try {
    const result: HookResult = await hook.run(inputData);
    return result;
} catch (error: unknown) {
    if (error instanceof TimeoutError) {
        console.warn('Hook execution timed out, using fallback');
        return fallbackResult();
    }
    console.error('Hook execution failed:', error);
    return safeDefault();
}""",
        "rust": """match hook.run(input_data) {
    Ok(result) => result,
    Err(HookError::Timeout) => {
        warn!("Hook execution timed out, using fallback");
        fallback_result()
    }
    Err(e) => {
        error!("Hook execution failed: {}", e);
        safe_default()
    }
}""",
        "go": """result, err := hook.Run(inputData)
if err != nil {
    if errors.Is(err, ErrTimeout) {
        log.Warn("Hook execution timed out, using fallback")
        return fallbackResult(), nil
    }
    log.Error("Hook execution failed", "error", err)
    return safeDefault(), nil
}
return result, nil""",
    }
    return patterns.get(
        language,
        """try {
    const result = await hook.run(inputData);
    return result;
} catch (error) {
    console.error('Hook execution failed:', error);
    return safeDefault();
}""",
    )


def _get_naming_convention(language: str) -> str:
    """Get naming convention for the language."""
    conventions = {
        "python": "snake_case for functions/variables, PascalCase for classes",
        "javascript": "camelCase for functions/variables, PascalCase for classes",
        "typescript": "camelCase for functions/variables, PascalCase for classes/interfaces",
        "rust": "snake_case for functions/variables, PascalCase for types/traits",
        "go": "camelCase for unexported, PascalCase for exported",
        "java": "camelCase for methods/variables, PascalCase for classes",
        "ruby": "snake_case for methods/variables, PascalCase for classes",
    }
    return conventions.get(language, "Follow language-specific conventions")


def _get_file_organization(language: str) -> str:
    """Get file organization pattern for the language."""
    organizations = {
        "python": "Package structure with __init__.py, src/ layout recommended",
        "javascript": "CommonJS modules, organize by feature or layer",
        "typescript": "ES modules with barrel exports, organize by feature",
        "rust": "Cargo workspace with crate organization",
        "go": "Package per directory, cmd/ for binaries",
        "java": "Maven/Gradle structure with com.company.project packages",
        "ruby": "Gem structure with lib/ and bin/ directories",
    }
    return organizations.get(language, "Organize files by feature and responsibility")


def _get_testing_framework(language: str, test_command: str) -> str:
    """Get testing framework information for the language."""
    if "pytest" in test_command:
        return "pytest with fixtures and parameterization"
    elif "jest" in test_command or "npm test" in test_command:
        return "Jest for JavaScript/TypeScript testing"
    elif "cargo test" in test_command:
        return "Built-in Rust testing with #[test] attributes"
    elif "go test" in test_command:
        return "Built-in Go testing with *_test.go files"
    elif "rspec" in test_command:
        return "RSpec for behavior-driven testing"
    elif "junit" in test_command or "mvn test" in test_command:
        return "JUnit for Java unit testing"

    frameworks = {
        "python": "pytest recommended",
        "javascript": "Jest or Vitest recommended",
        "typescript": "Jest or Vitest with TypeScript support",
        "rust": "Built-in testing framework",
        "go": "Built-in testing framework",
        "java": "JUnit 5 recommended",
        "ruby": "RSpec recommended",
    }
    return frameworks.get(language, "Configure appropriate testing framework")


def _get_dependency_management(language: str) -> str:
    """Get dependency management approach for the language."""
    managers = {
        "python": "pip with requirements.txt or Poetry/pipenv for advanced needs",
        "javascript": "npm with package.json and package-lock.json",
        "typescript": "npm with package.json, consider pnpm for monorepos",
        "rust": "Cargo with Cargo.toml dependency management",
        "go": "Go modules with go.mod versioning",
        "java": "Maven with pom.xml or Gradle with build.gradle",
        "ruby": "Bundler with Gemfile and Gemfile.lock",
    }
    return managers.get(language, "Use language-standard dependency management")


def _get_build_tool(language: str) -> str:
    """Get build tool information for the language."""
    tools = {
        "python": "setuptools/pip, Poetry, or PDM for packaging",
        "javascript": "npm scripts, Webpack, Vite, or Rollup for bundling",
        "typescript": "tsc compiler with npm scripts or build tools",
        "rust": "Cargo for compilation and packaging",
        "go": "go build with cross-compilation support",
        "java": "Maven or Gradle with lifecycle management",
        "ruby": "Bundler with rake for build tasks",
    }
    return tools.get(language, "Configure appropriate build tooling")


def _get_language_server(language: str) -> str:
    """Get language server information for the language."""
    servers = {
        "python": "Pylsp, Pyright, or Ruff LSP for IDE integration",
        "javascript": "TypeScript LSP or Flow for type checking",
        "typescript": "TypeScript LSP with rich IDE support",
        "rust": "rust-analyzer for comprehensive IDE features",
        "go": "gopls for Go language server support",
        "java": "Eclipse JDT LS or IntelliJ language server",
        "ruby": "Solargraph for Ruby language server",
    }
    return servers.get(language, "Configure language server for IDE support")


def _get_package_manager(language: str) -> str:
    """Get package manager for the language."""
    managers = {
        "python": "pip (PyPI), conda for scientific computing",
        "javascript": "npm (default), yarn, or pnpm",
        "typescript": "npm (default), yarn, or pnpm",
        "rust": "Cargo (crates.io registry)",
        "go": "Go modules (proxy.golang.org)",
        "java": "Maven Central, JCenter",
        "ruby": "RubyGems with Bundler",
    }
    return managers.get(language, "Standard package manager for the language")


def _get_virtual_env_info(language: str) -> str:
    """Get virtual environment information for the language."""
    envs = {
        "python": "venv, virtualenv, conda, or Poetry virtual environments",
        "javascript": "Node.js version managers (nvm, volta)",
        "typescript": "Node.js version managers (nvm, volta)",
        "rust": "Toolchain management with rustup",
        "go": "GOPATH workspace or Go modules",
        "java": "SDKMAN or jenv for JDK version management",
        "ruby": "rbenv or RVM for Ruby version management",
    }
    return envs.get(language, "Version management appropriate for the language")


def _get_code_formatter(language: str, format_command: str) -> str:
    """Get code formatter information for the language."""
    if "ruff format" in format_command:
        return "Ruff for fast Python formatting"
    elif "prettier" in format_command:
        return "Prettier for JavaScript/TypeScript formatting"
    elif "cargo fmt" in format_command:
        return "rustfmt for consistent Rust formatting"
    elif "go fmt" in format_command:
        return "gofmt for Go code formatting"
    elif "rubocop" in format_command:
        return "RuboCop for Ruby code formatting"

    formatters = {
        "python": "Black, Ruff, or autopep8 for code formatting",
        "javascript": "Prettier or ESLint --fix for formatting",
        "typescript": "Prettier with TypeScript support",
        "rust": "rustfmt for standard formatting",
        "go": "gofmt and goimports for formatting",
        "java": "google-java-format or Eclipse formatter",
        "ruby": "RuboCop for code formatting",
    }
    return formatters.get(language, "Configure appropriate code formatter")
