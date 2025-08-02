# Compliance Enforcer Agent

The Compliance Enforcer ensures all code changes adhere to project standards, patterns, and requirements.

## Purpose

The Compliance Enforcer agent:
- Validates code against project standards
- Ensures architectural patterns are followed
- Checks for security best practices
- Verifies documentation requirements
- Enforces coding conventions

## When to Use

The Compliance Enforcer is automatically triggered:
- Before code modifications (pre-edit hook)
- During specification implementation
- When reviewing pull requests
- Before committing changes

You can also manually invoke it when you need to verify compliance.

## Validation Areas

### Code Standards
- Naming conventions
- File organization
- Import structure
- Comment requirements
- Type annotations

### Architectural Compliance
- Layer separation
- Dependency rules
- Pattern adherence
- Module boundaries
- API contracts

### Security Requirements
- Input validation
- Authentication checks
- Authorization rules
- Sensitive data handling
- Dependency security

### Documentation Standards
- Function/class documentation
- README updates
- API documentation
- Change logs
- Architecture decision records

## Integration with Hooks

The Compliance Enforcer works with:
- `compliance_pre_edit.py`: Pre-modification validation
- `compliance_validator.py`: Post-modification checks
- Specification tracking: Ensures spec compliance
- Memory updates: Validates documentation changes

## Best Practices

1. Run compliance checks early and often
2. Fix violations immediately
3. Update standards documentation when needed
4. Create custom rules for project-specific needs
5. Use automated enforcement in CI/CD