---
allowed-tools: all
description: Synthesize a complete prompt by combining next.md with your arguments
---

<!-- META:command:compose -->
<!-- META:version:2.0 -->
<!-- META:ai-optimized:true -->

<!-- SECTION:compose:header:START -->
## 🎯 PROMPT COMPOSER
<!-- SECTION:compose:header:END -->

<!-- SECTION:compose:overview:START -->
<!-- DATA:composition-task:START -->
```yaml
task:
  description: "Compose a complete, ready-to-execute prompt"
  inputs:
    template: "Auto-detected task command from .quaestor/commands/"
    arguments: "$ARGUMENTS"
  output: "standalone_prompt"
  
auto_detection:
  priority:
    1: "Check MANIFEST.yaml metadata.language"
    2: "Check for Python files (*.py, requirements.txt, pyproject.toml)"
    3: "Check for Rust files (*.rs, Cargo.toml)"
    4: "Default to task-py.md if unclear"
  
  mapping:
    python: "task-py.md"
    rust: "task-rs.md"
    default: "task-py.md"
```
<!-- DATA:composition-task:END -->
<!-- SECTION:compose:overview:END -->

<!-- SECTION:compose:task-steps:START -->
### 📋 COMPOSITION WORKFLOW:

<!-- WORKFLOW:composition-steps:START -->
```yaml
workflow:
  - step: "detect_language"
    action: "Auto-detect project language"
    sources:
      - "MANIFEST.yaml → metadata.language"
      - "File extensions in project"
      - "Package manager files"
    
  - step: "load_template"
    action: "Load appropriate task-{lang}.md from commands directory"
    fallback: "task-py.md if detection unclear"
    
  - step: "parse_structure"
    action: "Extract workflow and requirements"
    
  - step: "inject_arguments"
    action: "Replace $ARGUMENTS with user input"
    context: "preserve_workflow_integrity"
    
  - step: "render_output"
    action: "Generate markdown code block"
    format: "copy_paste_ready"
```
<!-- WORKFLOW:composition-steps:END -->
<!-- SECTION:compose:task-steps:END -->

<!-- SECTION:compose:output-format:START -->
### 🎨 OUTPUT SPECIFICATION:

<!-- TEMPLATE:output-format:START -->
```yaml
output_spec:
  format: "markdown_code_block"
  structure: |
    ```
    [Composed prompt with integrated arguments]
    
    - Complete task.md structure preserved
    - $ARGUMENTS naturally embedded
    - Ready for immediate execution
    ```
```
<!-- TEMPLATE:output-format:END -->
<!-- SECTION:compose:output-format:END -->

<!-- SECTION:compose:rules:START -->
### 📏 COMPOSITION RULES:

<!-- DATA:composition-rules:START -->
```yaml
composition_rules:
  preserve_structure:
    requirement: "Maintain workflow integrity from task.md"
    includes: ["checkpoints", "requirements", "validation"]
    
  argument_injection:
    method: "seamless_replacement"
    target: "$ARGUMENTS placeholder"
    
  context_enhancement:
    when: "technology_specific"
    action: "emphasize_relevant_sections"
    
  output_requirements:
    standalone: true
    executable: true
    no_meta_commentary: true
```
<!-- DATA:composition-rules:END -->
<!-- SECTION:compose:rules:END -->

<!-- SECTION:compose:enhancement-guidelines:START -->
### 🔧 ADAPTIVE ENHANCEMENTS:

<!-- DATA:enhancement-logic:START -->
```yaml
enhancements:
  complex_task_detection:
    indicators: ["architecture", "multiple_components", "refactor"]
    emphasize: ["ultrathink", "agent_delegation"]
    
  refactoring_mode:
    trigger: "refactor in arguments"
    highlight: "code_replacement_rules"
    
  universal_requirements:
    always_include: ["linting", "testing", "validation"]
    non_negotiable: true
```
<!-- DATA:enhancement-logic:END -->
<!-- SECTION:compose:enhancement-guidelines:END -->

<!-- SECTION:compose:detection-logic:START -->
### 🔍 LANGUAGE DETECTION LOGIC:

<!-- DATA:detection-implementation:START -->
```yaml
detection_sequence:
  1_check_manifest:
    path: ".quaestor/MANIFEST.yaml"
    field: "metadata.language"
    maps_to:
      "Python": "task-py.md"
      "Rust": "task-rs.md"
      "python": "task-py.md"
      "rust": "task-rs.md"
  
  2_check_files:
    python_indicators:
      - "*.py files exist"
      - "pyproject.toml exists"
      - "requirements.txt exists"
      - "setup.py exists"
    rust_indicators:
      - "*.rs files exist"
      - "Cargo.toml exists"
      - "Cargo.lock exists"
  
  3_default_fallback:
    when: "No clear language detected"
    use: "task-py.md"
    reason: "Python is most common"
```
<!-- DATA:detection-implementation:END -->
<!-- SECTION:compose:detection-logic:END -->

<!-- SECTION:compose:example:START -->
### 📦 EXAMPLE COMPOSITION:

<!-- DATA:example-scenario:START -->
```yaml
example:
  input: "implement REST API for user management with JWT auth"
  
  detection_result: "Python project detected via MANIFEST.yaml"
  
  composition_flow:
    detect: "Found Python in metadata.language"
    load: "task-py.md template"
    inject: "REST API implementation requirements"
    enhance: ["API patterns", "security focus", "auth testing"]
    output: "complete executable prompt with Python-specific standards"
```
<!-- DATA:example-scenario:END -->
<!-- SECTION:compose:example:END -->

<!-- SECTION:compose:start-command:START -->
**COMPOSE NOW** - Auto-detect language and generate the executable prompt!
<!-- SECTION:compose:start-command:END -->