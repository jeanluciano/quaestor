# Refactorer Agent

The Refactorer agent specializes in improving code quality through systematic refactoring while maintaining functionality.

## Purpose

The Refactorer agent helps with:
- Improving code readability and maintainability
- Eliminating code duplication
- Applying design patterns
- Modernizing legacy code
- Optimizing performance through structural changes

## When to Use

Use the Refactorer agent when:
- Code is difficult to understand or maintain
- You identify repeated patterns or duplication
- Performance improvements are needed
- Code needs to follow new standards or patterns
- Technical debt needs to be addressed

## Example Usage

```
Use the refactorer agent to extract common validation logic into a reusable function
```

## Capabilities

- **Code Analysis**: Identifies refactoring opportunities
- **Pattern Application**: Implements design patterns
- **DRY Principle**: Eliminates duplication
- **Performance Optimization**: Improves efficiency
- **Test Preservation**: Ensures tests continue passing

## Refactoring Techniques

- Extract Method/Function
- Extract Variable
- Inline Method/Variable
- Move Method/Field
- Extract Interface/Class
- Replace Conditional with Polymorphism
- Introduce Parameter Object
- Replace Magic Numbers with Constants

## Best Practices

1. Always ensure tests pass before and after refactoring
2. Make one type of change at a time
3. Commit frequently with clear messages
4. Document why refactoring is needed
5. Consider performance implications
6. Maintain backwards compatibility when needed