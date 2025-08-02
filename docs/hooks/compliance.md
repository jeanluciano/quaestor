# Compliance Hooks

Quaestor provides two compliance hooks that work together to ensure code quality and standards adherence.

## Overview

The compliance system consists of:
- **compliance_pre_edit.py**: Pre-modification validation
- **compliance_validator.py**: Post-modification verification

These hooks enforce project standards, patterns, and best practices automatically.

## Pre-Edit Compliance Hook

### Purpose
Validates planned changes before they're made to prevent non-compliant code from being written.

### Checks Performed
- File naming conventions
- Forbidden patterns detection
- Architecture boundary violations
- Security anti-patterns
- Documentation requirements

### Example Output
```
🔍 Pre-Edit Compliance Check

Analyzing planned changes to: src/api/auth.py

⚠️ Compliance Warnings:
- Missing type hints required by project standards
- Direct database access detected (use repository pattern)
- No test file found for this module

Recommendations:
→ Add type hints to function parameters
→ Use AuthRepository instead of direct DB calls
→ Create tests/api/test_auth.py

Suggested: Use the compliance-enforcer agent for guided fixes
```

## Post-Edit Validation Hook

### Purpose
Verifies that completed changes meet all requirements and haven't introduced new issues.

### Validation Areas

#### Code Quality
- Syntax correctness
- Import organization
- Code complexity metrics
- Duplication detection

#### Standards Compliance
- Style guide adherence
- Naming conventions
- File organization
- Comment requirements

#### Security Checks
- Input validation
- SQL injection prevention
- XSS protection
- Authentication verification

#### Test Coverage
- Unit test existence
- Test completeness
- Edge case coverage
- Integration test needs

### Example Output
```
✅ Post-Edit Validation Complete

File: src/services/user_service.py
- Style: PASS (follows PEP 8)
- Security: PASS (input validation present)
- Tests: PASS (85% coverage)
- Docs: PASS (all public methods documented)

No compliance issues found!
```

## Integration with Development Flow

### Automatic Triggers
1. **Pre-Edit**: Before Write/Edit/MultiEdit operations
2. **Post-Edit**: After file modifications
3. **Commit Time**: During commit preparation
4. **PR Creation**: Before pull request

### With Other Hooks
- Works with spec tracker for requirement validation
- Integrates with memory tracker for decision recording
- Coordinates with workflow tracker for phase-appropriate checks

## Configuration

### Custom Rules
Create project-specific rules in `.quaestor/compliance-rules.yaml`:

```yaml
rules:
  naming:
    functions: snake_case
    classes: PascalCase
    constants: UPPER_SNAKE_CASE
  
  patterns:
    forbidden:
      - pattern: "print\\("
        message: "Use logger instead of print"
      - pattern: "import \\*"
        message: "Avoid wildcard imports"
    
  required:
    - pattern: "def .+\\(.*\\) -> .+:"
      message: "All functions must have return type hints"
```

### Severity Levels
- **ERROR**: Blocks changes
- **WARNING**: Allows with caution
- **INFO**: Suggestions only

## Best Practices

1. Address compliance warnings immediately
2. Don't disable hooks without good reason
3. Update rules as patterns evolve
4. Document exemptions clearly
5. Run compliance checks in CI/CD

## Customization

Extend compliance checks by:
1. Adding rules to configuration
2. Creating custom validators
3. Integrating with linters
4. Adding project-specific patterns
5. Connecting to external tools