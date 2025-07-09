# AI-Optimized Markdown Format Guide

This guide explains the structured markdown format designed to optimize AI readability and manipulation of documents.

## Core Principles

1. **Structured over Prose**: Use data blocks instead of paragraphs
2. **Explicit over Implicit**: Clear markers and identifiers
3. **Atomic over Monolithic**: Small, addressable chunks
4. **Predictable over Flexible**: Consistent patterns

## Format Components

### 1. Section Markers

Every section has unique start/end markers:

```markdown
<!-- SECTION:command:subsection:START -->
Content here
<!-- SECTION:command:subsection:END -->
```

**Benefits**:
- Precise targeting: "Edit section task:requirements"
- No ambiguity about boundaries
- Easy section replacement

### 2. Data Blocks

Structured data in YAML format:

```markdown
<!-- DATA:config-name:START -->
```yaml
key: value
list:
  - item1
  - item2
nested:
  key: value
```
<!-- DATA:config-name:END -->
```

**Benefits**:
- Easy value extraction
- Type-safe parsing
- Clear structure

### 3. Metadata Headers

Document-level metadata:

```markdown
<!-- META:command:task -->
<!-- META:version:2.0 -->
<!-- META:ai-optimized:true -->
```

### 4. Workflows

Explicit process definitions:

```markdown
<!-- WORKFLOW:process-name:START -->
```yaml
steps:
  - id: step1
    action: "Do something"
    next: step2
  - id: step2
    condition: "If something"
    action: "Do other thing"
```
<!-- WORKFLOW:process-name:END -->
```

### 5. Templates

Reusable content patterns:

```markdown
<!-- TEMPLATE:message-template:START -->
```yaml
message_template: |
  Hello {{name}},
  Your {{item}} is {{status}}.
```
<!-- TEMPLATE:message-template:END -->
```

### 6. References

Cross-referencing system:

```markdown
<!-- REF:other-section -->
See details in [](#other-section)
```

## Usage Examples

### Finding a Specific Configuration

```python
# AI can easily extract
section = find_section("DATA:linting-requirements")
config = parse_yaml(section.content)
formatter = config['tools']['formatter']  # "uv run ruff format"
```

### Updating a Workflow Step

```python
# AI can precisely target
workflow = find_section("WORKFLOW:check-fix-cycle")
steps = parse_yaml(workflow.content)
steps['workflow'][2]['action'] = "New action"
replace_section("WORKFLOW:check-fix-cycle", format_yaml(steps))
```

### Adding a New Rule

```python
# AI can append to specific data blocks
rules = find_section("DATA:forbidden-patterns")
patterns = parse_yaml(rules.content)
patterns['patterns'].append({
    'statement': 'New forbidden pattern',
    'correction': 'Do this instead'
})
replace_section("DATA:forbidden-patterns", format_yaml(patterns))
```

## Best Practices

1. **Use Unique IDs**: Every section should have a unique identifier
2. **Keep Sections Small**: One concept per section
3. **Use YAML for Data**: Structured data should always be in YAML
4. **Avoid Prose in Data**: Keep human text in templates or separate sections
5. **Test Parseability**: Ensure all YAML blocks are valid

## Migration Guide

To convert existing markdown:

1. Identify logical sections → Wrap with SECTION markers
2. Extract configuration → Convert to DATA blocks
3. Find workflows → Convert to WORKFLOW blocks
4. Identify templates → Convert to TEMPLATE blocks
5. Add metadata headers
6. Create cross-references

## Benefits for AI

- **Precise Edits**: No regex confusion or string matching errors
- **Structured Data**: Direct access to configuration values
- **Safe Updates**: Clear boundaries prevent corruption
- **Efficient Processing**: Can jump directly to relevant sections
- **Reliable Parsing**: Consistent format reduces errors

This format transforms markdown from a human-first document format to a hybrid format that serves both humans and AI effectively.