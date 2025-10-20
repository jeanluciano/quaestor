# Document Templates & Generation

This file describes the document generation process, template variables, and skills installation.

## Generated Documents Overview

```yaml
generated_documents:
  AGENT.md:
    location: ".quaestor/AGENT.md"
    source: "src/quaestor/agent.md"
    processing: "Copy template as-is"
    purpose: "AI behavioral rules and workflow enforcement"

  ARCHITECTURE.md:
    location: ".quaestor/ARCHITECTURE.md"
    source: "src/quaestor/architecture.md"
    processing: "Jinja2 template with variable substitution"
    purpose: "Project architecture, patterns, and quality standards"

  CLAUDE.md:
    location: "CLAUDE.md" (project root)
    source: "src/quaestor/include.md"
    processing: "Merge with existing or create new"
    purpose: "Main entry point with Quaestor configuration"
```

## ARCHITECTURE.md Template Variables

ARCHITECTURE.md uses Jinja2 templating with variables populated from detected language config:

### Section 1: Project Configuration

```yaml
template_variables:
  project_name: "[Detected from directory name or git config]"
  project_type: "[Detected from framework: web-api, web-app, library, cli, etc.]"
  language_display_name: "[Human-readable: Python, TypeScript, Rust]"
  primary_language: "[Code: python, typescript, rust]"
  config_system_version: "2.0"
  strict_mode: "[true if complexity > 0.7, else false]"

  build_tool: "[Detected: cargo, npm, pip, gradle]"
  package_manager: "[Detected: cargo, npm/yarn, pip/poetry, maven]"
  language_server: "[Optional: pyright, rust-analyzer, tsserver]"
  virtual_env: "[Optional: venv, conda, nvm]"
  dependency_management: "[Detected from package files]"
```

### Section 3: Code Quality Standards

These variables are populated from `src/quaestor/core/languages.yaml`:

```yaml
quality_standards:
  lint_command: "{{ lint_command }}"           # e.g., "ruff check ."
  format_command: "{{ format_command }}"       # e.g., "ruff format ."
  test_command: "{{ test_command }}"           # e.g., "pytest"
  coverage_command: "{{ coverage_command }}"   # e.g., "pytest --cov"
  type_check_command: "{{ type_check_command }}" # e.g., "mypy ."

  quick_check_command: "{{ quick_check_command }}"
  # e.g., "ruff check . && pytest -x"

  full_check_command: "{{ full_check_command }}"
  # e.g., "ruff check . && ruff format --check . && mypy . && pytest"

  code_formatter: "{{ code_formatter }}"           # e.g., "ruff"
  testing_framework: "{{ testing_framework }}"     # e.g., "pytest"
  coverage_threshold_percent: "{{ coverage_threshold_percent }}" # e.g., ">= 80%"
```

### Section 6: Security & Performance

```yaml
security_performance:
  has_security_scanner: "{{ has_security_scanner }}"    # "true" or "false"
  security_scan_command: "{{ security_scan_command }}"  # e.g., "bandit -r ."
  security_scanner: "{{ security_scanner }}"            # e.g., "bandit"

  has_profiler: "{{ has_profiler }}"                    # "true" or "false"
  profile_command: "{{ profile_command }}"              # e.g., "py-spy top"
  performance_budget: "{{ performance_budget }}"        # e.g., "< 200ms p95"
```

### Section 8: Quality Thresholds

```yaml
quality_thresholds:
  coverage_threshold_percent: "{{ coverage_threshold_percent }}"
  max_duplication: "{{ max_duplication }}"               # e.g., "3%"
  max_debt_hours: "{{ max_debt_hours }}"                 # e.g., "40 hours"
  max_bugs_per_kloc: "{{ max_bugs_per_kloc }}"           # e.g., "0.5"

  current_coverage: "{{ current_coverage }}"             # e.g., "0% (not yet measured)"
  current_duplication: "{{ current_duplication }}"       # e.g., "N/A"
  current_debt: "{{ current_debt }}"                     # e.g., "N/A"
  current_bug_density: "{{ current_bug_density }}"       # e.g., "N/A"
  main_config_available: "{{ main_config_available }}"   # true or false
```

### Section 10: Project Standards

```yaml
project_standards:
  max_build_time: "{{ max_build_time }}"             # e.g., "< 5 minutes"
  max_bundle_size: "{{ max_bundle_size }}"           # e.g., "< 250KB gzipped"
  memory_threshold: "{{ memory_threshold }}"         # e.g., "< 512MB"
  retry_configuration: "{{ retry_configuration }}"   # e.g., "3 retries with exponential backoff"
  fallback_behavior: "{{ fallback_behavior }}"       # e.g., "Fail gracefully with user message"
  rule_enforcement: "{{ rule_enforcement }}"         # e.g., "Enforced on commit (pre-commit hooks)"
  pre_edit_script: "{{ pre_edit_script }}"           # e.g., "ruff check"
  post_edit_script: "{{ post_edit_script }}"         # e.g., "ruff format"
```

## Variable Population Process

### Step 1: Detect Language
Use patterns from @DETECTION.md to identify primary language.

### Step 2: Load Language Config
```python
# Read src/quaestor/core/languages.yaml
# Extract section for detected language
# Example:
config = yaml.load("src/quaestor/core/languages.yaml")
lang_config = config[detected_language]  # e.g., config["python"]
```

### Step 3: Populate Template
```python
# Use Jinja2 to render template
from jinja2 import Template

template = Template(open("src/quaestor/architecture.md").read())
rendered = template.render(**lang_config, **project_metadata)
```

### Step 4: Write Output
```python
# Write to .quaestor/ARCHITECTURE.md
output_path = ".quaestor/ARCHITECTURE.md"
with open(output_path, "w") as f:
    f.write(rendered)
```

## Language-Specific Template Examples

### Python Project
```markdown
## 3. CODE QUALITY STANDARDS

### Linting and Formatting
- **Linter**: `ruff check .`
- **Formatter**: `ruff format .`
- **Code Formatter**: ruff
- **Quick Check**: `ruff check . && pytest -x`
- **Full Validation**: `ruff check . && ruff format --check . && mypy . && pytest`

### Testing Requirements
- **Test Runner**: `pytest`
- **Coverage**: `pytest --cov`
- **Coverage Threshold**: >= 80%
- **Testing Framework**: pytest
```

### TypeScript Project
```markdown
## 3. CODE QUALITY STANDARDS

### Linting and Formatting
- **Linter**: `eslint .`
- **Formatter**: `prettier --write .`
- **Code Formatter**: prettier
- **Quick Check**: `eslint . && npm test`
- **Full Validation**: `eslint . && prettier --check . && tsc --noEmit && npm test`

### Testing Requirements
- **Test Runner**: `npm test`
- **Coverage**: `npm run test:coverage`
- **Coverage Threshold**: >= 80%
- **Testing Framework**: jest
```

### Rust Project
```markdown
## 3. CODE QUALITY STANDARDS

### Linting and Formatting
- **Linter**: `cargo clippy`
- **Formatter**: `cargo fmt`
- **Code Formatter**: rustfmt
- **Quick Check**: `cargo clippy && cargo test`
- **Full Validation**: `cargo clippy && cargo fmt --check && cargo test`

### Testing Requirements
- **Test Runner**: `cargo test`
- **Coverage**: `cargo tarpaulin`
- **Coverage Threshold**: >= 75%
- **Testing Framework**: cargo test
```

## Skills Installation

### Installation Process

```yaml
skills_installation:
  source_directory: "src/quaestor/skills/"
  target_directory: ".claude/skills/"

  steps:
    1. Create target directory: "mkdir -p .claude/skills"
    2. Iterate through source skills
    3. Copy each skill directory to target
    4. Verify SKILL.md exists in each
    5. Report installed skills to user
```

### Skills Installed

```yaml
skills_list:
  - name: architecture-patterns
    purpose: "MVC, DDD, Microservices, Clean Architecture examples"

  - name: code-quality
    purpose: "SOLID principles, linting patterns, code review checklists"

  - name: debugging-workflow
    purpose: "Systematic debugging approaches"

  - name: performance-optimization
    purpose: "Caching strategies, profiling techniques"

  - name: security-audit
    purpose: "OWASP guidelines, authentication patterns"

  - name: testing-strategy
    purpose: "Test pyramid, pytest patterns, coverage guidelines"

  - name: spec-writing
    purpose: "Create specifications from requirements"

  - name: spec-management
    purpose: "Manage specification lifecycle"

  - name: pr-generation
    purpose: "Generate pull requests from completed specs"

  - name: project-initialization
    purpose: "This skill - intelligent project setup"
```

### Installation Code Example

```python
from pathlib import Path
import shutil

def install_skills(project_root: Path):
    """Install all Quaestor skills to project."""
    source_dir = Path("src/quaestor/skills")
    target_dir = project_root / ".claude" / "skills"

    # Create target directory
    target_dir.mkdir(parents=True, exist_ok=True)

    installed = []
    for skill_dir in source_dir.iterdir():
        if skill_dir.is_dir():
            skill_name = skill_dir.name
            skill_file = skill_dir / "SKILL.md"

            if skill_file.exists():
                # Copy skill directory
                target_skill_dir = target_dir / skill_name
                shutil.copytree(skill_dir, target_skill_dir, dirs_exist_ok=True)
                installed.append(skill_name)
                print(f"✓ Installed {skill_name}")

    return installed
```

## CLAUDE.md Merging

### Merge Strategy

```yaml
claude_md_handling:
  if_exists:
    strategy: "Merge Quaestor config with existing content"
    process:
      - Check for existing QUAESTOR CONFIG markers
      - If found: Replace old config with new
      - If not found: Prepend Quaestor config to existing content
    preserve: "All user custom content"

  if_not_exists:
    strategy: "Create new CLAUDE.md from template"
    content: "src/quaestor/include.md"
```

### CLAUDE.md Template

```markdown
<!-- QUAESTOR CONFIG START -->
[!IMPORTANT]
**Claude:** This project uses Quaestor for AI context management.
Please read the following files in order:
@.quaestor/AGENT.md - AI behavioral rules and workflow enforcement
@.quaestor/ARCHITECTURE.md - Project architecture, standards, and quality guidelines
@.quaestor/specs/active/ - Active specifications and implementation details
<!-- QUAESTOR CONFIG END -->

<!-- Your custom content below -->
```

## Customization After Generation

Users can customize the generated ARCHITECTURE.md:

### Common Customizations

```markdown
# Example: Customize test command for specific project needs

# Before (default)
- **Test Runner**: `pytest`

# After (customized for project)
- **Test Runner**: `pytest -xvs --cov=src --cov-report=html`

# Example: Add project-specific linting rules

# Before (default)
- **Linter**: `ruff check .`

# After (customized)
- **Linter**: `ruff check . --select E,F,W,I,N --ignore E501`
```

### Where to Customize

1. Open `.quaestor/ARCHITECTURE.md`
2. Navigate to **Section 3: CODE QUALITY STANDARDS**
3. Edit command values directly
4. Save file - changes take effect immediately

**Important**: Users should edit `.quaestor/ARCHITECTURE.md` directly, not the template files in `src/quaestor/`.

---

*This file provides complete documentation templates and variable mappings for intelligent document generation.*
